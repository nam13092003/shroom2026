import torch
import torch.nn as nn
import torch.nn.functional as F

class FocalLoss(nn.Module):
    """
    Multi-class Focal Loss to handle class imbalance.
    FL(p_t) = -alpha * (1 - p_t)^gamma * log(p_t)
    """
    def __init__(self, alpha: float = 1.0, gamma: float = 2.0, ignore_index: int = -100):
        super().__init__()
        self.alpha = alpha
        self.gamma = gamma
        self.ignore_index = ignore_index

    def forward(self, logits: torch.Tensor, targets: torch.Tensor) -> torch.Tensor:
        """
        Args:
            logits: [N, C] where C is number of classes
            targets: [N] with values in 0 to C-1
        """
        # Create mask to ignore specified indices
        mask = (targets != self.ignore_index)
        if not mask.any():
            return torch.tensor(0.0, device=logits.device)
            
        logits = logits[mask]
        targets = targets[mask]
        
        log_p = F.log_softmax(logits, dim=-1)
        p = torch.exp(log_p)
        
        # Gather log_p and p for target classes
        target_log_p = log_p.gather(dim=-1, index=targets.unsqueeze(-1)).squeeze(-1)
        target_p = p.gather(dim=-1, index=targets.unsqueeze(-1)).squeeze(-1)
        
        loss = -self.alpha * ((1.0 - target_p) ** self.gamma) * target_log_p
        return loss.mean()

class DiceLoss(nn.Module):
    """
    Dice Loss for sequence labeling, measuring overlap of target classes.
    """
    def __init__(self, ignore_index: int = -100, smooth: float = 1e-5):
        super().__init__()
        self.ignore_index = ignore_index
        self.smooth = smooth

    def forward(self, logits: torch.Tensor, targets: torch.Tensor) -> torch.Tensor:
        """
        Args:
            logits: [N, C] where C is classes (e.g. 3 for BIO)
            targets: [N]
        """
        mask = (targets != self.ignore_index)
        if not mask.any():
            return torch.tensor(0.0, device=logits.device)
            
        logits = logits[mask]
        targets = targets[mask]
        
        probs = F.softmax(logits, dim=-1)
        num_classes = logits.size(-1)
        
        # Convert targets to one-hot encoding
        targets_one_hot = F.one_hot(targets, num_classes=num_classes).float()
        
        dice_loss = 0.0
        # Calculate dice per class and average (excluding the background class if desired, but we average all here)
        for c in range(num_classes):
            p_c = probs[:, c]
            t_c = targets_one_hot[:, c]
            
            intersection = (p_c * t_c).sum()
            union = (p_c * p_c).sum() + (t_c * t_c).sum()
            
            class_dice = 1.0 - (2.0 * intersection + self.smooth) / (union + self.smooth)
            dice_loss += class_dice
            
        return dice_loss / num_classes

class SpanLoss(nn.Module):
    """
    Combined Focal and Dice loss for BIO span classification.
    """
    def __init__(self, alpha: float = 1.0, gamma: float = 2.0, w_focal: float = 1.0, w_dice: float = 1.0, ignore_index: int = -100):
        super().__init__()
        self.focal_loss = FocalLoss(alpha=alpha, gamma=gamma, ignore_index=ignore_index)
        self.dice_loss = DiceLoss(ignore_index=ignore_index)
        self.w_focal = w_focal
        self.w_dice = w_dice

    def forward(self, logits: torch.Tensor, targets: torch.Tensor) -> torch.Tensor:
        l_focal = self.focal_loss(logits, targets)
        l_dice = self.dice_loss(logits, targets)
        return self.w_focal * l_focal + self.w_dice * l_dice

