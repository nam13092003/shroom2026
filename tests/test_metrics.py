import numpy as np
import pytest
from evaluation.metrics import compute_char_iou, compute_ece, compute_classification_metrics

def test_compute_char_iou():
    text_len = 50
    # Gold spans: (5, 10), (20, 25)
    # Total gold chars: 5 (5..9) + 5 (20..24) = 10 chars
    gold = [(5, 10), (20, 25)]
    
    # Perfect prediction
    pred_perfect = [(5, 10), (20, 25)]
    assert compute_char_iou(gold, pred_perfect, text_len) == 1.0
    
    # Overlapping prediction
    # Pred: (5, 12) -> 7 chars (5..11), (22, 25) -> 3 chars (22..24)
    # Intersection: (5..9) -> 5 chars, (22..24) -> 3 chars. Total intersection = 8 chars
    # Union: (5..11) -> 7 chars, (20..24) -> 5 chars. Total union = 12 chars
    pred_overlap = [(5, 12), (22, 25)]
    assert abs(compute_char_iou(gold, pred_overlap, text_len) - (8 / 12)) < 1e-5
    
    # Empty gold and empty pred
    assert compute_char_iou([], [], text_len) == 1.0

def test_compute_ece():
    # Simple ECE test with 2 bins: [0, 0.5), [0.5, 1.0]
    # Predictions and target empirical probabilities
    preds = np.array([0.1, 0.2, 0.8, 0.9])
    targets = np.array([0.0, 0.0, 1.0, 1.0])
    
    # Bin 1: [0, 0.5) -> [0.1, 0.2]. Count = 2. Avg conf = 0.15, Avg acc = 0.0. Diff = 0.15
    # Bin 2: [0.5, 1.0] -> [0.8, 0.9]. Count = 2. Avg conf = 0.85, Avg acc = 1.0. Diff = 0.15
    # ECE = (2/4)*0.15 + (2/4)*0.15 = 0.15
    ece = compute_ece(preds, targets, num_bins=2)
    assert abs(ece - 0.15) < 1e-4
    
    # ECE with ignored/padded targets
    preds_pad = np.array([0.1, 0.2, 0.8, 0.9, 0.5])
    targets_pad = np.array([0.0, 0.0, 1.0, 1.0, -100.0]) # 0.5 pred is ignored
    ece_pad = compute_ece(preds_pad, targets_pad, num_bins=2)
    assert abs(ece_pad - 0.15) < 1e-4

def test_compute_classification_metrics():
    preds = np.array([0, 1, 0, 1, 0, 1])
    targets = np.array([0, 1, 0, 0, 1, 1])
    # CM:
    # Target 0: predicted 0 twice, predicted 1 once. CM[0,0]=2, CM[0,1]=1
    # Target 1: predicted 0 once, predicted 1 twice. CM[1,0]=1, CM[1,1]=2
    metrics = compute_classification_metrics(preds, targets, num_classes=2)
    
    assert metrics['precision'] == 2/3
    assert metrics['recall'] == 2/3
    assert metrics['f1'] == 2/3
    assert metrics['confusion_matrix'] == [[2, 1], [1, 2]]
