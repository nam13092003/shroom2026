"""
Detailed Hallucination Type Analysis
=====================================
Analyzes probe performance by:
- basic_hallucination_type (Object-Related, Relationship, Attribute-Related, Other)
- domain_type (Attribute Recognition, Visual Understanding, Spatial Reasoning, etc.)
- answer_type (Yes/No, Open-Ended, Unanswerable, Number, Selection)

For each probe, calculates:
- Test AUROC per type
- Sample count per type
- Class distribution per type
"""

import os
import sys
import torch
import pandas as pd
import numpy as np
from datetime import datetime
import logging
import json

sys.path.insert(0, '/root/akhil/probe_analysis')

from analyze_probe_by_category import (
    load_hallucination_labels,
    load_embeddings_from_h5,
    HallucinationProbe,
    get_predictions
)

from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score

# Setup logging
log_file = f'/root/akhil/detailed_probe_analysis/analysis_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Configuration
DETAILED_CSV = "/root/akhil/final_data/sampled_10k_with_hallucination_types.csv"
CONFIG_PARAMS = {
    "TEST_SIZE": 0.2,
    "RANDOM_STATE": 42,
    "LAYER_SIZES": [512, 256, 128],
    "DROPOUT_RATE": 0.3,
    "DEVICE": "cuda" if torch.cuda.is_available() else "cpu"
}

# Analysis columns
ANALYSIS_COLUMNS = {
    'basic_hallucination_type': 'Basic Hallucination Type',
    'domain_type': 'Domain Type',
    'answer_type': 'Answer Type'
}

def load_detailed_metadata(csv_path):
    """Load detailed hallucination type metadata."""
    logger.info(f"Loading detailed metadata from: {csv_path}")
    df = pd.read_csv(csv_path, low_memory=False)

    metadata_map = {}
    for _, row in df.iterrows():
        question_id = row['question_id']
        metadata_map[question_id] = {
            'basic_hallucination_type': row.get('basic_hallucination_type', 'Unknown'),
            'domain_type': row.get('domain_type', 'Unknown'),
            'answer_type': row.get('answer_type', 'Unknown')
        }

    logger.info(f"Loaded metadata for {len(metadata_map)} questions")

    # Print distributions
    for col in ANALYSIS_COLUMNS.keys():
        values = [v[col] for v in metadata_map.values()]
        unique_count = len(set(values))
        logger.info(f"  {col}: {unique_count} unique values")

    return metadata_map

def analyze_by_type(test_question_ids, y_test, test_probs, metadata_map, column_name, column_label):
    """Analyze AUROC scores by a specific type column."""
    logger.info(f"\n{'='*80}")
    logger.info(f"ANALYZING BY {column_label.upper()}")
    logger.info(f"{'='*80}")

    # Create DataFrame
    df = pd.DataFrame({
        'question_id': test_question_ids,
        'true_label': y_test,
        'predicted_prob': test_probs
    })

    # Add type metadata
    df['type_value'] = df['question_id'].map(lambda qid: metadata_map.get(qid, {}).get(column_name, 'Unknown'))

    # Calculate overall AUROC
    overall_auroc = roc_auc_score(df['true_label'], df['predicted_prob'])
    logger.info(f"\n✓ Overall Test AUROC: {overall_auroc:.4f}")

    # Calculate AUROC per type
    logger.info(f"\nCalculating AUROC per {column_label}...")
    type_results = []

    for type_value in sorted(df['type_value'].unique()):
        if type_value == 'Unknown':
            continue

        type_df = df[df['type_value'] == type_value]

        # Need at least 2 samples and both classes
        if len(type_df) < 2:
            continue

        if len(type_df['true_label'].unique()) < 2:
            # Only one class
            type_results.append({
                'type': type_value,
                'num_samples': len(type_df),
                'num_hallucination': int(type_df['true_label'].sum()),
                'num_no_hallucination': int((type_df['true_label'] == 0).sum()),
                'auroc': None,
                'note': 'Single class only'
            })
        else:
            auroc = roc_auc_score(type_df['true_label'], type_df['predicted_prob'])
            type_results.append({
                'type': type_value,
                'num_samples': len(type_df),
                'num_hallucination': int(type_df['true_label'].sum()),
                'num_no_hallucination': int((type_df['true_label'] == 0).sum()),
                'auroc': float(auroc),
                'note': ''
            })

    type_df_result = pd.DataFrame(type_results)

    # Sort by AUROC
    if len(type_df_result) > 0 and 'auroc' in type_df_result.columns:
        type_df_result = type_df_result.sort_values('auroc', ascending=False, na_position='last')

    # Print results
    logger.info(f"\n{'='*80}")
    logger.info(f"RESULTS BY {column_label.upper()}")
    logger.info(f"{'='*80}")

    for idx, row in type_df_result.iterrows():
        if pd.notna(row['auroc']):
            logger.info(f"{row['type']:40s} | AUROC: {row['auroc']:.4f} | Samples: {row['num_samples']:4d} | Hall: {row['num_hallucination']:3d} | No-Hall: {row['num_no_hallucination']:4d}")
        else:
            logger.info(f"{row['type']:40s} | AUROC: N/A (single class) | Samples: {row['num_samples']:4d}")

    return type_df_result, overall_auroc