class CalibrationLoss(nn.Module):
    """
    Calibration Loss minimizing Brier Score (MSE) on predicted probabilities vs empirical targets.
    """
    def __init__(self, ignore_index: float = -100.0):
        super().__init__()
        self.ignore_index = ignore_index

    def forward(self, probs: torch.Tensor, targets: torch.Tensor) -> torch.Tensor:
        """
        Args:
            probs: [N, 1] or [N] containing predicted probabilities (0 to 1)
            targets: [N, 1] or [N] containing empirical probabilities (0 to 1)
        """
        mask = (targets != self.ignore_index)
        if not mask.any():
            return torch.tensor(0.0, device=probs.device)
            
        p = probs[mask]
        t = targets[mask]
        
        # Brier Score (Mean Squared Error)
        loss = F.mse_loss(p, t)
        return loss

class WeightedMultiTaskLoss(nn.Module):
    """
    Weighted combination of all multitask losses.
    """
    def __init__(
        self,
        w_seq_risk: float = 1.0,
        w_token_risk: float = 1.0,
        w_bio_span: float = 1.0,
        w_category: float = 1.0,
        w_calib: float = 1.0,
        ignore_index: int = -100
    ):
        super().__init__()
        self.w_seq_risk = w_seq_risk
        self.w_token_risk = w_token_risk
        self.w_bio_span = w_bio_span
        self.w_category = w_category
        self.w_calib = w_calib
        
        self.seq_risk_loss = nn.BCEWithLogitsLoss()
        self.token_risk_loss = nn.BCEWithLogitsLoss(reduction='mean')
        self.bio_span_loss = SpanLoss(ignore_index=ignore_index)
        self.category_loss = FocalLoss(ignore_index=ignore_index)
        self.calib_loss = CalibrationLoss(ignore_index=float(ignore_index))

    def forward(
        self,
        predictions: dict,
        batch: dict
    ) -> dict:
        """
        Calculate total weighted multitask loss.
        """
        device = predictions['bio_logits'].device
        
        # 1. Sequence Risk Loss
        seq_targets = batch['seq_labels'].unsqueeze(-1) # [batch, 1]
        l_seq_risk = self.seq_risk_loss(predictions['seq_risk_logits'], seq_targets)
        
        # 2. Token Risk Loss (BCE)
        token_risk_logits = predictions['token_risk_logits'].squeeze(-1) # [batch, seq_len]
        token_risk_targets = (batch['bio_tags'] > 0).float() # 1 if B or I, 0 if O
        # mask out padding
        mask = (batch['bio_tags'] != -100)
        if mask.any():
            l_token_risk = F.binary_cross_entropy_with_logits(
                token_risk_logits[mask], token_risk_targets[mask]
            )
        else:
            l_token_risk = torch.tensor(0.0, device=device)
            
        # 3. BIO Span Loss (SpanLoss)
        bio_logits_flat = predictions['bio_logits'].view(-1, 3)
        bio_targets_flat = batch['bio_tags'].view(-1)
        l_bio_span = self.bio_span_loss(bio_logits_flat, bio_targets_flat)
        
        # 4. Category Loss
        # Mask so we compute category loss ONLY for hallucinated tokens (i.e. bio_tag = 1 or 2)
        # Non-hallucinated tokens have target category -100 (which is automatically ignored by FocalLoss)
        cat_logits_flat = predictions['category_logits'].view(-1, 5)
        cat_targets_flat = batch['categories'].view(-1)
        l_category = self.category_loss(cat_logits_flat, cat_targets_flat)
        
        # 5. Calibration Loss
        calib_probs_flat = predictions['calibrated_probabilities'].view(-1)
        calib_targets_flat = batch['probabilities'].view(-1)
        l_calib = self.calib_loss(calib_probs_flat, calib_targets_flat)
        
        # Weighted sum
        total_loss = (
            self.w_seq_risk * l_seq_risk +
            self.w_token_risk * l_token_risk +
            self.w_bio_span * l_bio_span +
            self.w_category * l_category +
            self.w_calib * l_calib
        )
        
        return {
            'loss': total_loss,
            'l_seq_risk': l_seq_risk.item(),
            'l_token_risk': l_token_risk.item(),
            'l_bio_span': l_bio_span.item(),
            'l_category': l_category.item(),
            'l_calib': l_calib.item()
        }
