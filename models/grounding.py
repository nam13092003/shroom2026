import torch
import torch.nn as nn
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Tuple

class GroundingInterface(nn.Module, ABC):
    """
    Abstract interface for pluggable grounding modules.
    Grounding modules take images and generated text, and produce token-level features
    that represent verification signals (e.g., OCR presence, object counts, spatial alignment).
    """
    def __init__(self, feature_dim: int):
        super().__init__()
        self.feature_dim = feature_dim

    @abstractmethod
    def forward(
        self,
        images: List[Any],
        texts: List[str],
        tokenized_offsets: List[List[Tuple[int, int]]],
        max_len: int,
        device: torch.device
    ) -> torch.Tensor:
        """
        Extract token-level grounding features.
        
        Args:
            images: List of PIL Images or image tensors.
            texts: List of prompt + response texts.
            tokenized_offsets: List of character offsets for each token in the sequence.
            max_len: Maximum sequence length to pad to.
            device: Device to place the output tensor on.
            
        Returns:
            Tensor of shape [batch, max_len, feature_dim] containing grounding features.
        """
        pass

class DummyGrounding(GroundingInterface):
    """A dummy grounding module that outputs zero features. Used when grounding is disabled."""
    def forward(
        self,
        images: List[Any],
        texts: List[str],
        tokenized_offsets: List[List[Tuple[int, int]]],
        max_len: int,
        device: torch.device
    ) -> torch.Tensor:
        batch_size = len(texts)
        return torch.zeros((batch_size, max_len, self.feature_dim), dtype=torch.float32, device=device)

class MockGroundingModule(GroundingInterface):
    """
    A mock grounding module that simulates OCR and object counting verification.
    For example:
    - Feature 0: Simulated OCR alignment (high if word is found in OCR text)
    - Feature 1: Simulated Object matching (high if object is detected)
    """
    def forward(
        self,
        images: List[Any],
        texts: List[str],
        tokenized_offsets: List[List[Tuple[int, int]]],
        max_len: int,
        device: torch.device
    ) -> torch.Tensor:
        batch_size = len(texts)
        features = torch.zeros((batch_size, max_len, self.feature_dim), dtype=torch.float32, device=device)
        
        for b in range(batch_size):
            text = texts[b]
            offsets = tokenized_offsets[b]
            for t, (start, end) in enumerate(offsets):
                if t >= max_len:
                    break
                if start == 0 and end == 0:
                    continue
                # Extract token string
                token_str = text[start:end].lower()
                
                # OCR Mock: check if token represents text or numbers
                ocr_score = 0.0
                if any(char.isdigit() for char in token_str):
                    ocr_score = 0.8
                elif len(token_str) > 2 and token_str in ["ship", "cat", "desk", "garlic", "cauliflower"]:
                    ocr_score = 0.9
                    
                # Object Count Mock: check for numbers or quantities
                count_score = 0.0
                if token_str in ["three", "four", "one", "two", "legs", "knobs", "masts"]:
                    count_score = 0.75
                    
                features[b, t, 0] = ocr_score
                features[b, t, 1] = count_score
                # Add random noise for remaining features to simulate complex representations
                if self.feature_dim > 2:
                    features[b, t, 2:] = torch.randn(self.feature_dim - 2, device=device) * 0.05
                    
        return features
