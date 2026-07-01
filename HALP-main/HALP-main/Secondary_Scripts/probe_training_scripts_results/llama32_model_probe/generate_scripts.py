#!/usr/bin/env python3
"""Generate all 11 probe training scripts for Llama-3.2-11B-Vision"""

import os

# Model configuration
MODEL_NAME = "Llama-3.2-11B-Vision"
H5_DIR = "/root/akhil/HALP_EACL_Models/Models/LLama_32/llama_output"
CSV_PATH = "/root/akhil/FInal_CSV_Hallucination/llama32_manually_reviewed.csv"
VISION_DIM = 7680
LANGUAGE_DIM = 4096
LAYERS = [0, 10, 20, 30, 39]  # Available layers in H5 files

# Script template
SCRIPT_TEMPLATE = '''#!/usr/bin/env python3
"""
Probe Training Script for {MODEL_NAME}
Embedding Type: {EMBEDDING_TYPE}
Layer: {LAYER_DISPLAY}
"""

import os
import sys
import json
import logging
import numpy as np
import pandas as pd
import h5py
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix
import matplotlib.pyplot as plt
from pathlib import Path
from tqdm import tqdm
from datetime import datetime

# ==================== CONFIGURATION ====================

CONFIG = {{
    "H5_DIR": "{H5_DIR}",
    "CSV_PATH": "{CSV_PATH}",
    "OUTPUT_DIR": "{OUTPUT_DIR}",
    "MODEL_NAME": "{MODEL_NAME}",
    "EMBEDDING_TYPE": "{EMBEDDING_TYPE}",
    "LAYER_NAME": {LAYER_NAME_STR},
    "TARGET_COLUMN": "is_hallucinating_manual",
    "LAYER_SIZES": [512, 256, 128],
    "DROPOUT_RATE": 0.3,
    "LEARNING_RATE": 0.001,
    "BATCH_SIZE": 32,
    "EPOCHS": 50,
    "TEST_SIZE": 0.2,
    "RANDOM_STATE": 42,
    "DEVICE": "cuda" if torch.cuda.is_available() else "cpu"
}}

# ==================== SETUP LOGGING ====================

os.makedirs(CONFIG["OUTPUT_DIR"], exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(CONFIG["OUTPUT_DIR"], "training.log")),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# ==================== DATA LOADING ====================

def load_labels(csv_path, target_column):
    """Load labels from CSV file."""
    logger.info(f"Loading labels from: {{csv_path}}")
    df = pd.read_csv(csv_path)

    # Create labels dictionary
    labels_dict = {{}}
    for _, row in df.iterrows():
        question_id = row['question_id']
        label = 1 if row[target_column] else 0
        labels_dict[question_id] = {{
            'label': label,
            'question': row.get('question', ''),
            'answer': row.get('model_answer', '')
        }}

    logger.info(f"Loaded {{len(labels_dict)}} labels")
    return labels_dict

def load_embeddings_from_h5(h5_dir, embedding_type, labels_dict, layer_name=None):
    """
    Load embeddings from H5 files.

    Args:
        h5_dir: Directory containing H5 files
        embedding_type: Type of embedding ('vision_only_representation', 'vision_token_representation', 'query_token_representation')
        labels_dict: Dictionary mapping question_id to labels
        layer_name: Layer name (e.g., 'layer_0', 'layer_10', etc.) for token representations
    """
    h5_files = sorted(Path(h5_dir).glob("*.h5"))
    logger.info(f"Loading embeddings: {{embedding_type}}" + (f" / {{layer_name}}" if layer_name else ""))
    logger.info(f"Found {{len(h5_files)}} H5 files")

    embeddings_list = []
    labels_list = []
    question_ids = []

    for h5_file in tqdm(h5_files, desc="Processing H5 files"):
        with h5py.File(h5_file, 'r') as f:
            for question_id in f.keys():
                if question_id not in labels_dict:
                    continue

                try:
                    sample_group = f[question_id]

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
                                logger.warning(f"Missing {{layer_name}} in {{embedding_type}} for {{question_id}}")
                        else:
                            logger.warning(f"Missing {{embedding_type}} for {{question_id}}")
                    else:
                        # Direct access: vision_only_representation
                        if embedding_type in sample_group:
                            embedding = sample_group[embedding_type][:]

                            embeddings_list.append(embedding)
                            labels_list.append(labels_dict[question_id]['label'])
                            question_ids.append(question_id)
                        else:
                            logger.warning(f"Missing {{embedding_type}} for {{question_id}}")

                except Exception as e:
                    logger.warning(f"Error loading {{question_id}}: {{e}}")
                    continue

    if len(embeddings_list) == 0:
        raise ValueError(f"No embeddings found for {{embedding_type}}" + (f"/{{layer_name}}" if layer_name else ""))

    # Handle variable-size embeddings (for vision_only_representation in some models)
    # Check if all embeddings have the same shape
    shapes = [emb.shape for emb in embeddings_list]
    if len(set(shapes)) > 1:
        # Variable shapes detected - pad to max length
        max_len = max(emb.shape[0] for emb in embeddings_list)
        logger.info(f"Variable embedding shapes detected. Padding to max length: {{max_len}}")
        padded_embeddings = []
        for emb in embeddings_list:
            if len(emb.shape) == 1:  # 1D embeddings
                padded = np.zeros(max_len, dtype=emb.dtype)
                padded[:len(emb)] = emb
                padded_embeddings.append(padded)
            else:
                raise ValueError(f"Unexpected embedding shape: {{emb.shape}}")
        embeddings = np.stack(padded_embeddings)
    else:
        embeddings = np.stack(embeddings_list)

    labels = np.array(labels_list)

    logger.info(f"Loaded {{len(embeddings)}} samples")
    logger.info(f"Embedding shape: {{embeddings.shape}}")
    logger.info(f"Label distribution - Class 0: {{(labels==0).sum()}}, Class 1: {{(labels==1).sum()}}")

    return embeddings, labels, question_ids

# ==================== PYTORCH DATASET ====================

class EmbeddingDataset(Dataset):
    """PyTorch dataset for embeddings."""

    def __init__(self, embeddings, labels):
        self.embeddings = torch.tensor(embeddings, dtype=torch.float32)
        self.labels = torch.tensor(labels, dtype=torch.float32)

    def __len__(self):
        return len(self.embeddings)

    def __getitem__(self, idx):
        return self.embeddings[idx], self.labels[idx]

# ==================== PROBE MODEL ====================

class HallucinationProbe(nn.Module):
    """
    Multi-layer feedforward probe for hallucination detection.
    Architecture: input_dim -> 512 -> 256 -> 128 -> 1
    """

    def __init__(self, input_dim, layer_sizes=[512, 256, 128], dropout_rate=0.3):
        super(HallucinationProbe, self).__init__()

        layers = []
        prev_size = input_dim

        for size in layer_sizes:
            layers.extend([
                nn.Linear(prev_size, size),
                nn.BatchNorm1d(size),
                nn.ReLU(),
                nn.Dropout(dropout_rate)
            ])
            prev_size = size

        # Output layer
        layers.append(nn.Linear(prev_size, 1))
        layers.append(nn.Sigmoid())

        self.network = nn.Sequential(*layers)

    def forward(self, x):
        return self.network(x)

# ==================== TRAINING ====================

def train_epoch(model, dataloader, criterion, optimizer, device):
    """Train for one epoch."""
    model.train()
    total_loss = 0
    all_preds = []
    all_labels = []

    for embeddings, labels in dataloader:
        embeddings = embeddings.to(device)
        labels = labels.to(device)

        optimizer.zero_grad()
        outputs = model(embeddings).squeeze()
        loss = criterion(outputs, labels)

        loss.backward()
        optimizer.step()

        total_loss += loss.item()

        preds = (outputs > 0.5).float()
        all_preds.extend(preds.cpu().numpy())
        all_labels.extend(labels.cpu().numpy())

    avg_loss = total_loss / len(dataloader)
    accuracy = accuracy_score(all_labels, all_preds)

    return avg_loss, accuracy

def evaluate(model, dataloader, device):
    """Evaluate model."""
    model.eval()
    all_preds = []
    all_probs = []
    all_labels = []

    with torch.no_grad():
        for embeddings, labels in dataloader:
            embeddings = embeddings.to(device)
            labels = labels.to(device)

            outputs = model(embeddings).squeeze()

            all_probs.extend(outputs.cpu().numpy())
            preds = (outputs > 0.5).float()
            all_preds.extend(preds.cpu().numpy())
            all_labels.extend(labels.cpu().numpy())

    metrics = {{
        'accuracy': accuracy_score(all_labels, all_preds),
        'precision': precision_score(all_labels, all_preds, zero_division=0),
        'recall': recall_score(all_labels, all_preds, zero_division=0),
        'f1': f1_score(all_labels, all_preds, zero_division=0),
        'auroc': roc_auc_score(all_labels, all_probs),
        'confusion_matrix': confusion_matrix(all_labels, all_preds).tolist(),
        'predictions': all_preds,
        'probabilities': all_probs,
        'labels': all_labels
    }}

    return metrics

# ==================== VISUALIZATION ====================

def plot_training_history(history, output_dir):
    """Plot training history."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))

    # Loss plot
    ax1.plot(history['train_loss'], label='Train Loss')
    ax1.set_xlabel('Epoch')
    ax1.set_ylabel('Loss')
    ax1.set_title('Training Loss')
    ax1.legend()
    ax1.grid(True)

    # Accuracy plot
    ax2.plot(history['train_acc'], label='Train Accuracy')
    ax2.set_xlabel('Epoch')
    ax2.set_ylabel('Accuracy')
    ax2.set_title('Training Accuracy')
    ax2.legend()
    ax2.grid(True)

    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'training_history.png'), dpi=150, bbox_inches='tight')
    plt.close()

def plot_confusion_matrices(train_cm, test_cm, output_dir):
    """Plot confusion matrices."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

    # Train confusion matrix
    im1 = ax1.imshow(train_cm, cmap='Blues')
    ax1.set_title('Train Confusion Matrix')
    ax1.set_xlabel('Predicted')
    ax1.set_ylabel('Actual')
    ax1.set_xticks([0, 1])
    ax1.set_yticks([0, 1])
    ax1.set_xticklabels(['No Hallucination', 'Hallucination'])
    ax1.set_yticklabels(['No Hallucination', 'Hallucination'])

    for i in range(2):
        for j in range(2):
            text = ax1.text(j, i, train_cm[i][j], ha="center", va="center", color="black")

    plt.colorbar(im1, ax=ax1)

    # Test confusion matrix
    im2 = ax2.imshow(test_cm, cmap='Blues')
    ax2.set_title('Test Confusion Matrix')
    ax2.set_xlabel('Predicted')
    ax2.set_ylabel('Actual')
    ax2.set_xticks([0, 1])
    ax2.set_yticks([0, 1])
    ax2.set_xticklabels(['No Hallucination', 'Hallucination'])
    ax2.set_yticklabels(['No Hallucination', 'Hallucination'])

    for i in range(2):
        for j in range(2):
            text = ax2.text(j, i, test_cm[i][j], ha="center", va="center", color="black")

    plt.colorbar(im2, ax=ax2)

    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'confusion_matrices.png'), dpi=150, bbox_inches='tight')
    plt.close()

def plot_roc_curves(train_metrics, test_metrics, output_dir):
    """Plot ROC curves."""
    from sklearn.metrics import roc_curve

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

    # Train ROC
    fpr, tpr, _ = roc_curve(train_metrics['labels'], train_metrics['probabilities'])
    ax1.plot(fpr, tpr, label=f"AUROC = {{train_metrics['auroc']:.4f}}")
    ax1.plot([0, 1], [0, 1], 'k--', label='Random')
    ax1.set_xlabel('False Positive Rate')
    ax1.set_ylabel('True Positive Rate')
    ax1.set_title('Train ROC Curve')
    ax1.legend()
    ax1.grid(True)

    # Test ROC
    fpr, tpr, _ = roc_curve(test_metrics['labels'], test_metrics['probabilities'])
    ax2.plot(fpr, tpr, label=f"AUROC = {{test_metrics['auroc']:.4f}}")
    ax2.plot([0, 1], [0, 1], 'k--', label='Random')
    ax2.set_xlabel('False Positive Rate')
    ax2.set_ylabel('True Positive Rate')
    ax2.set_title('Test ROC Curve')
    ax2.legend()
    ax2.grid(True)

    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'roc_curves.png'), dpi=150, bbox_inches='tight')
    plt.close()

# ==================== MAIN ====================

def main():
    """Main training and evaluation pipeline."""

    # Print configuration
    logger.info("="*80)
    logger.info(f"{{CONFIG['MODEL_NAME']}} - {{CONFIG['EMBEDDING_TYPE']}}" + (f"/{{CONFIG['LAYER_NAME']}}" if CONFIG['LAYER_NAME'] else "") + " Probe Training")
    logger.info("="*80)
    logger.info(f"Target: {{CONFIG['TARGET_COLUMN']}}")
    logger.info(f"Output directory: {{CONFIG['OUTPUT_DIR']}}")
    logger.info("")

    # Load labels
    labels_dict = load_labels(CONFIG["CSV_PATH"], CONFIG["TARGET_COLUMN"])

    # Load embeddings
    embeddings, labels, question_ids = load_embeddings_from_h5(
        CONFIG["H5_DIR"],
        CONFIG["EMBEDDING_TYPE"],
        labels_dict,
        layer_name=CONFIG["LAYER_NAME"]
    )

    # Get input dimension
    input_dim = embeddings.shape[1]
    logger.info(f"Input dimension: {{input_dim}}")

    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        embeddings, labels,
        test_size=CONFIG["TEST_SIZE"],
        random_state=CONFIG["RANDOM_STATE"],
        stratify=labels
    )

    # Dataset statistics
    logger.info("")
    logger.info("Data splits:")
    logger.info(f"  Train: {{len(X_train)}} samples ({{len(X_train)/len(embeddings)*100:.0f}}%)")
    logger.info(f"  Test:  {{len(X_test)}} samples ({{len(X_test)/len(embeddings)*100:.0f}}%)")
    logger.info("")
    logger.info("Class distribution:")
    logger.info(f"  Train set:")
    logger.info(f"    Class 0 (No Hallucination): {{(y_train==0).sum()}} ({{(y_train==0).sum()/len(y_train)*100:.1f}}%)")
    logger.info(f"    Class 1 (Hallucination):    {{(y_train==1).sum()}} ({{(y_train==1).sum()/len(y_train)*100:.1f}}%)")
    logger.info(f"  Test set:")
    logger.info(f"    Class 0 (No Hallucination): {{(y_test==0).sum()}} ({{(y_test==0).sum()/len(y_test)*100:.1f}}%)")
    logger.info(f"    Class 1 (Hallucination):    {{(y_test==1).sum()}} ({{(y_test==1).sum()/len(y_test)*100:.1f}}%)")
    logger.info("")

    # Create datasets and dataloaders
    train_dataset = EmbeddingDataset(X_train, y_train)
    test_dataset = EmbeddingDataset(X_test, y_test)

    train_loader = DataLoader(train_dataset, batch_size=CONFIG["BATCH_SIZE"], shuffle=True)
    test_loader = DataLoader(test_dataset, batch_size=CONFIG["BATCH_SIZE"], shuffle=False)

    # Initialize model
    device = torch.device(CONFIG["DEVICE"])
    model = HallucinationProbe(
        input_dim=input_dim,
        layer_sizes=CONFIG["LAYER_SIZES"],
        dropout_rate=CONFIG["DROPOUT_RATE"]
    ).to(device)

    criterion = nn.BCELoss()
    optimizer = optim.Adam(model.parameters(), lr=CONFIG["LEARNING_RATE"])

    # Training
    logger.info("="*80)
    logger.info("TRAINING PHASE")
    logger.info("="*80)
    logger.info(f"Starting training...")
    logger.info(f"Device: {{device}}")
    logger.info(f"Train samples: {{len(train_dataset)}}")
    logger.info(f"Architecture: {{input_dim}} -> {{' -> '.join(map(str, CONFIG['LAYER_SIZES']))}} -> 1")

    history = {{
        'train_loss': [],
        'train_acc': []
    }}

    for epoch in range(CONFIG["EPOCHS"]):
        train_loss, train_acc = train_epoch(model, train_loader, criterion, optimizer, device)

        history['train_loss'].append(train_loss)
        history['train_acc'].append(train_acc)

        if (epoch + 1) % 10 == 0:
            logger.info(f"Epoch {{epoch+1}}/{{CONFIG['EPOCHS']}}: Train Loss: {{train_loss:.4f}}, Train Acc: {{train_acc:.4f}}")

    logger.info("Training completed!")

    # Save model
    model_path = os.path.join(CONFIG["OUTPUT_DIR"], "probe_model.pt")
    torch.save(model.state_dict(), model_path)
    logger.info(f"\\nModel saved: {{model_path}}")

    # Plot training history
    plot_training_history(history, CONFIG["OUTPUT_DIR"])
    logger.info("Training history plot saved")

    # Evaluation
    logger.info("")
    logger.info("="*80)
    logger.info("EVALUATION PHASE")
    logger.info("="*80)
    logger.info("Loading saved model...")
    model.load_state_dict(torch.load(model_path))
    logger.info("Model loaded successfully!")

    logger.info("\\nEvaluating on train set...")
    train_metrics = evaluate(model, train_loader, device)

    logger.info("="*60)
    logger.info("TRAIN METRICS:")
    logger.info(f"  Accuracy:  {{train_metrics['accuracy']:.4f}}")
    logger.info(f"  Precision: {{train_metrics['precision']:.4f}}")
    logger.info(f"  Recall:    {{train_metrics['recall']:.4f}}")
    logger.info(f"  F1 Score:  {{train_metrics['f1']:.4f}}")
    logger.info(f"  AUROC:     {{train_metrics['auroc']:.4f}}")
    logger.info("="*60)

    logger.info("\\nEvaluating on test set...")
    test_metrics = evaluate(model, test_loader, device)

    logger.info("="*60)
    logger.info("TEST METRICS:")
    logger.info(f"  Accuracy:  {{test_metrics['accuracy']:.4f}}")
    logger.info(f"  Precision: {{test_metrics['precision']:.4f}}")
    logger.info(f"  Recall:    {{test_metrics['recall']:.4f}}")
    logger.info(f"  F1 Score:  {{test_metrics['f1']:.4f}}")
    logger.info(f"  AUROC:     {{test_metrics['auroc']:.4f}}")
    logger.info("="*60)

    # Plot confusion matrices
    plot_confusion_matrices(
        train_metrics['confusion_matrix'],
        test_metrics['confusion_matrix'],
        CONFIG["OUTPUT_DIR"]
    )
    logger.info("Confusion matrices saved")

    # Plot ROC curves
    plot_roc_curves(train_metrics, test_metrics, CONFIG["OUTPUT_DIR"])
    logger.info("ROC curves saved")

    # Save results
    results = {{
        "model_name": CONFIG["MODEL_NAME"],
        "embedding_type": CONFIG["EMBEDDING_TYPE"],
        "layer_name": CONFIG["LAYER_NAME"],
        "target_column": CONFIG["TARGET_COLUMN"],
        "input_dim": input_dim,
        "timestamp": datetime.now().strftime("%Y%m%d_%H%M%S"),
        "dataset_statistics": {{
            "total_samples": len(embeddings),
            "num_no_hallucination": int((labels == 0).sum()),
            "num_hallucination": int((labels == 1).sum()),
            "hallucination_percentage": float((labels == 1).sum() / len(labels) * 100)
        }},
        "train_set": {{
            "num_samples": len(X_train),
            "accuracy": train_metrics['accuracy'],
            "precision": train_metrics['precision'],
            "recall": train_metrics['recall'],
            "f1": train_metrics['f1'],
            "auroc": train_metrics['auroc'],
            "confusion_matrix": train_metrics['confusion_matrix'],
            "num_no_hallucination": int((y_train == 0).sum()),
            "num_hallucination": int((y_train == 1).sum())
        }},
        "test_set": {{
            "num_samples": len(X_test),
            "accuracy": test_metrics['accuracy'],
            "precision": test_metrics['precision'],
            "recall": test_metrics['recall'],
            "f1": test_metrics['f1'],
            "auroc": test_metrics['auroc'],
            "confusion_matrix": test_metrics['confusion_matrix'],
            "num_no_hallucination": int((y_test == 0).sum()),
            "num_hallucination": int((y_test == 1).sum())
        }},
        "training_history": history,
        "config": CONFIG
    }}

    results_path = os.path.join(CONFIG["OUTPUT_DIR"], "results.json")
    with open(results_path, 'w') as f:
        json.dump(results, f, indent=2)

    logger.info(f"\\nResults saved: {{results_path}}")
    logger.info("")
    logger.info("="*80)
    logger.info("TRAINING AND EVALUATION COMPLETED SUCCESSFULLY!")
    logger.info("="*80)

if __name__ == "__main__":
    main()
'''