def generate_detailed_report(results_dict, overall_auroc, output_dir, probe_name):
    """Generate comprehensive markdown report."""
    report_path = os.path.join(output_dir, 'detailed_analysis_report.md')

    with open(report_path, 'w') as f:
        f.write(f"# Detailed Hallucination Type Analysis\n\n")
        f.write(f"**Probe:** {probe_name}\n")
        f.write(f"**Analysis Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(f"---\n\n")

        f.write(f"## Overall Performance\n\n")
        f.write(f"**Test AUROC:** {overall_auroc:.4f}\n\n")
        f.write(f"---\n\n")

        # For each analysis type
        for col_name, col_label in ANALYSIS_COLUMNS.items():
            if col_name in results_dict:
                df = results_dict[col_name]

                f.write(f"## Performance by {col_label}\n\n")
                f.write(f"| {col_label} | AUROC | Samples | Hallucination | No Hallucination |\n")
                f.write(f"|{'-'*40}|-------|---------|---------------|------------------|\n")

                for idx, row in df.iterrows():
                    auroc_str = f"{row['auroc']:.4f}" if pd.notna(row['auroc']) else "N/A"
                    f.write(f"| {row['type']} | {auroc_str} | {row['num_samples']} | {row['num_hallucination']} | {row['num_no_hallucination']} |\n")

                f.write(f"\n---\n\n")

    logger.info(f"✓ Detailed report saved to: {report_path}")

def run_detailed_analysis(model_config, probe_info, output_dir):
    """Run detailed analysis for a single probe."""
    probe_name = f"{model_config['name']}/{probe_info['probe_dir']}"

    logger.info(f"\n{'='*80}")
    logger.info(f"DETAILED ANALYSIS: {probe_name}")
    logger.info(f"{'='*80}")

    try:
        # Load labels
        labels_dict = load_hallucination_labels(model_config["csv_path"])

        # Load detailed metadata
        metadata_map = load_detailed_metadata(DETAILED_CSV)

        # Load embeddings
        embeddings, labels, question_ids = load_embeddings_from_h5(
            model_config["h5_dir"],
            probe_info['embedding_type'],
            labels_dict,
            layer_name=probe_info['layer_name']
        )

        logger.info(f"Loaded {len(embeddings)} samples")

        # Create train/test split (same as original)
        X_train, X_test, y_train, y_test, train_ids, test_ids = train_test_split(
            embeddings, labels, question_ids,
            test_size=CONFIG_PARAMS["TEST_SIZE"],
            random_state=CONFIG_PARAMS["RANDOM_STATE"],
            stratify=labels
        )

        logger.info(f"Split: Train={len(X_train)}, Test={len(X_test)}")

        # Load model
        checkpoint = torch.load(probe_info['checkpoint_path'], map_location=CONFIG_PARAMS["DEVICE"])

        # Handle different checkpoint formats
        if isinstance(checkpoint, dict) and 'input_dim' in checkpoint:
            # Gemma format: full checkpoint with metadata
            input_dim = checkpoint['input_dim']
            state_dict = checkpoint['model_state_dict']
        else:
            # Llama/Phi format: just state_dict, get input_dim from embeddings or probe_info
            state_dict = checkpoint
            # Get input_dim from the embeddings shape
            input_dim = X_train.shape[1]

        model = HallucinationProbe(
            input_dim=input_dim,
            layer_sizes=CONFIG_PARAMS["LAYER_SIZES"],
            dropout_rate=CONFIG_PARAMS["DROPOUT_RATE"]
        ).to(CONFIG_PARAMS["DEVICE"])

        model.load_state_dict(state_dict)
        logger.info(f"Model loaded (input_dim={input_dim})")

        # Get predictions
        test_probs = get_predictions(model, X_test)
        logger.info(f"Generated {len(test_probs)} predictions")

        # Analyze by each type
        results_dict = {}
        overall_auroc = None

        for col_name, col_label in ANALYSIS_COLUMNS.items():
            type_df, auroc = analyze_by_type(test_ids, y_test, test_probs, metadata_map, col_name, col_label)
            results_dict[col_name] = type_df

            # Save individual CSV
            csv_path = os.path.join(output_dir, f'{col_name}_auroc.csv')
            type_df.to_csv(csv_path, index=False)
            logger.info(f"✓ Saved to: {csv_path}")

            if overall_auroc is None:
                overall_auroc = auroc

        # Generate comprehensive report
        generate_detailed_report(results_dict, overall_auroc, output_dir, probe_name)

        # Save summary JSON
        summary = {
            'probe_name': probe_name,
            'model': model_config['name'],
            'probe_dir': probe_info['probe_dir'],
            'embedding_type': probe_info['embedding_type'],
            'layer_name': probe_info['layer_name'],
            'overall_auroc': float(overall_auroc),
            'test_samples': len(X_test),
            'analysis_types': list(ANALYSIS_COLUMNS.keys()),
            'timestamp': datetime.now().strftime("%Y%m%d_%H%M%S")
        }

        summary_path = os.path.join(output_dir, 'detailed_summary.json')
        with open(summary_path, 'w') as f:
            json.dump(summary, f, indent=2)

        logger.info(f"\n✓ SUCCESS: {probe_name}")
        logger.info(f"  Overall AUROC: {overall_auroc:.4f}")
        logger.info(f"  Output: {output_dir}")

        return overall_auroc, "Success"

    except Exception as e:
        logger.error(f"✗ FAILED: {probe_name} - {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return None, str(e)

def main():
    """Run detailed analysis for a specific probe (example: SmolVLM Layer 18)."""
    logger.info("="*80)
    logger.info("DETAILED HALLUCINATION TYPE ANALYSIS")
    logger.info("="*80)

    # Example: Analyze SmolVLM Query Token Layer 18 (best performing probe)
    model_config = {
        "name": "SmolVLM2-2.2B",
        "h5_dir": "/root/akhil/HALP_EACL_Models/Models/Smol_VL/smolvlm_output",
        "csv_path": "/root/akhil/FInal_CSV_Hallucination/smolvlm_manually_reviewed.csv",
    }

    probe_info = {
        "probe_dir": "query_token_layer18",
        "embedding_type": "query_token_representation",
        "layer_name": "layer_18",
        "checkpoint_path": "/root/akhil/probe_training_scripts/smolvlm_model_probe/results/query_token_layer18/probe_model.pt"
    }

    output_dir = "/root/akhil/detailed_probe_analysis/results/smolvlm_query_token_layer18"
    os.makedirs(output_dir, exist_ok=True)

    auroc, status = run_detailed_analysis(model_config, probe_info, output_dir)

    if status == "Success":
        logger.info(f"\n{'='*80}")
        logger.info("ANALYSIS COMPLETE")
        logger.info(f"{'='*80}")
        logger.info(f"\nResults saved to: {output_dir}")
        logger.info(f"\nFiles created:")
        logger.info(f"  - basic_hallucination_type_auroc.csv")
        logger.info(f"  - domain_type_auroc.csv")
        logger.info(f"  - answer_type_auroc.csv")
        logger.info(f"  - detailed_analysis_report.md")
        logger.info(f"  - detailed_summary.json")

if __name__ == "__main__":
    main()
