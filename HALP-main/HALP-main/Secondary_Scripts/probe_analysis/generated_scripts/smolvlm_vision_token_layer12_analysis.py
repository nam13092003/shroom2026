"""
Category Analysis for SmolVLM2-2.2B - vision_token_layer12
Auto-generated analysis script
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

# Configuration
CONFIG = {
    "MODEL_NAME": "SmolVLM2-2.2B",
    "EMBEDDING_TYPE": "vision_token_representation",
    "LAYER_NAME": "layer_12",

    "H5_DIR": "/root/akhil/HALP_EACL_Models/Models/Smol_VL/smolvlm_output",
    "CSV_PATH": "/root/akhil/FInal_CSV_Hallucination/smolvlm_manually_reviewed.csv",
    "CATEGORY_CSV_PATH": "/root/akhil/final_data/sampled_10k_relational_dataset.csv",

    "MODEL_CHECKPOINT": "/root/akhil/probe_training_scripts/smolvlm_model_probe/results/vision_token_layer12/probe_model.pt",
    "OUTPUT_DIR": "/root/akhil/probe_analysis/results/smolvlm/vision_token_layer12",

    "TARGET_COLUMN": "is_hallucinating_manual",
    "TEST_SIZE": 0.2,
    "RANDOM_STATE": 42,

    "LAYER_SIZES": [512, 256, 128],
    "DROPOUT_RATE": 0.3,

    "DEVICE": "cuda" if torch.cuda.is_available() else "cpu"
}

# Setup logging
os.makedirs(CONFIG["OUTPUT_DIR"], exist_ok=True)
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

# Import the core functions from the main analysis script
import sys
sys.path.insert(0, '/root/akhil/probe_analysis')

from analyze_probe_by_category import (
    load_hallucination_labels,
    load_category_metadata,
    load_embeddings_from_h5,
    HallucinationProbe,
    get_predictions,
    analyze_by_category,
    analyze_by_source,
    generate_markdown_report,
    EmbeddingDataset
)

def verify_paths():
    """Verify all required paths exist."""
    logger.info("=" * 80)
    logger.info("VERIFYING PATHS")
    logger.info("=" * 80)

    paths = {
        "H5 Directory": CONFIG["H5_DIR"],
        "Hallucination CSV": CONFIG["CSV_PATH"],
        "Category CSV": CONFIG["CATEGORY_CSV_PATH"],
        "Model Checkpoint": CONFIG["MODEL_CHECKPOINT"]
    }

    all_valid = True
    for name, path in paths.items():
        exists = os.path.exists(path)
        status = "✓" if exists else "✗"
        logger.info(f"{status} {name}: {path}")
        if not exists:
            all_valid = False

    if not all_valid:
        raise FileNotFoundError("Some required paths do not exist.")

    logger.info("\n✓ All paths verified!\n")

def main():
    logger.info("=" * 80)
    logger.info(f"PROBE CATEGORY ANALYSIS")
    logger.info(f"{CONFIG['MODEL_NAME']} - {CONFIG['EMBEDDING_TYPE']}" + (f" / {CONFIG['LAYER_NAME']}" if CONFIG['LAYER_NAME'] else ""))
    logger.info("=" * 80)

    verify_paths()

    # Load data
    labels_dict = load_hallucination_labels(CONFIG["CSV_PATH"])
    category_map = load_category_metadata(CONFIG["CATEGORY_CSV_PATH"])

    embeddings, labels, question_ids = load_embeddings_from_h5(
        CONFIG["H5_DIR"],
        CONFIG["EMBEDDING_TYPE"],
        labels_dict,
        layer_name=CONFIG["LAYER_NAME"]
    )

    logger.info(f"\nTotal samples: {len(embeddings)}")
    logger.info(f"Matched with categories: {len([qid for qid in question_ids if qid in category_map])}/{len(question_ids)}")

    # Create train/test split
    logger.info("\n" + "=" * 80)
    logger.info("CREATING TRAIN/TEST SPLIT")
    logger.info("=" * 80)

    X_train, X_test, y_train, y_test, train_ids, test_ids = train_test_split(
        embeddings, labels, question_ids,
        test_size=CONFIG["TEST_SIZE"],
        random_state=CONFIG["RANDOM_STATE"],
        stratify=labels
    )

    logger.info(f"Train: {len(X_train)}, Test: {len(X_test)}")

    # Load model
    logger.info("\n" + "=" * 80)
    logger.info("LOADING MODEL")
    logger.info("=" * 80)

    checkpoint = torch.load(CONFIG["MODEL_CHECKPOINT"], map_location=CONFIG["DEVICE"])
    input_dim = checkpoint['input_dim']

    model = HallucinationProbe(
        input_dim=input_dim,
        layer_sizes=CONFIG["LAYER_SIZES"],
        dropout_rate=CONFIG["DROPOUT_RATE"]
    ).to(CONFIG["DEVICE"])

    model.load_state_dict(checkpoint['model_state_dict'])
    logger.info("✓ Model loaded!")

    # Get predictions
    logger.info("\n" + "=" * 80)
    logger.info("GETTING PREDICTIONS")
    logger.info("=" * 80)

    test_probs = get_predictions(model, X_test)
    logger.info(f"✓ Generated {len(test_probs)} predictions")

    # Analyze
    category_df, overall_auroc = analyze_by_category(test_ids, y_test, test_probs, category_map)
    source_df = analyze_by_source(test_ids, y_test, test_probs, category_map)
    generate_markdown_report(category_df, source_df, overall_auroc)

    # Save summary
    summary = {
        'model_name': CONFIG['MODEL_NAME'],
        'embedding_type': CONFIG['EMBEDDING_TYPE'],
        'layer_name': CONFIG['LAYER_NAME'],
        'timestamp': timestamp,
        'overall_auroc': float(overall_auroc),
        'test_samples': len(X_test)
    }

    with open(os.path.join(CONFIG["OUTPUT_DIR"], 'analysis_summary.json'), 'w') as f:
        json.dump(summary, f, indent=2)

    logger.info("\n" + "=" * 80)
    logger.info("ANALYSIS COMPLETED!")
    logger.info("=" * 80)

    return overall_auroc

if __name__ == "__main__":
    main()
