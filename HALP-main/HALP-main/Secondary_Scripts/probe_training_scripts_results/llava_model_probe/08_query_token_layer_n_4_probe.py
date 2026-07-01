"""
LLaVa-Next-8B Query Token Layer n//4 Representation Probe Training
====================================================================
Trains a binary classifier to predict hallucination from query token representations
at layer 8 (n//4 where n=32 total layers).

Embeddings: query_token_representation/layer_8 from H5 files
Target: is_hallucinating_manual from CSV
"""

import os
import h5py
import pandas as pd
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, roc_auc_score, confusion_matrix
import json
import logging
from datetime import datetime
from tqdm import tqdm
import glob
import matplotlib.pyplot as plt
import seaborn as sns

# ==================== CONFIGURATION ====================

CONFIG = {
    # Data paths
    "H5_DIR": "/root/akhil/HALP_EACL_Models/Models/LLaVa_model/llava_output",
    "CSV_PATH": "/root/akhil/FInal_CSV_Hallucination/llava_manually_reviewed.csv",
    "OUTPUT_DIR": "/root/akhil/probe_training_scripts/llava_model_probe/results/query_token_layer_n_4",

    # Model name and embedding type
    "MODEL_NAME": "LLaVa-Next-8B",
    "EMBEDDING_TYPE": "query_token_representation",
    "LAYER_NAME": "layer_8",
    "TARGET_COLUMN": "is_hallucinating_manual",

    # Neural network architecture
    "LAYER_SIZES": [512, 256, 128],
    "DROPOUT_RATE": 0.3,

    # Training parameters
    "LEARNING_RATE": 0.001,
    "BATCH_SIZE": 32,
    "EPOCHS": 50,

    # Data splits (train/test only)
    "TEST_SIZE": 0.2,
    "RANDOM_STATE": 42,

    # Device
    "DEVICE": "cuda" if torch.cuda.is_available() else "cpu"
}

# ==================== SETUP ====================

os.makedirs(CONFIG["OUTPUT_DIR"], exist_ok=True)

# Setup logging
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
log_file = os.path.join(CONFIG["OUTPUT_DIR"], f'training_{timestamp}.log')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ==================== DATA LOADING ====================

def load_hallucination_labels(csv_path):
    """Load hallucination labels from CSV."""
    logger.info(f"Loading labels from: {csv_path}")
    df = pd.read_csv(csv_path, low_memory=False)

    labels = {}
    for _, row in df.iterrows():
        question_id = row['question_id']

        # Handle different formats
        target_value = row[CONFIG["TARGET_COLUMN"]]
        if isinstance(target_value, str):
            target_value = target_value.lower() in ['true', '1', 'yes']
        else:
            target_value = bool(target_value)

        labels[question_id] = {
            'label': int(target_value),
            'image_id': row['image_id'],
            'question': row['question']
        }

    logger.info(f"Loaded {len(labels)} labels")
    return labels

