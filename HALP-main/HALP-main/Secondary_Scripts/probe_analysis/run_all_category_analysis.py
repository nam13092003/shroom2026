"""
Run Category Analysis for All Models and Probes
================================================
Analyzes all trained probes across all models for category-level performance.
"""

import os
import sys
import subprocess
import pandas as pd
from datetime import datetime
import logging

# Add probe_analysis to path
sys.path.insert(0, '/root/akhil/probe_analysis')

from analyze_probe_by_category import (
    load_hallucination_labels,
    load_category_metadata,
    load_embeddings_from_h5,
    HallucinationProbe,
    get_predictions,
    analyze_by_category,
    analyze_by_source,
    generate_markdown_report
)

import torch
import numpy as np
from sklearn.model_selection import train_test_split
import json

# Setup logging
log_file = f'/root/akhil/probe_analysis/all_models_analysis_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Model configurations with ACTUAL paths
MODEL_CONFIGS = [
    {
        "name": "Gemma3-12B",
        "h5_dir": "/root/akhil/HALP_EACL_Models/Models/Gemma3_12B/gemma_output",
        "csv_path": "/root/akhil/FInal_CSV_Hallucination/gemma3_manually_reviewed.csv",
        "probe_base": "/root/akhil/probe_training_scripts/gemma_model_probe/results",
        "output_base": "/root/akhil/probe_analysis/results/gemma3",
        "probe_dirs": [
            ("vision_only_representation", None, "vision_only"),
            ("vision_token_representation", "layer_0", "vision_token_layer0"),
            ("vision_token_representation", "layer_n_4", "vision_token_layer_n_4"),
            ("vision_token_representation", "layer_n_2", "vision_token_layer_n_2"),
            ("vision_token_representation", "layer_3n_4", "vision_token_layer_3n_4"),
            ("vision_token_representation", "layer_n", "vision_token_layer_n"),
            ("query_token_representation", "layer_0", "query_token_layer0"),
            ("query_token_representation", "layer_n_4", "query_token_layer_n_4"),
            ("query_token_representation", "layer_n_2", "query_token_layer_n_2"),
            ("query_token_representation", "layer_3n_4", "query_token_layer_3n_4"),
            ("query_token_representation", "layer_n", "query_token_layer_n"),
        ]
    },
    {
        "name": "FastVLM-7B",
        "h5_dir": "/root/akhil/HALP_EACL_Models/Models/FastVLM_model/fastvlm_output",
        "csv_path": "/root/akhil/FInal_CSV_Hallucination/fastvlm_manually_reviewed.csv",
        "probe_base": "/root/akhil/probe_training_scripts/fastvlm_model_probe/results",
        "output_base": "/root/akhil/probe_analysis/results/fastvlm",
        "probe_dirs": [
            ("vision_only_representation", None, "vision_only"),
            ("vision_token_representation", "layer_0", "vision_token_layer0"),
            ("vision_token_representation", "layer_n_4", "vision_token_layer_n_4"),
            ("vision_token_representation", "layer_n_2", "vision_token_layer_n_2"),
            ("vision_token_representation", "layer_3n_4", "vision_token_layer_3n_4"),
            ("vision_token_representation", "layer_n", "vision_token_layer_n"),
            ("query_token_representation", "layer_0", "query_token_layer0"),
            ("query_token_representation", "layer_n_4", "query_token_layer_n_4"),
            ("query_token_representation", "layer_n_2", "query_token_layer_n_2"),
            ("query_token_representation", "layer_3n_4", "query_token_layer_3n_4"),
            ("query_token_representation", "layer_n", "query_token_layer_n"),
        ]
    },
    {
        "name": "LLaVA-Next-8B",
        "h5_dir": "/root/akhil/HALP_EACL_Models/Models/LLaVa_model/llava_output",
        "csv_path": "/root/akhil/FInal_CSV_Hallucination/llava_next_manually_reviewed.csv",
        "probe_base": "/root/akhil/probe_training_scripts/llava_model_probe/results",
        "output_base": "/root/akhil/probe_analysis/results/llava_next",
        "probe_dirs": [
            ("vision_only_representation", None, "vision_only"),
            ("vision_token_representation", "layer_0", "vision_token_layer0"),
            ("vision_token_representation", "layer_n_4", "vision_token_layer_n_4"),
            ("vision_token_representation", "layer_n_2", "vision_token_layer_n_2"),
            ("vision_token_representation", "layer_3n_4", "vision_token_layer_3n_4"),
            ("vision_token_representation", "layer_n", "vision_token_layer_n"),
            ("query_token_representation", "layer_0", "query_token_layer0"),
            ("query_token_representation", "layer_n_4", "query_token_layer_n_4"),
            ("query_token_representation", "layer_n_2", "query_token_layer_n_2"),
            ("query_token_representation", "layer_3n_4", "query_token_layer_3n_4"),
            ("query_token_representation", "layer_n", "query_token_layer_n"),
        ]
    },
    {
        "name": "Molmo-V1",
        "h5_dir": "/root/akhil/HALP_EACL_Models/Models/Molmo_V1/molmo_output",
        "csv_path": "/root/akhil/FInal_CSV_Hallucination/molmo_manually_reviewed.csv",
        "probe_base": "/root/akhil/probe_training_scripts/molmo_model_probe/results",
        "output_base": "/root/akhil/probe_analysis/results/molmo",
        "probe_dirs": [
            ("vision_only_representation", None, "vision_only"),
            ("vision_token_representation", "layer_0", "vision_token_layer0"),
            ("vision_token_representation", "layer_n_4", "vision_token_layer_n_4"),
            ("vision_token_representation", "layer_n_2", "vision_token_layer_n_2"),
            ("vision_token_representation", "layer_3n_4", "vision_token_layer_3n_4"),
            ("vision_token_representation", "layer_n", "vision_token_layer_n"),
            ("query_token_representation", "layer_0", "query_token_layer0"),
            ("query_token_representation", "layer_n_4", "query_token_layer_n_4"),
            ("query_token_representation", "layer_n_2", "query_token_layer_n_2"),
            ("query_token_representation", "layer_3n_4", "query_token_layer_3n_4"),
            ("query_token_representation", "layer_n", "query_token_layer_n"),
        ]
    },
    {
        "name": "Qwen2.5-VL-7B",
        "h5_dir": "/root/akhil/HALP_EACL_Models/Models/Qwen25_VL/qwen25_output",
        "csv_path": "/root/akhil/FInal_CSV_Hallucination/qwen_manually_reviewed.csv",
        "probe_base": "/root/akhil/probe_training_scripts/qwen25vl_model_probe/results",
        "output_base": "/root/akhil/probe_analysis/results/qwen25vl",
        "probe_dirs": [
            ("vision_only_representation", None, "vision_only"),
            ("vision_token_representation", "layer_0", "vision_token_layer0"),
            ("vision_token_representation", "layer_n_4", "vision_token_layer_n_4"),
            ("vision_token_representation", "layer_n_2", "vision_token_layer_n_2"),
            ("vision_token_representation", "layer_3n_4", "vision_token_layer_3n_4"),
            ("vision_token_representation", "layer_n", "vision_token_layer_n"),
            ("query_token_representation", "layer_0", "query_token_layer0"),
            ("query_token_representation", "layer_n_4", "query_token_layer_n_4"),
            ("query_token_representation", "layer_n_2", "query_token_layer_n_2"),
            ("query_token_representation", "layer_3n_4", "query_token_layer_3n_4"),
            ("query_token_representation", "layer_n", "query_token_layer_n"),
        ]
    },
    {
        "name": "Llama-3.2-11B-Vision",
        "h5_dir": "/root/akhil/HALP_EACL_Models/Models/LLama_32/llama_output",
        "csv_path": "/root/akhil/FInal_CSV_Hallucination/llama_manually_reviewed.csv",
        "probe_base": "/root/akhil/probe_training_scripts/llama32_model_probe/results",
        "output_base": "/root/akhil/probe_analysis/results/llama32",
        "probe_dirs": [
            ("vision_only_representation", None, "vision_only"),
            ("vision_token_representation", "layer_0", "vision_token_layer0"),
            ("vision_token_representation", "layer_n_4", "vision_token_layer_n_4"),
            ("vision_token_representation", "layer_n_2", "vision_token_layer_n_2"),
            ("vision_token_representation", "layer_3n_4", "vision_token_layer_3n_4"),
            ("vision_token_representation", "layer_n", "vision_token_layer_n"),
            ("query_token_representation", "layer_0", "query_token_layer0"),
            ("query_token_representation", "layer_n_4", "query_token_layer_n_4"),
            ("query_token_representation", "layer_n_2", "query_token_layer_n_2"),
            ("query_token_representation", "layer_3n_4", "query_token_layer_3n_4"),
            ("query_token_representation", "layer_n", "query_token_layer_n"),
        ]
    },
    {
        "name": "Phi4-VL",
        "h5_dir": "/root/akhil/HALP_EACL_Models/Models/Phi4_VL/phi4_output",
        "csv_path": "/root/akhil/FInal_CSV_Hallucination/phi4_manually_reviewed.csv",
        "probe_base": "/root/akhil/probe_training_scripts/phi4vl_model_probe/results",
        "output_base": "/root/akhil/probe_analysis/results/phi4vl",
        "probe_dirs": [
            ("vision_only_representation", None, "vision_only"),
            ("vision_token_representation", "layer_0", "vision_token_layer0"),
            ("vision_token_representation", "layer_n_4", "vision_token_layer_n_4"),
            ("vision_token_representation", "layer_n_2", "vision_token_layer_n_2"),
            ("vision_token_representation", "layer_3n_4", "vision_token_layer_3n_4"),
            ("vision_token_representation", "layer_n", "vision_token_layer_n"),
            ("query_token_representation", "layer_0", "query_token_layer0"),
            ("query_token_representation", "layer_n_4", "query_token_layer_n_4"),
            ("query_token_representation", "layer_n_2", "query_token_layer_n_2"),
            ("query_token_representation", "layer_3n_4", "query_token_layer_3n_4"),
            ("query_token_representation", "layer_n", "query_token_layer_n"),
        ]
    },
    {
        "name": "SmolVLM2-2.2B",
        "h5_dir": "/root/akhil/HALP_EACL_Models/Models/Smol_VL/smolvlm_output",
        "csv_path": "/root/akhil/FInal_CSV_Hallucination/smolvlm_manually_reviewed.csv",
        "probe_base": "/root/akhil/probe_training_scripts/smolvlm_model_probe/results",
        "output_base": "/root/akhil/probe_analysis/results/smolvlm",
        "probe_dirs": [
            ("vision_only_representation", None, "vision_only"),
            ("vision_token_representation", "layer_0", "vision_token_layer0"),
            ("vision_token_representation", "layer_6", "vision_token_layer6"),
            ("vision_token_representation", "layer_12", "vision_token_layer12"),
            ("vision_token_representation", "layer_18", "vision_token_layer18"),
            ("vision_token_representation", "layer_23", "vision_token_layer23"),
            ("query_token_representation", "layer_0", "query_token_layer0"),
            ("query_token_representation", "layer_6", "query_token_layer6"),
            ("query_token_representation", "layer_12", "query_token_layer12"),
            ("query_token_representation", "layer_18", "query_token_layer18"),
            ("query_token_representation", "layer_23", "query_token_layer23"),
        ]
    },
]

