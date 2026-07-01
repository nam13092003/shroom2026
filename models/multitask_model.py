import torch
import torch.nn as nn
from typing import Dict, List, Any, Optional, Tuple

from models.heads import RiskHead, BIOSpanHead, CategoryHead, CalibrationHead
from models.grounding import GroundingInterface, DummyGrounding

class MultiTaskModel(nn.Module):
    """
    Multitask model for SHROOM-Vision 2026.
    Fuses decoder hidden states, attended vision features, global query context, and grounding features.
    Processes them through a Shared Feature Encoder (Transformer Layer), and feeds them to four heads:
    1. Risk Head (binary classification)
    2. BIO Span Head (sequence labeling)
    3. Category Head (5-class categorization)
    4. Calibration Head (confidence calibration)
    """
    def __init__(
        self,
        d_hidden: int = 3584,      # Qwen2.5-VL-7B hidden size
        d_vision: int = 1280,      # Qwen2.5-VL-7B vision size
        d_grounding: int = 16,     # Dimension of grounding module output
        encoder_dim: int = 512,    # Projected shared dimension
        num_encoder_layers: int = 1,
        use_calibration_network: bool = True,
        grounding_module: Optional[GroundingInterface] = None
    ):
        super().__init__()
        self.d_hidden = d_hidden
        self.d_vision = d_vision
        self.d_grounding = d_grounding
        self.encoder_dim = encoder_dim
        
        # Grounding module
        if grounding_module is not None:
            self.grounding_module = grounding_module
            assert grounding_module.feature_dim == d_grounding
        else:
            self.grounding_module = DummyGrounding(feature_dim=d_grounding)
            
        # Fusion projection layer
        # Combined size: decoder hidden + attended vision + query hidden + grounding features
        input_dim = d_hidden + d_vision + d_hidden + d_grounding
        self.input_projection = nn.Sequential(
            nn.Linear(input_dim, encoder_dim),
            nn.GELU(),
            nn.LayerNorm(encoder_dim)
        )
        
        # Shared Feature Encoder (Transformer Encoder Layer)
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=encoder_dim,
            nhead=8,
            dim_feedforward=encoder_dim * 4,
            dropout=0.1,
            activation='gelu',
            batch_first=True
        )
        self.shared_encoder = nn.TransformerEncoder(encoder_layer, num_layers=num_encoder_layers)
        
        # Prediction Heads
        self.risk_head = RiskHead(feature_dim=encoder_dim)
        self.bio_head = BIOSpanHead(feature_dim=encoder_dim)
        self.category_head = CategoryHead(feature_dim=encoder_dim)
        self.calibration_head = CalibrationHead(use_calibration_network=use_calibration_network)

    def forward(
        self,
        batch: Dict[str, Any],
        images: Optional[List[Any]] = None
    ) -> Dict[str, torch.Tensor]:
        """
        Forward pass.
        
        Args:
            batch: Dictionary from Collator containing:
                - decoder_hidden_states: [batch, seq_len, d_hidden]
                - vision_features: [batch, num_patches, d_vision]
                - query_hidden_states: [batch, d_hidden]
                - cross_attention: [batch, seq_len, num_patches]
                - attention_mask: [batch, seq_len]
                - grounding_features (optional): [batch, seq_len, d_grounding]
            images: Optional raw images list for the grounding module.
            
        Returns:
            Dict containing output logits and probabilities from all heads.
        """
        decoder_states = batch['decoder_hidden_states'] # [batch, seq_len, d_hidden]
        vision_features = batch['vision_features']     # [batch, num_patches, d_vision]
        query_states = batch['query_hidden_states']     # [batch, d_hidden]
        cross_attention = batch['cross_attention']     # [batch, seq_len, num_patches]
        attention_mask = batch['attention_mask']       # [batch, seq_len]
        
        batch_size, seq_len, _ = decoder_states.shape
        device = decoder_states.device
        
        # 1. Compute attended visual features: v_t = sum_v a_tv u_v
        # Batch Matrix Multiplication: [B, seq_len, num_patches] x [B, num_patches, d_vision] -> [B, seq_len, d_vision]
        v_attended = torch.bmm(cross_attention, vision_features)
        
        # 2. Broadcast query features along sequence dimension
        # query_states is [B, d_hidden] -> [B, seq_len, d_hidden]
        query_states_expanded = query_states.unsqueeze(1).expand(-1, seq_len, -1)
        
        # 3. Extract grounding features
        if 'grounding_features' in batch:
            grounding_features = batch['grounding_features']
        elif images is not None and 'offsets' in batch and 'responses' in batch:
            grounding_features = self.grounding_module(
                images, batch['responses'], batch['offsets'], seq_len, device
            )
        else:
            # Fallback to Dummy/Zeros
            grounding_features = self.grounding_module(
                [], [""] * batch_size, [[]] * batch_size, seq_len, device
            )
            
        # 4. Concatenate all features
        # Shape: [batch, seq_len, input_dim]
        fused_features = torch.cat(
            [decoder_states, v_attended, query_states_expanded, grounding_features],
            dim=-1
        )
        
        # 5. Project and encode through Shared Encoder
        projected = self.input_projection(fused_features)
        
        # Transformer attention mask (True means masked out in PyTorch Transformer API)
        src_key_padding_mask = (attention_mask == 0)
        
        # Pass through sequence context encoder
        encoded = self.shared_encoder(projected, src_key_padding_mask=src_key_padding_mask)
        
        # 6. Global sequence representation (mean pooling over non-padded tokens)
        mask_expanded = attention_mask.unsqueeze(-1).float() # [batch, seq_len, 1]
        seq_features = (encoded * mask_expanded).sum(dim=1) / (mask_expanded.sum(dim=1) + 1e-8)
        
        # 7. Feed to heads
        seq_risk_logits, token_risk_logits = self.risk_head(encoded, seq_features)
        bio_logits = self.bio_head(encoded)
        category_logits = self.category_head(encoded)
        
        # 8. Confidence Calibration Head
        calibrated_probs = self.calibration_head(bio_logits, token_risk_logits)
        
        return {
            'seq_risk_logits': seq_risk_logits,         # [batch, 1]
            'token_risk_logits': token_risk_logits,     # [batch, seq_len, 1]
            'bio_logits': bio_logits,                   # [batch, seq_len, 3]
            'category_logits': category_logits,         # [batch, seq_len, 5]
            'calibrated_probabilities': calibrated_probs # [batch, seq_len, 1]
        }
