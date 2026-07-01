import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Tuple

class RiskHead(nn.Module):
    """
    Head 1: Predicts binary hallucination risk at both the sequence and token levels.
    """
    def __init__(self, feature_dim: int):
        super().__init__()
        self.seq_risk = nn.Sequential(
            nn.Linear(feature_dim, 256),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(256, 1)
        )
        self.token_risk = nn.Sequential(
            nn.Linear(feature_dim, 256),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(256, 1)
        )

    def forward(self, token_features: torch.Tensor, seq_features: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Args:
            token_features: [batch, seq_len, feature_dim]
            seq_features: [batch, feature_dim] (aggregated global representations)
        Returns:
            seq_logits: [batch, 1]
            token_logits: [batch, seq_len, 1]
        """
        seq_logits = self.seq_risk(seq_features)
        token_logits = self.token_risk(token_features)
        return seq_logits, token_logits

class BIOSpanHead(nn.Module):
    """
    Head 2: BIO Span Detection (token-level sequence labeler).
    Outputs logits for 3 classes: 0=O, 1=B, 2=I.
    """
    def __init__(self, feature_dim: int):
        super().__init__()
        self.classifier = nn.Sequential(
            nn.Linear(feature_dim, 256),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(256, 3)
        )

    def forward(self, token_features: torch.Tensor) -> torch.Tensor:
        """
        Returns:
            logits: [batch, seq_len, 3]
        """
        return self.classifier(token_features)

class CategoryHead(nn.Module):
    """
    Head 3: Hallucination Category Classification (5 classes: Invention, Mischaracterization, OCR, Miscounting, Other).
    """
    def __init__(self, feature_dim: int):
        super().__init__()
        self.classifier = nn.Sequential(
            nn.Linear(feature_dim, 256),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(256, 5)
        )

    def forward(self, token_features: torch.Tensor) -> torch.Tensor:
        """
        Returns:
            logits: [batch, seq_len, 5]
        """
        return self.classifier(token_features)

class CalibrationHead(nn.Module):
    """
    Head 4: Confidence Calibration.
    Applies temperature scaling or a calibration MLP to yield well-calibrated hallucination probabilities.
    """
    def __init__(self, use_calibration_network: bool = True):
        super().__init__()
        self.use_calibration_network = use_calibration_network
        
        # Method A: Temperature scaling
        self.temperature = nn.Parameter(torch.ones(1))
        
        # Method B: Calibration Network (fuses outputs of BIO head and Token Risk head)
        # Inputs: 3 (BIO logits) + 1 (Token Risk logit) = 4 values
        if self.use_calibration_network:
            self.calibrator = nn.Sequential(
                nn.Linear(4, 16),
                nn.ReLU(),
                nn.Linear(16, 1)
            )

    def forward(
        self,
        bio_logits: torch.Tensor,
        token_risk_logits: torch.Tensor
    ) -> torch.Tensor:
        """
        Fuses predictions to output a single calibrated hallucination probability per token.
        
        Args:
            bio_logits: [batch, seq_len, 3]
            token_risk_logits: [batch, seq_len, 1]
            
        Returns:
            calibrated_probs: [batch, seq_len, 1] (values in range [0, 1])
        """
        if self.use_calibration_network:
            # Concatenate logits along the feature dimension
            combined_logits = torch.cat([bio_logits, token_risk_logits], dim=-1) # [batch, seq_len, 4]
            calibrated_logits = self.calibrator(combined_logits)
            return torch.sigmoid(calibrated_logits)
        else:
            # Fallback: Temperature scale the token risk logit directly
            # bounded temperature: max(temp, 1e-4) to prevent division by zero
            temp = torch.clamp(self.temperature, min=1e-4)
            scaled_logits = token_risk_logits / temp
            return torch.sigmoid(scaled_logits)