def load_embeddings_from_h5(h5_dir, embedding_type, labels_dict, layer_name=None):
    """
    Load embeddings from H5 files.

    Args:
        h5_dir: Directory containing H5 files
        embedding_type: Type of embedding to load
            - 'vision_only_representation' (direct access)
            - 'vision_token_representation' (requires layer_name)
            - 'query_token_representation' (requires layer_name)
        labels_dict: Dictionary mapping question_id to labels
        layer_name: Layer name for nested embeddings (e.g., 'layer_0', 'layer_8')
    """
    logger.info(f"Loading embeddings: {embedding_type}" + (f" / {layer_name}" if layer_name else ""))

    h5_files = sorted(glob.glob(os.path.join(h5_dir, "*.h5")))
    if not h5_files:
        raise FileNotFoundError(f"No H5 files found in {h5_dir}")

    logger.info(f"Found {len(h5_files)} H5 files")

    embeddings_list = []
    labels_list = []
    question_ids = []

    for h5_file in tqdm(h5_files, desc="Processing H5 files"):
        with h5py.File(h5_file, 'r') as f:
            for question_id in f.keys():
                # Skip if no label
                if question_id not in labels_dict:
                    continue

                sample_group = f[question_id]

                # Extract embedding
                try:
                    if layer_name:
                        # Nested access: vision_token_representation/layer_X or query_token_representation/layer_X
                        if embedding_type in sample_group:
                            group = sample_group[embedding_type]
                            if layer_name in group:
                                embedding = group[layer_name][:]

                                embeddings_list.append(embedding)
                                labels_list.append(labels_dict[question_id]['label'])
                                question_ids.append(question_id)
                            else:
                                logger.warning(f"Missing {layer_name} in {embedding_type} for {question_id}")
                        else:
                            logger.warning(f"Missing {embedding_type} for {question_id}")
                    else:
                        # Direct access: vision_only_representation
                        if embedding_type in sample_group:
                            embedding = sample_group[embedding_type][:]

                            embeddings_list.append(embedding)
                            labels_list.append(labels_dict[question_id]['label'])
                            question_ids.append(question_id)
                        else:
                            logger.warning(f"Missing {embedding_type} for {question_id}")

                except Exception as e:
                    logger.warning(f"Error loading {question_id}: {e}")
                    continue

    if len(embeddings_list) == 0:
        raise ValueError(f"No embeddings found for {embedding_type}" + (f"/{layer_name}" if layer_name else ""))

    # Handle variable-size embeddings (for vision_only_representation in some models)
    # Check if all embeddings have the same shape
    shapes = [emb.shape for emb in embeddings_list]
    if len(set(shapes)) > 1:
        # Variable shapes detected - pad to max length
        max_len = max(emb.shape[0] for emb in embeddings_list)
        logger.info(f"Variable embedding shapes detected. Padding to max length: {max_len}")
        padded_embeddings = []
        for emb in embeddings_list:
            if len(emb.shape) == 1:  # 1D embeddings
                padded = np.zeros(max_len, dtype=emb.dtype)
                padded[:len(emb)] = emb
                padded_embeddings.append(padded)
            else:
                raise ValueError(f"Unexpected embedding shape: {emb.shape}")
        embeddings = np.stack(padded_embeddings)
    else:
        embeddings = np.stack(embeddings_list)

    labels = np.array(labels_list)

    logger.info(f"Loaded {len(embeddings)} samples")
    logger.info(f"Embedding shape: {embeddings.shape}")
    logger.info(f"Label distribution - Class 0: {(labels==0).sum()}, Class 1: {(labels==1).sum()}")

    return embeddings, labels, question_ids

# ==================== PYTORCH DATASET ====================

class EmbeddingDataset(Dataset):
    """PyTorch dataset for embeddings."""

    def __init__(self, embeddings, labels):
        self.embeddings = torch.tensor(embeddings, dtype=torch.float32)
        self.labels = torch.tensor(labels, dtype=torch.float32)

    def __len__(self):
        return len(self.labels)

    def __getitem__(self, idx):
        return self.embeddings[idx], self.labels[idx]

# ==================== MODEL ====================

class HallucinationProbe(nn.Module):
    """Binary classifier probe for hallucination detection."""

    def __init__(self, input_dim, layer_sizes, dropout_rate=0.3):
        super().__init__()

        layers = []
        prev_dim = input_dim

        for size in layer_sizes:
            layers.append(nn.Linear(prev_dim, size))
            layers.append(nn.ReLU())
            layers.append(nn.BatchNorm1d(size))
            layers.append(nn.Dropout(dropout_rate))
            prev_dim = size

        # Output layer
        layers.append(nn.Linear(prev_dim, 1))
        layers.append(nn.Sigmoid())

        self.model = nn.Sequential(*layers)

    def forward(self, x):
        return self.model(x).squeeze()

# ==================== TRAINING ====================

def train_epoch(model, train_loader, criterion, optimizer, device):
    """Train for one epoch."""
    model.train()
    total_loss = 0.0
    correct = 0
    total = 0

    for X_batch, y_batch in train_loader:
        X_batch, y_batch = X_batch.to(device), y_batch.to(device)

        optimizer.zero_grad()
        outputs = model(X_batch)
        loss = criterion(outputs, y_batch)
        loss.backward()
        optimizer.step()

        total_loss += loss.item() * X_batch.size(0)
        predicted = (outputs > 0.5).float()
        total += y_batch.size(0)
        correct += (predicted == y_batch).sum().item()

    avg_loss = total_loss / total
    accuracy = correct / total

    return avg_loss, accuracy

