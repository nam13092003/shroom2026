import pytest
import torch
from models.grounding import DummyGrounding, MockGroundingModule
from models.heads import RiskHead, BIOSpanHead, CategoryHead, CalibrationHead
from models.multitask_model import MultiTaskModel
from losses.multitask_losses import (
    FocalLoss,
    DiceLoss,
    SpanLoss,
    CalibrationLoss,
    WeightedMultiTaskLoss
)

def test_grounding_modules():
    device = torch.device('cpu')
    batch_size = 2
    max_len = 10
    
    # Dummy Grounding
    dummy = DummyGrounding(feature_dim=16)
    out_dummy = dummy(
        images=[],
        texts=["hello", "world"],
        tokenized_offsets=[[(0, 5)], [(0, 5)]],
        max_len=max_len,
        device=device
    )
    assert out_dummy.shape == (batch_size, max_len, 16)
    assert (out_dummy == 0).all()

    # Mock Grounding
    mock = MockGroundingModule(feature_dim=8)
    out_mock = mock(
        images=[],
        texts=["This is a ship with four masts", "A white cat"],
        tokenized_offsets=[
            [(0, 4), (5, 7), (8, 9), (10, 14), (15, 19), (20, 24), (25, 30)],
            [(0, 1), (2, 7), (8, 11)]
        ],
        max_len=max_len,
        device=device
    )
    assert out_mock.shape == (batch_size, max_len, 8)
    # Check that "ship" or "four" triggers high signals in Mock Grounding
    # for the first text:
    # "ship" is at offset index 3
    # "four" is at offset index 5
    assert out_mock[0, 3, 0] > 0.5  # ocr mock for "ship"
    assert out_mock[0, 5, 1] > 0.5  # counting mock for "four"

def test_heads():
    feature_dim = 128
    batch_size = 4
    seq_len = 12
    
    encoded = torch.randn(batch_size, seq_len, feature_dim)
    seq_features = torch.randn(batch_size, feature_dim)
    
    # Heads initialization
    risk_head = RiskHead(feature_dim=feature_dim)
    bio_head = BIOSpanHead(feature_dim=feature_dim)
    cat_head = CategoryHead(feature_dim=feature_dim)
    calib_head = CalibrationHead(use_calibration_network=True)
    
    # Forward passes
    seq_risk, token_risk = risk_head(encoded, seq_features)
    assert seq_risk.shape == (batch_size, 1)
    assert token_risk.shape == (batch_size, seq_len, 1)
    
    bio_logits = bio_head(encoded)
    assert bio_logits.shape == (batch_size, seq_len, 3)
    
    cat_logits = cat_head(encoded)
    assert cat_logits.shape == (batch_size, seq_len, 5)
    
    calibrated_probs = calib_head(bio_logits, token_risk)
    assert calibrated_probs.shape == (batch_size, seq_len, 1)
    assert (calibrated_probs >= 0.0).all() and (calibrated_probs <= 1.0).all()

def test_multitask_model_and_losses():
    # Model parameters
    d_hidden = 64
    d_vision = 32
    d_grounding = 8
    encoder_dim = 16
    batch_size = 2
    seq_len = 8
    num_patches = 10
    
    model = MultiTaskModel(
        d_hidden=d_hidden,
        d_vision=d_vision,
        d_grounding=d_grounding,
        encoder_dim=encoder_dim,
        use_calibration_network=True
    )
    
    # Create mock batch data
    batch = {
        'decoder_hidden_states': torch.randn(batch_size, seq_len, d_hidden),
        'vision_features': torch.randn(batch_size, num_patches, d_vision),
        'query_hidden_states': torch.randn(batch_size, d_hidden),
        'cross_attention': torch.softmax(torch.randn(batch_size, seq_len, num_patches), dim=-1),
        'attention_mask': torch.ones(batch_size, seq_len, dtype=torch.long),
        # Target labels
        'seq_labels': torch.tensor([0.0, 1.0], dtype=torch.float),
        'bio_tags': torch.tensor([
            [0, 1, 2, 0, 0, -100, -100, -100],
            [0, 0, 1, 2, 2, 0, -100, -100]
        ], dtype=torch.long),
        'categories': torch.tensor([
            [-100, 0, 0, -100, -100, -100, -100, -100],
            [-100, -100, 1, 1, 1, -100, -100, -100]
        ], dtype=torch.long),
        'probabilities': torch.tensor([
            [0.0, 0.66, 0.66, 0.0, 0.0, -100.0, -100.0, -100.0],
            [0.0, 0.0, 1.0, 1.0, 1.0, 0.0, -100.0, -100.0]
        ], dtype=torch.float)
    }
    
    # Forward pass
    predictions = model(batch)
    
    assert 'seq_risk_logits' in predictions
    assert 'token_risk_logits' in predictions
    assert 'bio_logits' in predictions
    assert 'category_logits' in predictions
    assert 'calibrated_probabilities' in predictions
    
    assert predictions['bio_logits'].shape == (batch_size, seq_len, 3)
    assert predictions['category_logits'].shape == (batch_size, seq_len, 5)
    
    # Loss computation
    loss_module = WeightedMultiTaskLoss()
    loss_dict = loss_module(predictions, batch)
    
    assert 'loss' in loss_dict
    assert 'l_seq_risk' in loss_dict
    assert 'l_bio_span' in loss_dict
    assert 'l_category' in loss_dict
    assert 'l_calib' in loss_dict
    
    loss = loss_dict['loss']
    assert loss.item() > 0.0
    
    # Backward pass verification
    loss.backward()
    
    # Verify that gradients exist for model parameters
    for name, param in model.named_parameters():
        if param.requires_grad:
            # Skip checking gradient for temperature scale if calibration network is used instead
            if name == "calibration_head.temperature" and model.calibration_head.use_calibration_network:
                continue
            assert param.grad is not None, f"Parameter {name} does not have gradients!"
            
def test_individual_losses():
    # Verify Focal, Dice, Span, and Calibration Losses individually
    logits = torch.tensor([
        [10.0, -10.0, -10.0],
        [-10.0, 10.0, -10.0],
        [-10.0, -10.0, 10.0]
    ], dtype=torch.float)
    targets = torch.tensor([0, 1, 2], dtype=torch.long)
    
    # Focal Loss (should be extremely low since predictions are correct)
    fl = FocalLoss()
    loss_fl = fl(logits, targets)
    assert loss_fl.item() < 0.1
    
    # Dice Loss
    dl = DiceLoss()
    loss_dl = dl(logits, targets)
    assert loss_dl.item() < 0.1
    
    # Span Loss
    sl = SpanLoss()
    loss_sl = sl(logits, targets)
    assert loss_sl.item() < 0.2
    
    # Calibration Loss
    calib = CalibrationLoss()
    probs = torch.tensor([0.9, 0.1, 0.5], dtype=torch.float)
    target_probs = torch.tensor([1.0, 0.0, 0.5], dtype=torch.float)
    loss_calib = calib(probs, target_probs)
    # expected MSE: ((0.9-1)^2 + (0.1-0)^2 + (0.5-0.5)^2)/3 = (0.01 + 0.01 + 0)/3 = 0.006666
    assert abs(loss_calib.item() - 0.006666) < 1e-4