# Define all 11 probe configurations
probe_configs = [
    # Vision only
    {
        "filename": "01_vision_only_probe.py",
        "embedding_type": "vision_only_representation",
        "layer_name": None,
        "layer_display": "None",
        "output_subdir": "vision_only"
    },
    # Vision token representations (5 layers)
    {
        "filename": "02_vision_token_layer0_probe.py",
        "embedding_type": "vision_token_representation",
        "layer_name": "layer_0",
        "layer_display": "layer_0",
        "output_subdir": "vision_token_layer0"
    },
    {
        "filename": "03_vision_token_layer10_probe.py",
        "embedding_type": "vision_token_representation",
        "layer_name": "layer_10",
        "layer_display": "layer_10",
        "output_subdir": "vision_token_layer10"
    },
    {
        "filename": "04_vision_token_layer20_probe.py",
        "embedding_type": "vision_token_representation",
        "layer_name": "layer_20",
        "layer_display": "layer_20",
        "output_subdir": "vision_token_layer20"
    },
    {
        "filename": "05_vision_token_layer30_probe.py",
        "embedding_type": "vision_token_representation",
        "layer_name": "layer_30",
        "layer_display": "layer_30",
        "output_subdir": "vision_token_layer30"
    },
    {
        "filename": "06_vision_token_layer39_probe.py",
        "embedding_type": "vision_token_representation",
        "layer_name": "layer_39",
        "layer_display": "layer_39",
        "output_subdir": "vision_token_layer39"
    },
    # Query token representations (5 layers)
    {
        "filename": "07_query_token_layer0_probe.py",
        "embedding_type": "query_token_representation",
        "layer_name": "layer_0",
        "layer_display": "layer_0",
        "output_subdir": "query_token_layer0"
    },
    {
        "filename": "08_query_token_layer10_probe.py",
        "embedding_type": "query_token_representation",
        "layer_name": "layer_10",
        "layer_display": "layer_10",
        "output_subdir": "query_token_layer10"
    },
    {
        "filename": "09_query_token_layer20_probe.py",
        "embedding_type": "query_token_representation",
        "layer_name": "layer_20",
        "layer_display": "layer_20",
        "output_subdir": "query_token_layer20"
    },
    {
        "filename": "10_query_token_layer30_probe.py",
        "embedding_type": "query_token_representation",
        "layer_name": "layer_30",
        "layer_display": "layer_30",
        "output_subdir": "query_token_layer30"
    },
    {
        "filename": "11_query_token_layer39_probe.py",
        "embedding_type": "query_token_representation",
        "layer_name": "layer_39",
        "layer_display": "layer_39",
        "output_subdir": "query_token_layer39"
    }
]

# Generate all scripts
output_dir_base = "/root/akhil/probe_training_scripts/llama32_model_probe"

for config in probe_configs:
    output_dir = os.path.join(output_dir_base, "results", config["output_subdir"])

    layer_name_str = f'"{config["layer_name"]}"' if config["layer_name"] else "None"

    script_content = SCRIPT_TEMPLATE.format(
        MODEL_NAME=MODEL_NAME,
        H5_DIR=H5_DIR,
        CSV_PATH=CSV_PATH,
        OUTPUT_DIR=output_dir,
        EMBEDDING_TYPE=config["embedding_type"],
        LAYER_NAME_STR=layer_name_str,
        LAYER_DISPLAY=config["layer_display"]
    )

    script_path = os.path.join(output_dir_base, config["filename"])
    with open(script_path, 'w') as f:
        f.write(script_content)

    os.chmod(script_path, 0o755)
    print(f"Created: {config['filename']}")

print(f"\nAll 11 probe training scripts generated in {output_dir_base}")
