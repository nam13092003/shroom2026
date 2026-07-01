import torch
import numpy as np
from typing import Dict, List, Any, Optional

try:
    import pytorch_lightning as pl
except ImportError:
    try:
        import lightning.pytorch as pl
    except ImportError:
        # Fallback dummy class for local environment where lightning is not yet installed
        class DummyPLModule:
            def __init__(self, *args, **kwargs): pass
        pl = object
        pl.LightningModule = DummyPLModule

from models.multitask_model import MultiTaskModel
from losses.multitask_losses import WeightedMultiTaskLoss
from evaluation.metrics import compute_char_iou, compute_ece, compute_classification_metrics
from datasets.alignment import reconstruct_spans

class ShroomVisionsModule(pl.LightningModule):
    """
    PyTorch Lightning Module for SHROOM-Vision 2026 Multitask model.
    """
    def __init__(self, config: Dict[str, Any]):
        super().__init__()
        self.save_hyperparameters(config)
        self.config = config
        
        # Instantiate model
        self.model = MultiTaskModel(
            d_hidden=config.get('d_hidden', 3584),
            d_vision=config.get('d_vision', 1280),
            d_grounding=config.get('d_grounding', 16),
            encoder_dim=config.get('encoder_dim', 512),
            num_encoder_layers=config.get('num_encoder_layers', 1),
            use_calibration_network=config.get('use_calibration_network', True)
        )
        
        # Instantiate loss
        self.loss_module = WeightedMultiTaskLoss(
            w_seq_risk=config.get('w_seq_risk', 1.0),
            w_token_risk=config.get('w_token_risk', 1.0),
            w_bio_span=config.get('w_bio_span', 1.0),
            w_category=config.get('w_category', 1.0),
            w_calib=config.get('w_calib', 1.0),
            ignore_index=-100
        )
        
        # Validation outputs storage
        self.validation_step_outputs = []

    def forward(self, batch: Dict[str, Any]) -> Dict[str, torch.Tensor]:
        return self.model(batch)

    def training_step(self, batch: Dict[str, Any], batch_idx: int) -> torch.Tensor:
        predictions = self(batch)
        losses = self.loss_module(predictions, batch)
        
        # Log training losses
        self.log('train_loss', losses['loss'], on_step=True, on_epoch=True, prog_bar=True, logger=True)
        self.log('train_seq_risk_loss', losses['l_seq_risk'], on_epoch=True, logger=True)
        self.log('train_token_risk_loss', losses['l_token_risk'], on_epoch=True, logger=True)
        self.log('train_bio_span_loss', losses['l_bio_span'], on_epoch=True, logger=True)
        self.log('train_category_loss', losses['l_category'], on_epoch=True, logger=True)
        self.log('train_calib_loss', losses['l_calib'], on_epoch=True, logger=True)
        
        return losses['loss']

    def validation_step(self, batch: Dict[str, Any], batch_idx: int) -> Dict[str, Any]:
        predictions = self(batch)
        losses = self.loss_module(predictions, batch)
        
        # Extract predictions for metric calculation
        bio_preds = torch.argmax(predictions['bio_logits'], dim=-1).cpu().numpy()
        bio_targets = batch['bio_tags'].cpu().numpy()
        
        calib_probs = predictions['calibrated_probabilities'].squeeze(-1).cpu().numpy()
        gold_probs = batch['probabilities'].cpu().numpy()
        
        # Map token-level predictions back to character-level metrics
        batch_char_ious = []
        batch_eces = []
        
        for i in range(len(batch['ids'])):
            text = batch['responses'][i]
            offsets = batch['offsets'][i]
            
            # 1. Reconstruct predicted character spans from predicted BIO tags
            pred_bio_tags = [["O", "B", "I"][tag] for tag in bio_preds[i][:len(offsets)]]
            pred_spans = reconstruct_spans(pred_bio_tags, offsets)
            
            # Reconstruct gold character spans from target BIO tags
            gold_bio_tags = [["O", "B", "I"][tag] if tag != -100 else "O" for tag in bio_targets[i][:len(offsets)]]
            gold_spans = reconstruct_spans(gold_bio_tags, offsets)
            
            # Compute character-level IoU
            char_iou = compute_char_iou(gold_spans, pred_spans, len(text))
            batch_char_ious.append(char_iou)
            
            # 2. Compute calibration metric (ECE) at character level
            # Map predicted token probabilities to characters
            char_pred_probs = np.zeros(len(text))
            char_gold_probs = np.zeros(len(text))
            
            for t_idx, (start, end) in enumerate(offsets):
                if start == 0 and end == 0:
                    continue
                prob_val = calib_probs[i, t_idx]
                gold_val = gold_probs[i, t_idx]
                char_pred_probs[start:end] = prob_val
                char_gold_probs[start:end] = gold_val
                
            char_ece = compute_ece(char_pred_probs, char_gold_probs)
            batch_eces.append(char_ece)
            
        output = {
            'val_loss': losses['loss'].item(),
            'l_seq_risk': losses['l_seq_risk'],
            'l_bio_span': losses['l_bio_span'],
            'l_category': losses['l_category'],
            'l_calib': losses['l_calib'],
            'char_ious': batch_char_ious,
            'char_eces': batch_eces
        }
        self.validation_step_outputs.append(output)
        return output

    def on_validation_epoch_end(self):
        # Aggregate validation metrics
        avg_loss = np.mean([x['val_loss'] for x in self.validation_step_outputs])
        avg_seq_risk = np.mean([x['l_seq_risk'] for x in self.validation_step_outputs])
        avg_bio_span = np.mean([x['l_bio_span'] for x in self.validation_step_outputs])
        avg_category = np.mean([x['l_category'] for x in self.validation_step_outputs])
        avg_calib = np.mean([x['l_calib'] for x in self.validation_step_outputs])
        
        # Flatten lists of ious and eces
        all_ious = []
        all_eces = []
        for x in self.validation_step_outputs:
            all_ious.extend(x['char_ious'])
            all_eces.extend(x['char_eces'])
            
        mean_iou = np.mean(all_ious)
        mean_ece = np.mean(all_eces)
        
        # Log aggregated validation metrics
        self.log('val_loss', avg_loss, on_epoch=True, prog_bar=True, logger=True)
        self.log('val_seq_risk_loss', avg_seq_risk, on_epoch=True, logger=True)
        self.log('val_bio_span_loss', avg_bio_span, on_epoch=True, logger=True)
        self.log('val_category_loss', avg_category, on_epoch=True, logger=True)
        self.log('val_calib_loss', avg_calib, on_epoch=True, logger=True)
        
        self.log('val_char_iou', mean_iou, on_epoch=True, prog_bar=True, logger=True)
        self.log('val_char_ece', mean_ece, on_epoch=True, prog_bar=True, logger=True)
        
        # Clear outputs cache
        self.validation_step_outputs.clear()

    def configure_optimizers(self) -> Dict[str, Any]:
        optimizer = torch.optim.AdamW(
            self.model.parameters(),
            lr=self.config.get('learning_rate', 1e-4),
            weight_decay=self.config.get('weight_decay', 1e-2)
        )
        
        # Cosine Annealing Learning Rate Scheduler
        scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(
            optimizer,
            T_max=self.config.get('max_epochs', 10),
            eta_min=1e-6
        )
        
        return {
            "optimizer": optimizer,
            "lr_scheduler": {
                "scheduler": scheduler,
                "monitor": "val_loss"
            }
        }