CATEGORY_CSV = "/root/akhil/final_data/sampled_10k_relational_dataset.csv"
CONFIG_PARAMS = {
    "TEST_SIZE": 0.2,
    "RANDOM_STATE": 42,
    "LAYER_SIZES": [512, 256, 128],
    "DROPOUT_RATE": 0.3,
    "DEVICE": "cuda" if torch.cuda.is_available() else "cpu"
}

def run_single_analysis(model_config, probe_config):
    """Run analysis for a single probe."""
    embedding_type, layer_name, probe_dir = probe_config

    checkpoint_path = os.path.join(model_config["probe_base"], probe_dir, "probe_model.pt")
    output_dir = os.path.join(model_config["output_base"], probe_dir)

    # Check if checkpoint exists
    if not os.path.exists(checkpoint_path):
        logger.warning(f"⚠ SKIP {model_config['name']}/{probe_dir}: Checkpoint not found")
        return None, "Checkpoint not found"

    # Check if already analyzed
    category_csv = os.path.join(output_dir, "category_auroc.csv")
    if os.path.exists(category_csv):
        logger.info(f"✓ SKIP {model_config['name']}/{probe_dir}: Already analyzed")
        # Read existing AUROC
        try:
            df = pd.read_csv(category_csv)
            # Calculate overall AUROC from saved results if available
            return None, "Already analyzed"
        except:
            pass

    os.makedirs(output_dir, exist_ok=True)

    probe_name = f"{model_config['name']}/{probe_dir}"
    logger.info(f"\n{'='*80}")
    logger.info(f"Running: {probe_name}")
    logger.info(f"{'='*80}")

    try:
        # Load labels
        labels_dict = load_hallucination_labels(model_config["csv_path"])
        category_map = load_category_metadata(CATEGORY_CSV)

        # Load embeddings
        embeddings, labels, question_ids = load_embeddings_from_h5(
            model_config["h5_dir"],
            embedding_type,
            labels_dict,
            layer_name=layer_name
        )

        logger.info(f"Loaded {len(embeddings)} samples")

        # Create train/test split (same as training)
        X_train, X_test, y_train, y_test, train_ids, test_ids = train_test_split(
            embeddings, labels, question_ids,
            test_size=CONFIG_PARAMS["TEST_SIZE"],
            random_state=CONFIG_PARAMS["RANDOM_STATE"],
            stratify=labels
        )

        logger.info(f"Split: Train={len(X_train)}, Test={len(X_test)}")

        # Load model
        checkpoint = torch.load(checkpoint_path, map_location=CONFIG_PARAMS["DEVICE"])
        input_dim = checkpoint['input_dim']

        model = HallucinationProbe(
            input_dim=input_dim,
            layer_sizes=CONFIG_PARAMS["LAYER_SIZES"],
            dropout_rate=CONFIG_PARAMS["DROPOUT_RATE"]
        ).to(CONFIG_PARAMS["DEVICE"])

        model.load_state_dict(checkpoint['model_state_dict'])
        logger.info(f"Model loaded (input_dim={input_dim})")

        # Get predictions
        test_probs = get_predictions(model, X_test)

        # Analyze by category and source
        category_df, overall_auroc = analyze_by_category(test_ids, y_test, test_probs, category_map)
        source_df = analyze_by_source(test_ids, y_test, test_probs, category_map)
        generate_markdown_report(category_df, source_df, overall_auroc)

        # Save summary
        summary = {
            'model_name': model_config['name'],
            'embedding_type': embedding_type,
            'layer_name': layer_name,
            'probe_dir': probe_dir,
            'overall_auroc': float(overall_auroc),
            'test_samples': len(X_test),
            'timestamp': datetime.now().strftime("%Y%m%d_%H%M%S")
        }

        with open(os.path.join(output_dir, 'analysis_summary.json'), 'w') as f:
            json.dump(summary, f, indent=2)

        logger.info(f"✓ SUCCESS: {probe_name} - AUROC: {overall_auroc:.4f}")
        return overall_auroc, "Success"

    except Exception as e:
        logger.error(f"✗ FAILED: {probe_name} - {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return None, str(e)

def main():
    logger.info("="*80)
    logger.info("CATEGORY ANALYSIS FOR ALL MODELS AND PROBES")
    logger.info("="*80)
    logger.info(f"Total models: {len(MODEL_CONFIGS)}")
    logger.info(f"Device: {CONFIG_PARAMS['DEVICE']}")
    logger.info("")

    results = []

    for model_config in MODEL_CONFIGS:
        logger.info(f"\n{'='*80}")
        logger.info(f"Processing: {model_config['name']}")
        logger.info(f"{'='*80}")
        logger.info(f"H5 Dir: {model_config['h5_dir']}")
        logger.info(f"Probes: {len(model_config['probe_dirs'])}")

        for probe_config in model_config['probe_dirs']:
            embedding_type, layer_name, probe_dir = probe_config

            auroc, status = run_single_analysis(model_config, probe_config)

            results.append({
                'model': model_config['name'],
                'embedding_type': embedding_type,
                'layer_name': layer_name if layer_name else 'N/A',
                'probe_dir': probe_dir,
                'auroc': auroc,
                'status': status
            })

    # Save summary
    results_df = pd.DataFrame(results)
    summary_path = "/root/akhil/probe_analysis/all_models_category_analysis_summary.csv"
    results_df.to_csv(summary_path, index=False)

    logger.info(f"\n{'='*80}")
    logger.info("BATCH ANALYSIS COMPLETE")
    logger.info(f"{'='*80}")
    logger.info(f"\nResults saved to: {summary_path}")

    # Print summary statistics
    total = len(results_df)
    success = len(results_df[results_df['status'] == 'Success'])
    already = len(results_df[results_df['status'] == 'Already analyzed'])
    failed = len(results_df[(results_df['status'] != 'Success') &
                            (results_df['status'] != 'Already analyzed') &
                            (results_df['status'] != 'Checkpoint not found')])
    skipped = len(results_df[results_df['status'] == 'Checkpoint not found'])

    logger.info(f"\nSummary:")
    logger.info(f"  Total: {total}")
    logger.info(f"  ✓ Success: {success}")
    logger.info(f"  ✓ Already analyzed: {already}")
    logger.info(f"  ✗ Failed: {failed}")
    logger.info(f"  ⚠ Skipped (no checkpoint): {skipped}")

    # Show results by model
    logger.info(f"\n{'='*80}")
    logger.info("RESULTS BY MODEL")
    logger.info(f"{'='*80}")

    for model_name in results_df['model'].unique():
        model_results = results_df[results_df['model'] == model_name]
        success_count = len(model_results[model_results['status'] == 'Success'])
        logger.info(f"\n{model_name}: {success_count}/{len(model_results)} successful")

        for _, row in model_results.iterrows():
            if row['auroc']:
                logger.info(f"  ✓ {row['probe_dir']:35s} AUROC: {row['auroc']:.4f}")
            elif row['status'] == 'Already analyzed':
                logger.info(f"  ✓ {row['probe_dir']:35s} (already analyzed)")
            elif row['status'] == 'Checkpoint not found':
                logger.info(f"  ⚠ {row['probe_dir']:35s} (no checkpoint)")
            else:
                logger.info(f"  ✗ {row['probe_dir']:35s} ({row['status']})")

if __name__ == "__main__":
    main()