def train_model(X_train, y_train, input_dim):
    """Train the probe on training set only."""

    # Create dataset and loader
    train_dataset = EmbeddingDataset(X_train, y_train)
    train_loader = DataLoader(train_dataset, batch_size=CONFIG["BATCH_SIZE"], shuffle=True)

    # Initialize model
    model = HallucinationProbe(
        input_dim=input_dim,
        layer_sizes=CONFIG["LAYER_SIZES"],
        dropout_rate=CONFIG["DROPOUT_RATE"]
    ).to(CONFIG["DEVICE"])

    criterion = nn.BCELoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=CONFIG["LEARNING_RATE"])

    # Training history
    history = {
        'train_loss': [],
        'train_acc': []
    }

    logger.info("Starting training...")
    logger.info(f"Device: {CONFIG['DEVICE']}")
    logger.info(f"Train samples: {len(X_train)}")
    logger.info(f"Architecture: {input_dim} -> {' -> '.join(map(str, CONFIG['LAYER_SIZES']))} -> 1")

    for epoch in range(CONFIG["EPOCHS"]):
        train_loss, train_acc = train_epoch(model, train_loader, criterion, optimizer, CONFIG["DEVICE"])

        history['train_loss'].append(train_loss)
        history['train_acc'].append(train_acc)

        if (epoch + 1) % 10 == 0:
            logger.info(f"Epoch {epoch+1}/{CONFIG['EPOCHS']}: "
                       f"Train Loss: {train_loss:.4f}, Train Acc: {train_acc:.4f}")

    logger.info("Training completed!")

    return model, history

# ==================== EVALUATION ====================

def evaluate_model(model, X_data, y_data, dataset_name="Test"):
    """Evaluate model and compute metrics."""

    model.eval()

    dataset = EmbeddingDataset(X_data, y_data)
    data_loader = DataLoader(dataset, batch_size=CONFIG["BATCH_SIZE"], shuffle=False)

    all_preds = []
    all_probs = []
    all_labels = []

    with torch.no_grad():
        for X_batch, y_batch in data_loader:
            X_batch = X_batch.to(CONFIG["DEVICE"])
            outputs = model(X_batch).cpu().numpy()

            all_probs.extend(outputs)
            all_preds.extend((outputs > 0.5).astype(int))
            all_labels.extend(y_batch.numpy())

    all_preds = np.array(all_preds)
    all_probs = np.array(all_probs)
    all_labels = np.array(all_labels)

    # Calculate metrics
    accuracy = accuracy_score(all_labels, all_preds)
    precision, recall, f1, _ = precision_recall_fscore_support(all_labels, all_preds, average='binary', zero_division=0)

    try:
        auroc = roc_auc_score(all_labels, all_probs)
    except ValueError:
        auroc = 0.5
        logger.warning(f"Only one class in {dataset_name} set, AUROC set to 0.5")

    cm = confusion_matrix(all_labels, all_preds)

    metrics = {
        'accuracy': float(accuracy),
        'precision': float(precision),
        'recall': float(recall),
        'f1': float(f1),
        'auroc': float(auroc),
        'confusion_matrix': cm.tolist(),
        'num_samples': len(all_labels),
        'num_class_0': int((all_labels == 0).sum()),
        'num_class_1': int((all_labels == 1).sum())
    }

    logger.info("=" * 60)
    logger.info(f"{dataset_name.upper()} METRICS:")
    logger.info(f"  Accuracy:  {accuracy:.4f}")
    logger.info(f"  Precision: {precision:.4f}")
    logger.info(f"  Recall:    {recall:.4f}")
    logger.info(f"  F1 Score:  {f1:.4f}")
    logger.info(f"  AUROC:     {auroc:.4f}")
    logger.info("=" * 60)

    return metrics, all_labels, all_probs

