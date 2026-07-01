"""
Analyze Probe Performance by Category
======================================
This script analyzes probe performance broken down by question categories.

For a given trained probe:
1. Recreates the exact same train/test split used during training (random_state=42)
2. Loads the saved model checkpoint
3. Gets predictions on the test set
4. Merges with category metadata from sampled_10k_relational_dataset.csv
5. Calculates AUROC scores per category, per source dataset, and overall

Usage:
    python analyze_probe_by_category.py
"""

import os
import h5py
import pandas as pd
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score
import json
import logging
from datetime import datetime
import glob
from tqdm import tqdm

# ==================== CONFIGURATION ====================

CONFIG = {
    # Model configuration (must match training)
    "MODEL_NAME": "SmolVLM2-2.2B",
    "EMBEDDING_TYPE": "query_token_representation",
    "LAYER_NAME": "layer_18",

    # Data paths
    "H5_DIR": "/root/akhil/HALP_EACL_Models/Models/Smol_VL/smolvlm_output",
    "CSV_PATH": "/root/akhil/FInal_CSV_Hallucination/smolvlm_manually_reviewed.csv",
    "CATEGORY_CSV_PATH": "/root/akhil/final_data/sampled_10k_relational_dataset.csv",

    # Model checkpoint path
    "MODEL_CHECKPOINT": "/root/akhil/probe_training_scripts/smolvlm_model_probe/results/query_token_layer18/probe_model.pt",

    # Output directory
    "OUTPUT_DIR": "/root/akhil/probe_analysis/results/smolvlm_query_token_layer18",

    # Training parameters (must match training for consistent split)
    "TARGET_COLUMN": "is_hallucinating_manual",
    "TEST_SIZE": 0.2,
    "RANDOM_STATE": 42,

    # Model architecture (must match training)
    "LAYER_SIZES": [512, 256, 128],
    "DROPOUT_RATE": 0.3,

    # Device
    "DEVICE": "cuda" if torch.cuda.is_available() else "cpu"
}

# ==================== SETUP ====================

os.makedirs(CONFIG["OUTPUT_DIR"], exist_ok=True)

# Setup logging
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
log_file = os.path.join(CONFIG["OUTPUT_DIR"], f'analysis_{timestamp}.log')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ==================== PATH VERIFICATION ====================

def verify_paths():
    """Verify all required paths exist before proceeding."""
    logger.info("=" * 80)
    logger.info("VERIFYING PATHS")
    logger.info("=" * 80)

    paths_to_check = {
        "H5 Directory": CONFIG["H5_DIR"],
        "Hallucination CSV": CONFIG["CSV_PATH"],
        "Category CSV": CONFIG["CATEGORY_CSV_PATH"],
        "Model Checkpoint": CONFIG["MODEL_CHECKPOINT"]
    }

    all_valid = True
    for name, path in paths_to_check.items():
        exists = os.path.exists(path)
        status = "✓" if exists else "✗"
        logger.info(f"{status} {name}: {path}")
        if not exists:
            all_valid = False

    if not all_valid:
        raise FileNotFoundError("Some required paths do not exist. Please check configuration.")

    logger.info("\n✓ All paths verified successfully!\n")

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

def load_category_metadata(category_csv_path):
    """Load category metadata from sampled_10k_relational_dataset.csv."""
    logger.info(f"Loading category metadata from: {category_csv_path}")
    df = pd.read_csv(category_csv_path, low_memory=False)

    # Create mapping from question_id to category and source
    category_map = {}
    for _, row in df.iterrows():
        question_id = row['question_id']
        category_map[question_id] = {
            'category': row.get('category', 'Unknown'),
            'source_dataset': row.get('dataset', 'Unknown')  # Column is 'dataset' not 'source_dataset'
        }

    logger.info(f"Loaded category metadata for {len(category_map)} questions")

    # Print summary statistics
    categories = [v['category'] for v in category_map.values()]
    sources = [v['source_dataset'] for v in category_map.values()]

    logger.info(f"  Unique categories: {len(set(categories))}")
    logger.info(f"  Unique source datasets: {len(set(sources))}")

    return category_map

