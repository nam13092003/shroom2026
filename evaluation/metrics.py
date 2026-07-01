import numpy as np
from typing import List, Tuple, Dict, Any

def compute_char_iou(
    gold_spans: List[Tuple[int, int]],
    pred_spans: List[Tuple[int, int]],
    text_len: int
) -> float:
    """
    Calculate character-level Intersection-over-Union (IoU) of hallucinated spans.
    
    Args:
        gold_spans: List of (start, end) ground truth spans.
        pred_spans: List of (start, end) predicted spans.
        text_len: Length of the original response text.
        
    Returns:
        float: Character-level IoU value.
    """
    gold_mask = np.zeros(text_len, dtype=bool)
    pred_mask = np.zeros(text_len, dtype=bool)
    
    for start, end in gold_spans:
        gold_mask[max(0, start):min(text_len, end)] = True
        
    for start, end in pred_spans:
        pred_mask[max(0, start):min(text_len, end)] = True
        
    intersection = np.logical_and(gold_mask, pred_mask).sum()
    union = np.logical_or(gold_mask, pred_mask).sum()
    
    if union == 0:
        # If both gold and pred are empty, the prediction is perfect (no hallucination correctly predicted)
        return 1.0
        
    return float(intersection / union)

def compute_ece(
    preds: np.ndarray,
    targets: np.ndarray,
    num_bins: int = 10
) -> float:
    """
    Calculate Expected Calibration Error (ECE) for probabilities.
    Supports continuous/empirical target probabilities in range [0, 1].
    
    Args:
        preds: 1D array of predicted probabilities.
        targets: 1D array of target empirical probabilities.
        num_bins: Number of confidence bins.
        
    Returns:
        float: Expected Calibration Error value.
    """
    # Flatten arrays
    preds = np.asarray(preds).flatten()
    targets = np.asarray(targets).flatten()
    
    # Filter out padding values (e.g. -100)
    valid_mask = (targets >= 0.0) & (targets <= 1.0)
    if not valid_mask.any():
        return 0.0
        
    preds = preds[valid_mask]
    targets = targets[valid_mask]
    
    bin_boundaries = np.linspace(0, 1, num_bins + 1)
    ece = 0.0
    n_samples = len(preds)
    
    for i in range(num_bins):
        bin_lower = bin_boundaries[i]
        bin_upper = bin_boundaries[i + 1]
        
        # Determine elements in this bin
        in_bin = (preds >= bin_lower) & (preds < bin_upper) if i < num_bins - 1 else (preds >= bin_lower) & (preds <= bin_upper)
        prop_in_bin = in_bin.sum() / n_samples
        
        if prop_in_bin > 0:
            accuracy_in_bin = targets[in_bin].mean()
            avg_confidence_in_bin = preds[in_bin].mean()
            ece += prop_in_bin * np.abs(avg_confidence_in_bin - accuracy_in_bin)
            
    return float(ece)

def compute_classification_metrics(
    preds: np.ndarray,
    targets: np.ndarray,
    num_classes: int = 2,
    ignore_index: int = -100
) -> Dict[str, Any]:
    """
    Calculate standard classification metrics: Precision, Recall, F1, and Confusion Matrix.
    
    Args:
        preds: 1D array of predictions.
        targets: 1D array of ground truth labels.
        num_classes: Number of classes.
        ignore_index: Index to ignore in evaluation.
        
    Returns:
        Dict: Computed metric summaries.
    """
    preds = np.asarray(preds).flatten()
    targets = np.asarray(targets).flatten()
    
    mask = (targets != ignore_index)
    if not mask.any():
        return {
            "precision": 0.0,
            "recall": 0.0,
            "f1": 0.0,
            "confusion_matrix": np.zeros((num_classes, num_classes)).tolist()
        }
        
    p = preds[mask]
    t = targets[mask]
    
    # Calculate confusion matrix
    cm = np.zeros((num_classes, num_classes), dtype=int)
    for i in range(len(p)):
        if 0 <= p[i] < num_classes and 0 <= t[i] < num_classes:
            cm[t[i], p[i]] += 1
            
    # Calculate macro precision, recall, F1
    precisions = []
    recalls = []
    f1s = []
    
    for c in range(num_classes):
        tp = cm[c, c]
        fp = cm[:, c].sum() - tp
        fn = cm[c, :].sum() - tp
        
        prec = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        rec = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = 2 * prec * rec / (prec + rec) if (prec + rec) > 0 else 0.0
        
        precisions.append(prec)
        recalls.append(rec)
        f1s.append(f1)
        
    return {
        "precision": float(np.mean(precisions)),
        "recall": float(np.mean(recalls)),
        "f1": float(np.mean(f1s)),
        "confusion_matrix": cm.tolist()
    }