def plot_confusion_matrix(cm_train, cm_test):
    """Plot and save confusion matrices for train and test sets."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

    # Train confusion matrix
    sns.heatmap(cm_train, annot=True, fmt='d', cmap='Blues', ax=ax1,
                xticklabels=['No Hallucination', 'Hallucination'],
                yticklabels=['No Hallucination', 'Hallucination'])
    ax1.set_title('Train Set - Confusion Matrix')
    ax1.set_ylabel('True Label')
    ax1.set_xlabel('Predicted Label')

    # Test confusion matrix
    sns.heatmap(cm_test, annot=True, fmt='d', cmap='Greens', ax=ax2,
                xticklabels=['No Hallucination', 'Hallucination'],
                yticklabels=['No Hallucination', 'Hallucination'])
    ax2.set_title('Test Set - Confusion Matrix')
    ax2.set_ylabel('True Label')
    ax2.set_xlabel('Predicted Label')

    plt.tight_layout()
    plt.savefig(os.path.join(CONFIG["OUTPUT_DIR"], 'confusion_matrix.png'), dpi=300)
    plt.close()
    logger.info("Confusion matrices saved")

def plot_roc_curve(y_train, train_probs, y_test, test_probs):
    """Plot and save ROC curves for train and test sets."""
    from sklearn.metrics import roc_curve, auc

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

    # Train ROC curve
    try:
        fpr_train, tpr_train, _ = roc_curve(y_train, train_probs)
        roc_auc_train = auc(fpr_train, tpr_train)

        ax1.plot(fpr_train, tpr_train, color='blue', lw=2,
                label=f'ROC curve (AUROC = {roc_auc_train:.4f})')
        ax1.plot([0, 1], [0, 1], color='gray', lw=2, linestyle='--', label='Random')
        ax1.set_xlim([0.0, 1.0])
        ax1.set_ylim([0.0, 1.05])
        ax1.set_xlabel('False Positive Rate')
        ax1.set_ylabel('True Positive Rate')
        ax1.set_title('Train Set - ROC Curve')
        ax1.legend(loc="lower right")
        ax1.grid(True, alpha=0.3)
    except ValueError:
        ax1.text(0.5, 0.5, 'ROC curve not available\n(single class)',
                ha='center', va='center', transform=ax1.transAxes)
        ax1.set_title('Train Set - ROC Curve')

    # Test ROC curve
    try:
        fpr_test, tpr_test, _ = roc_curve(y_test, test_probs)
        roc_auc_test = auc(fpr_test, tpr_test)

        ax2.plot(fpr_test, tpr_test, color='green', lw=2,
                label=f'ROC curve (AUROC = {roc_auc_test:.4f})')
        ax2.plot([0, 1], [0, 1], color='gray', lw=2, linestyle='--', label='Random')
        ax2.set_xlim([0.0, 1.0])
        ax2.set_ylim([0.0, 1.05])
        ax2.set_xlabel('False Positive Rate')
        ax2.set_ylabel('True Positive Rate')
        ax2.set_title('Test Set - ROC Curve')
        ax2.legend(loc="lower right")
        ax2.grid(True, alpha=0.3)
    except ValueError:
        ax2.text(0.5, 0.5, 'ROC curve not available\n(single class)',
                ha='center', va='center', transform=ax2.transAxes)
        ax2.set_title('Test Set - ROC Curve')

    plt.tight_layout()
    plt.savefig(os.path.join(CONFIG["OUTPUT_DIR"], 'roc_curve.png'), dpi=300)
    plt.close()
    logger.info("ROC curves saved")

def plot_training_history(history):
    """Plot training history."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 5))

    # Loss
    ax1.plot(history['train_loss'], label='Train Loss', color='blue')
    ax1.set_xlabel('Epoch')
    ax1.set_ylabel('Loss')
    ax1.set_title('Training Loss')
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    # Accuracy
    ax2.plot(history['train_acc'], label='Train Accuracy', color='green')
    ax2.set_xlabel('Epoch')
    ax2.set_ylabel('Accuracy')
    ax2.set_title('Training Accuracy')
    ax2.legend()
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(os.path.join(CONFIG["OUTPUT_DIR"], 'training_history.png'), dpi=300)
    plt.close()
    logger.info("Training history plot saved")

# ==================== MAIN ====================