def load_embeddings_from_h5(h5_dir, embedding_type, labels_dict, layer_name=None):
    """
    Load embeddings from H5 files.

    Returns embeddings, labels, and question_ids in the same order.
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
                        # Direct access: vision_only_representation
                        if embedding_type in sample_group:
                            embedding = sample_group[embedding_type][:]

                            embeddings_list.append(embedding)
                            labels_list.append(labels_dict[question_id]['label'])
                            question_ids.append(question_id)

                except Exception as e:
                    logger.warning(f"Error loading {question_id}: {e}")
                    continue

    if len(embeddings_list) == 0:
        raise ValueError(f"No embeddings found for {embedding_type}" + (f"/{layer_name}" if layer_name else ""))

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

# ==================== INFERENCE ====================

def get_predictions(model, X_data):
    """Get probability predictions from model."""
    model.eval()

    dataset = EmbeddingDataset(X_data, np.zeros(len(X_data)))  # Dummy labels
    data_loader = DataLoader(dataset, batch_size=32, shuffle=False)

    all_probs = []

    with torch.no_grad():
        for X_batch, _ in data_loader:
            X_batch = X_batch.to(CONFIG["DEVICE"])
            outputs = model(X_batch).cpu().numpy()
            all_probs.extend(outputs)

    return np.array(all_probs)

# ==================== CATEGORY ANALYSIS ====================

def analyze_by_category(test_question_ids, y_test, test_probs, category_map):
    """Analyze AUROC scores by category."""
    logger.info("\n" + "=" * 80)
    logger.info("ANALYZING BY CATEGORY")
    logger.info("=" * 80)

    # Create DataFrame for analysis
    df = pd.DataFrame({
        'question_id': test_question_ids,
        'true_label': y_test,
        'predicted_prob': test_probs
    })

    # Add category and source metadata
    df['category'] = df['question_id'].map(lambda qid: category_map.get(qid, {}).get('category', 'Unknown'))
    df['source_dataset'] = df['question_id'].map(lambda qid: category_map.get(qid, {}).get('source_dataset', 'Unknown'))

    # Calculate overall AUROC (should match training results)
    overall_auroc = roc_auc_score(df['true_label'], df['predicted_prob'])
    logger.info(f"\n✓ Overall Test AUROC: {overall_auroc:.4f}")

    # Calculate AUROC per category
    logger.info("\nCalculating AUROC per category...")
    category_results = []

    for category in sorted(df['category'].unique()):
        if category == 'Unknown':
            continue

        cat_df = df[df['category'] == category]

        # Need at least 2 samples and both classes for AUROC
        if len(cat_df) < 2:
            continue

        if len(cat_df['true_label'].unique()) < 2:
            # Only one class present
            category_results.append({
                'category': category,
                'num_samples': len(cat_df),
                'num_hallucination': int(cat_df['true_label'].sum()),
                'num_no_hallucination': int((cat_df['true_label'] == 0).sum()),
                'auroc': None,
                'note': 'Single class only'
            })
        else:
            auroc = roc_auc_score(cat_df['true_label'], cat_df['predicted_prob'])
            category_results.append({
                'category': category,
                'num_samples': len(cat_df),
                'num_hallucination': int(cat_df['true_label'].sum()),
                'num_no_hallucination': int((cat_df['true_label'] == 0).sum()),
                'auroc': float(auroc),
                'note': ''
            })

    category_df = pd.DataFrame(category_results)
    category_df = category_df.sort_values('auroc', ascending=False, na_position='last')

    # Save category results
    category_csv_path = os.path.join(CONFIG["OUTPUT_DIR"], 'category_auroc.csv')
    category_df.to_csv(category_csv_path, index=False)
    logger.info(f"\n✓ Category AUROC saved to: {category_csv_path}")

    # Print top/bottom categories
    logger.info("\n" + "=" * 80)
    logger.info("TOP 10 CATEGORIES BY AUROC")
    logger.info("=" * 80)
    valid_categories = category_df[category_df['auroc'].notna()]
    if len(valid_categories) > 0:
        for idx, row in valid_categories.head(10).iterrows():
            logger.info(f"{row['category']:40s} | AUROC: {row['auroc']:.4f} | Samples: {row['num_samples']:4d}")

    logger.info("\n" + "=" * 80)
    logger.info("BOTTOM 10 CATEGORIES BY AUROC")
    logger.info("=" * 80)
    if len(valid_categories) > 0:
        for idx, row in valid_categories.tail(10).iterrows():
            logger.info(f"{row['category']:40s} | AUROC: {row['auroc']:.4f} | Samples: {row['num_samples']:4d}")

    return category_df, overall_auroc

def analyze_by_source(test_question_ids, y_test, test_probs, category_map):
    """Analyze AUROC scores by source dataset."""
    logger.info("\n" + "=" * 80)
    logger.info("ANALYZING BY SOURCE DATASET")
    logger.info("=" * 80)

    # Create DataFrame for analysis
    df = pd.DataFrame({
        'question_id': test_question_ids,
        'true_label': y_test,
        'predicted_prob': test_probs
    })

    # Add source metadata
    df['source_dataset'] = df['question_id'].map(lambda qid: category_map.get(qid, {}).get('source_dataset', 'Unknown'))

    # Calculate AUROC per source
    source_results = []

    for source in sorted(df['source_dataset'].unique()):
        if source == 'Unknown':
            continue

        src_df = df[df['source_dataset'] == source]

        # Need at least 2 samples and both classes for AUROC
        if len(src_df) < 2:
            continue

        if len(src_df['true_label'].unique()) < 2:
            # Only one class present
            source_results.append({
                'source_dataset': source,
                'num_samples': len(src_df),
                'num_hallucination': int(src_df['true_label'].sum()),
                'num_no_hallucination': int((src_df['true_label'] == 0).sum()),
                'auroc': None,
                'note': 'Single class only'
            })
        else:
            auroc = roc_auc_score(src_df['true_label'], src_df['predicted_prob'])
            source_results.append({
                'source_dataset': source,
                'num_samples': len(src_df),
                'num_hallucination': int(src_df['true_label'].sum()),
                'num_no_hallucination': int((src_df['true_label'] == 0).sum()),
                'auroc': float(auroc),
                'note': ''
            })

    source_df = pd.DataFrame(source_results)

    # Only sort if we have results with AUROC
    if len(source_df) > 0 and 'auroc' in source_df.columns:
        source_df = source_df.sort_values('auroc', ascending=False, na_position='last')

    # Save source results
    source_csv_path = os.path.join(CONFIG["OUTPUT_DIR"], 'source_auroc.csv')
    source_df.to_csv(source_csv_path, index=False)
    logger.info(f"\n✓ Source dataset AUROC saved to: {source_csv_path}")

    # Print results
    logger.info("\n" + "=" * 80)
    logger.info("AUROC BY SOURCE DATASET")
    logger.info("=" * 80)
    if len(source_df) > 0:
        for idx, row in source_df.iterrows():
            if pd.notna(row['auroc']):
                logger.info(f"{row['source_dataset']:20s} | AUROC: {row['auroc']:.4f} | Samples: {row['num_samples']:4d}")
            else:
                logger.info(f"{row['source_dataset']:20s} | AUROC: N/A (single class) | Samples: {row['num_samples']:4d}")
    else:
        logger.info("No source datasets found with sufficient data")

    return source_df

# ==================== REPORT GENERATION ====================

def generate_markdown_report(category_df, source_df, overall_auroc):
    """Generate a human-readable markdown report."""
    report_path = os.path.join(CONFIG["OUTPUT_DIR"], 'analysis_report.md')

    with open(report_path, 'w') as f:
        f.write(f"# Probe Performance Analysis by Category\n\n")
        f.write(f"**Model:** {CONFIG['MODEL_NAME']}\n")
        f.write(f"**Embedding Type:** {CONFIG['EMBEDDING_TYPE']} / {CONFIG['LAYER_NAME']}\n")
        f.write(f"**Analysis Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(f"---\n\n")

        f.write(f"## Overall Performance\n\n")
        f.write(f"**Test AUROC:** {overall_auroc:.4f}\n\n")

        f.write(f"---\n\n")
        f.write(f"## Performance by Source Dataset\n\n")
        f.write(f"| Source Dataset | AUROC | Samples | Hallucination | No Hallucination |\n")
        f.write(f"|----------------|-------|---------|---------------|------------------|\n")
        for idx, row in source_df.iterrows():
            auroc_str = f"{row['auroc']:.4f}" if pd.notna(row['auroc']) else "N/A"
            f.write(f"| {row['source_dataset']} | {auroc_str} | {row['num_samples']} | {row['num_hallucination']} | {row['num_no_hallucination']} |\n")

        f.write(f"\n---\n\n")
        f.write(f"## Performance by Category (Top 20)\n\n")
        f.write(f"| Category | AUROC | Samples | Hallucination | No Hallucination |\n")
        f.write(f"|----------|-------|---------|---------------|------------------|\n")
        valid_categories = category_df[category_df['auroc'].notna()].head(20)
        for idx, row in valid_categories.iterrows():
            f.write(f"| {row['category']} | {row['auroc']:.4f} | {row['num_samples']} | {row['num_hallucination']} | {row['num_no_hallucination']} |\n")

        f.write(f"\n---\n\n")
        f.write(f"## Performance by Category (Bottom 20)\n\n")
        f.write(f"| Category | AUROC | Samples | Hallucination | No Hallucination |\n")
        f.write(f"|----------|-------|---------|---------------|------------------|\n")
        valid_categories = category_df[category_df['auroc'].notna()].tail(20)
        for idx, row in valid_categories.iterrows():
            f.write(f"| {row['category']} | {row['auroc']:.4f} | {row['num_samples']} | {row['num_hallucination']} | {row['num_no_hallucination']} |\n")

        f.write(f"\n---\n\n")
        f.write(f"## Categories with Single Class (No AUROC)\n\n")
        single_class = category_df[category_df['auroc'].isna()]
        if len(single_class) > 0:
            f.write(f"| Category | Samples | Note |\n")
            f.write(f"|----------|---------|------|\n")
            for idx, row in single_class.iterrows():
                f.write(f"| {row['category']} | {row['num_samples']} | {row['note']} |\n")
        else:
            f.write(f"*No categories with single class.*\n")

    logger.info(f"\n✓ Markdown report saved to: {report_path}")

# ==================== MAIN ====================

def main():
    """Main analysis pipeline."""
    logger.info("=" * 80)
    logger.info(f"PROBE CATEGORY ANALYSIS")
    logger.info(f"{CONFIG['MODEL_NAME']} - {CONFIG['EMBEDDING_TYPE']} / {CONFIG['LAYER_NAME']}")
    logger.info("=" * 80)
    logger.info(f"Model checkpoint: {CONFIG['MODEL_CHECKPOINT']}")
    logger.info(f"Output directory: {CONFIG['OUTPUT_DIR']}")
    logger.info("")

    # Verify all paths exist
    verify_paths()

    # Load labels
    labels_dict = load_hallucination_labels(CONFIG["CSV_PATH"])

    # Load category metadata
    category_map = load_category_metadata(CONFIG["CATEGORY_CSV_PATH"])

    # Load embeddings (this will give us the same data as training)
    embeddings, labels, question_ids = load_embeddings_from_h5(
        CONFIG["H5_DIR"],
        CONFIG["EMBEDDING_TYPE"],
        labels_dict,
        layer_name=CONFIG["LAYER_NAME"]
    )

    logger.info(f"\nTotal samples loaded: {len(embeddings)}")
    logger.info(f"Question IDs matched with categories: {len([qid for qid in question_ids if qid in category_map])}/{len(question_ids)}")

    # Create the EXACT same train/test split as training
    logger.info("\n" + "=" * 80)
    logger.info("CREATING TRAIN/TEST SPLIT (matching training configuration)")
    logger.info("=" * 80)
    logger.info(f"Random state: {CONFIG['RANDOM_STATE']}")
    logger.info(f"Test size: {CONFIG['TEST_SIZE']}")

    # Split both embeddings and question_ids in the same way
    X_train, X_test, y_train, y_test, train_ids, test_ids = train_test_split(
        embeddings, labels, question_ids,
        test_size=CONFIG["TEST_SIZE"],
        random_state=CONFIG["RANDOM_STATE"],
        stratify=labels
    )

    logger.info(f"\n✓ Split created:")
    logger.info(f"  Train: {len(X_train)} samples")
    logger.info(f"  Test:  {len(X_test)} samples")
    logger.info(f"  Test class distribution: 0={int((y_test==0).sum())}, 1={int((y_test==1).sum())}")

    # Load the saved model
    logger.info("\n" + "=" * 80)
    logger.info("LOADING SAVED MODEL")
    logger.info("=" * 80)
    logger.info(f"Checkpoint: {CONFIG['MODEL_CHECKPOINT']}")

    checkpoint = torch.load(CONFIG['MODEL_CHECKPOINT'], map_location=CONFIG['DEVICE'])

    input_dim = checkpoint['input_dim']
    logger.info(f"Input dimension: {input_dim}")

    model = HallucinationProbe(
        input_dim=input_dim,
        layer_sizes=CONFIG["LAYER_SIZES"],
        dropout_rate=CONFIG["DROPOUT_RATE"]
    ).to(CONFIG["DEVICE"])

    model.load_state_dict(checkpoint['model_state_dict'])
    logger.info("✓ Model loaded successfully!")

    # Get predictions on test set
    logger.info("\n" + "=" * 80)
    logger.info("GETTING PREDICTIONS ON TEST SET")
    logger.info("=" * 80)

    test_probs = get_predictions(model, X_test)
    logger.info(f"✓ Generated {len(test_probs)} predictions")

    # Analyze by category
    category_df, overall_auroc = analyze_by_category(test_ids, y_test, test_probs, category_map)

    # Analyze by source dataset
    source_df = analyze_by_source(test_ids, y_test, test_probs, category_map)

    # Generate markdown report
    generate_markdown_report(category_df, source_df, overall_auroc)

    # Save summary JSON
    summary = {
        'model_name': CONFIG['MODEL_NAME'],
        'embedding_type': CONFIG['EMBEDDING_TYPE'],
        'layer_name': CONFIG['LAYER_NAME'],
        'timestamp': timestamp,
        'overall_auroc': float(overall_auroc),
        'test_samples': len(X_test),
        'num_categories_analyzed': len(category_df),
        'num_sources_analyzed': len(source_df),
        'checkpoint_path': CONFIG['MODEL_CHECKPOINT']
    }

    summary_path = os.path.join(CONFIG["OUTPUT_DIR"], 'analysis_summary.json')
    with open(summary_path, 'w') as f:
        json.dump(summary, f, indent=2)
    logger.info(f"\n✓ Summary saved to: {summary_path}")

    logger.info("\n" + "=" * 80)
    logger.info("ANALYSIS COMPLETED SUCCESSFULLY!")
    logger.info("=" * 80)
    logger.info(f"\nResults saved to: {CONFIG['OUTPUT_DIR']}")
    logger.info(f"  - category_auroc.csv")
    logger.info(f"  - source_auroc.csv")
    logger.info(f"  - analysis_report.md")
    logger.info(f"  - analysis_summary.json")

if __name__ == "__main__":
    main()