def main():
    """Main training pipeline."""
    logger.info("=" * 80)
    logger.info(f"{CONFIG['MODEL_NAME']} - {CONFIG['EMBEDDING_TYPE']}/{CONFIG['LAYER_NAME']} Probe Training")
    logger.info("=" * 80)
    logger.info(f"Target: {CONFIG['TARGET_COLUMN']}")
    logger.info(f"Output directory: {CONFIG['OUTPUT_DIR']}")
    logger.info("")

    # Load labels
    labels_dict = load_hallucination_labels(CONFIG["CSV_PATH"])

    # Load embeddings
    embeddings, labels, question_ids = load_embeddings_from_h5(
        CONFIG["H5_DIR"],
        CONFIG["EMBEDDING_TYPE"],
        labels_dict,
        layer_name=CONFIG["LAYER_NAME"]
    )

    input_dim = embeddings.shape[1]
    logger.info(f"Input dimension: {input_dim}")

    # Split data into train and test only
    X_train, X_test, y_train, y_test = train_test_split(
        embeddings, labels,
        test_size=CONFIG["TEST_SIZE"],
        random_state=CONFIG["RANDOM_STATE"],
        stratify=labels
    )

    logger.info(f"\nData splits:")
    logger.info(f"  Train: {len(X_train)} samples ({(1-CONFIG['TEST_SIZE'])*100:.0f}%)")
    logger.info(f"  Test:  {len(X_test)} samples ({CONFIG['TEST_SIZE']*100:.0f}%)")

    # Print class distribution
    train_class_0 = (y_train == 0).sum()
    train_class_1 = (y_train == 1).sum()
    test_class_0 = (y_test == 0).sum()
    test_class_1 = (y_test == 1).sum()

    logger.info(f"\nClass distribution:")
    logger.info(f"  Train set:")
    logger.info(f"    Class 0 (No Hallucination): {train_class_0} ({train_class_0/len(y_train)*100:.1f}%)")
    logger.info(f"    Class 1 (Hallucination):    {train_class_1} ({train_class_1/len(y_train)*100:.1f}%)")
    logger.info(f"  Test set:")
    logger.info(f"    Class 0 (No Hallucination): {test_class_0} ({test_class_0/len(y_test)*100:.1f}%)")
    logger.info(f"    Class 1 (Hallucination):    {test_class_1} ({test_class_1/len(y_test)*100:.1f}%)")
    logger.info("")

    # Train model on training set only
    logger.info("=" * 80)
    logger.info("TRAINING PHASE")
    logger.info("=" * 80)
    model, history = train_model(X_train, y_train, input_dim)

    # Save model
    model_path = os.path.join(CONFIG["OUTPUT_DIR"], 'probe_model.pt')
    torch.save({
        'model_state_dict': model.state_dict(),
        'config': CONFIG,
        'input_dim': input_dim,
        'timestamp': timestamp
    }, model_path)
    logger.info(f"\nModel saved: {model_path}")

    # Plot training history
    plot_training_history(history)

    # Load model and evaluate on both train and test sets
    logger.info("\n" + "=" * 80)
    logger.info("EVALUATION PHASE")
    logger.info("=" * 80)
    logger.info("Loading saved model...")

    # Load model
    checkpoint = torch.load(model_path)
    loaded_model = HallucinationProbe(
        input_dim=checkpoint['input_dim'],
        layer_sizes=CONFIG["LAYER_SIZES"],
        dropout_rate=CONFIG["DROPOUT_RATE"]
    ).to(CONFIG["DEVICE"])
    loaded_model.load_state_dict(checkpoint['model_state_dict'])
    logger.info("Model loaded successfully!")

    # Evaluate on train set
    logger.info("\nEvaluating on train set...")
    train_metrics, y_train_true, train_probs = evaluate_model(loaded_model, X_train, y_train, dataset_name="Train")

    # Evaluate on test set
    logger.info("\nEvaluating on test set...")
    test_metrics, y_test_true, test_probs = evaluate_model(loaded_model, X_test, y_test, dataset_name="Test")

    # Plot confusion matrices
    plot_confusion_matrix(np.array(train_metrics['confusion_matrix']),
                         np.array(test_metrics['confusion_matrix']))

    # Plot ROC curves
    plot_roc_curve(y_train_true, train_probs, y_test_true, test_probs)

    # Calculate overall dataset statistics
    total_class_0 = int((labels == 0).sum())
    total_class_1 = int((labels == 1).sum())

    # Save comprehensive results
    results = {
        'model_name': CONFIG["MODEL_NAME"],
        'embedding_type': CONFIG["EMBEDDING_TYPE"],
        'layer_name': CONFIG["LAYER_NAME"],
        'target_column': CONFIG["TARGET_COLUMN"],
        'input_dim': input_dim,
        'timestamp': timestamp,

        # Dataset statistics
        'dataset_statistics': {
            'total_samples': len(labels),
            'num_no_hallucination': total_class_0,
            'num_hallucination': total_class_1,
            'hallucination_percentage': float(total_class_1 / len(labels) * 100)
        },

        # Train set results
        'train_set': {
            'num_samples': len(X_train),
            'accuracy': train_metrics['accuracy'],
            'precision': train_metrics['precision'],
            'recall': train_metrics['recall'],
            'f1': train_metrics['f1'],
            'auroc': train_metrics['auroc'],
            'confusion_matrix': train_metrics['confusion_matrix'],
            'num_no_hallucination': train_metrics['num_class_0'],
            'num_hallucination': train_metrics['num_class_1']
        },

        # Test set results
        'test_set': {
            'num_samples': len(X_test),
            'accuracy': test_metrics['accuracy'],
            'precision': test_metrics['precision'],
            'recall': test_metrics['recall'],
            'f1': test_metrics['f1'],
            'auroc': test_metrics['auroc'],
            'confusion_matrix': test_metrics['confusion_matrix'],
            'num_no_hallucination': test_metrics['num_class_0'],
            'num_hallucination': test_metrics['num_class_1']
        },

        # Training history
        'training_history': history,

        # Configuration
        'config': CONFIG
    }

    results_path = os.path.join(CONFIG["OUTPUT_DIR"], 'results.json')
    with open(results_path, 'w') as f:
        json.dump(results, f, indent=2)
    logger.info(f"\nResults saved: {results_path}")

    logger.info("\n" + "=" * 80)
    logger.info("TRAINING AND EVALUATION COMPLETED SUCCESSFULLY!")
    logger.info("=" * 80)

if __name__ == "__main__":
    main()
