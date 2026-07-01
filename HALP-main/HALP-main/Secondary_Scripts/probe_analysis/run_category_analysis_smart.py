"""
Smart Category Analysis - Reads Layer Names from Checkpoints
=============================================================
Automatically discovers probes and reads correct layer names from checkpoint files.
"""

import os
import sys
import torch
import pandas as pd
from datetime import datetime
import logging
import glob

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

import numpy as np
from sklearn.model_selection import train_test_split
import json

# Setup logging
log_file = f'/root/akhil/probe_analysis/smart_analysis_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Model configurations
MODEL_CONFIGS = [
    {
        "name": "Gemma3-12B",
        "h5_dir": "/root/akhil/HALP_EACL_Models/Models/Gemma3_12B/gemma_output",
        "csv_path": "/root/akhil/FInal_CSV_Hallucination/gemma3_manually_reviewed.csv",
        "probe_base": "/root/akhil/probe_training_scripts/gemma_model_probe/results",
        "output_base": "/root/akhil/probe_analysis/results/gemma3",
    },
    {
        "name": "FastVLM-7B",
        "h5_dir": "/root/akhil/HALP_EACL_Models/Models/FastVLM_model/fastvlm_output",
        "csv_path": "/root/akhil/FInal_CSV_Hallucination/fastvlm_manually_reviewed.csv",
        "probe_base": "/root/akhil/probe_training_scripts/fastvlm_model_probe/results",
        "output_base": "/root/akhil/probe_analysis/results/fastvlm",
    },
    {
        "name": "LLaVA-Next-8B",
        "h5_dir": "/root/akhil/HALP_EACL_Models/Models/LLaVa_model/llava_output",
        "csv_path": "/root/akhil/FInal_CSV_Hallucination/llava_manually_reviewed.csv",
        "probe_base": "/root/akhil/probe_training_scripts/llava_model_probe/results",
        "output_base": "/root/akhil/probe_analysis/results/llava_next",
    },
    {
        "name": "Molmo-V1",
        "h5_dir": "/root/akhil/HALP_EACL_Models/Models/Molmo_V1/molmo_output",
        "csv_path": "/root/akhil/FInal_CSV_Hallucination/molmo_manually_reviewed.csv",
        "probe_base": "/root/akhil/probe_training_scripts/molmo_model_probe/results",
        "output_base": "/root/akhil/probe_analysis/results/molmo",
    },
    {
        "name": "Qwen2.5-VL-7B",
        "h5_dir": "/root/akhil/HALP_EACL_Models/Models/Qwen25_VL/qwen25_output",
        "csv_path": "/root/akhil/FInal_CSV_Hallucination/qwen25vl_manually_reviewed.csv",
        "probe_base": "/root/akhil/probe_training_scripts/qwen25vl_model_probe/results",
        "output_base": "/root/akhil/probe_analysis/results/qwen25vl",
    },
    {
        "name": "Llama-3.2-11B-Vision",
        "h5_dir": "/root/akhil/HALP_EACL_Models/Models/LLama_32/llama_output",
        "csv_path": "/root/akhil/FInal_CSV_Hallucination/llama_manually_reviewed.csv",
        "probe_base": "/root/akhil/probe_training_scripts/llama32_model_probe/results",
        "output_base": "/root/akhil/probe_analysis/results/llama32",
    },
    {
        "name": "Phi4-VL",
        "h5_dir": "/root/akhil/HALP_EACL_Models/Models/Phi4_VL/phi4_output",
        "csv_path": "/root/akhil/FInal_CSV_Hallucination/phi4_manually_reviewed.csv",
        "probe_base": "/root/akhil/probe_training_scripts/phi4vl_model_probe/results",
        "output_base": "/root/akhil/probe_analysis/results/phi4vl",
    },
    {
        "name": "SmolVLM2-2.2B",
        "h5_dir": "/root/akhil/HALP_EACL_Models/Models/Smol_VL/smolvlm_output",
        "csv_path": "/root/akhil/FInal_CSV_Hallucination/smolvlm_manually_reviewed.csv",
        "probe_base": "/root/akhil/probe_training_scripts/smolvlm_model_probe/results",
        "output_base": "/root/akhil/probe_analysis/results/smolvlm",
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

def discover_probes(probe_base):
    """Discover all trained probes by finding checkpoint files."""
    probes = []

    checkpoint_files = glob.glob(os.path.join(probe_base, "*/probe_model.pt"))

    for checkpoint_path in sorted(checkpoint_files):
        probe_dir = os.path.basename(os.path.dirname(checkpoint_path))

        try:
            # Load checkpoint to get actual configuration
            checkpoint = torch.load(checkpoint_path, map_location='cpu')
            config = checkpoint.get('config', {})

            embedding_type = config.get('EMBEDDING_TYPE')
            layer_name = config.get('LAYER_NAME')

            if embedding_type:
                probes.append({
                    'probe_dir': probe_dir,
                    'embedding_type': embedding_type,
                    'layer_name': layer_name,
                    'checkpoint_path': checkpoint_path
                })
        except Exception as e:
            logger.warning(f"Could not load checkpoint {checkpoint_path}: {e}")
            continue

    return probes

def run_single_analysis(model_config, probe_info):
    """Run analysis for a single probe."""
    probe_dir = probe_info['probe_dir']
    embedding_type = probe_info['embedding_type']
    layer_name = probe_info['layer_name']
    checkpoint_path = probe_info['checkpoint_path']

    output_dir = os.path.join(model_config["output_base"], probe_dir)

    # Check if already analyzed
    category_csv = os.path.join(output_dir, "category_auroc.csv")
    if os.path.exists(category_csv):
        logger.info(f"✓ SKIP {model_config['name']}/{probe_dir}: Already analyzed")
        return None, "Already analyzed"

    os.makedirs(output_dir, exist_ok=True)

    probe_name = f"{model_config['name']}/{probe_dir}"
    logger.info(f"\n{'='*80}")
    logger.info(f"Running: {probe_name}")
    logger.info(f"  Embedding: {embedding_type}")
    logger.info(f"  Layer: {layer_name if layer_name else 'N/A'}")
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

        # Create train/test split
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

        # Analyze
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
    logger.info("SMART CATEGORY ANALYSIS - ALL MODELS")
    logger.info("="*80)
    logger.info(f"Device: {CONFIG_PARAMS['DEVICE']}")
    logger.info("")

    results = []

    for model_config in MODEL_CONFIGS:
        logger.info(f"\n{'='*80}")
        logger.info(f"Processing: {model_config['name']}")
        logger.info(f"{'='*80}")
        logger.info(f"Probe base: {model_config['probe_base']}")

        # Discover all probes for this model
        probes = discover_probes(model_config['probe_base'])
        logger.info(f"Found {len(probes)} trained probes")

        for probe_info in probes:
            auroc, status = run_single_analysis(model_config, probe_info)

            results.append({
                'model': model_config['name'],
                'probe_dir': probe_info['probe_dir'],
                'embedding_type': probe_info['embedding_type'],
                'layer_name': probe_info['layer_name'] if probe_info['layer_name'] else 'N/A',
                'auroc': auroc,
                'status': status
            })

    # Save results
    results_df = pd.DataFrame(results)
    summary_path = "/root/akhil/probe_analysis/smart_analysis_summary.csv"
    results_df.to_csv(summary_path, index=False)

    logger.info(f"\n{'='*80}")
    logger.info("ANALYSIS COMPLETE")
    logger.info(f"{'='*80}")
    logger.info(f"\nResults: {summary_path}")

    # Summary statistics
    total = len(results_df)
    success = len(results_df[results_df['status'] == 'Success'])
    already = len(results_df[results_df['status'] == 'Already analyzed'])
    failed = total - success - already

    logger.info(f"\nSummary:")
    logger.info(f"  Total: {total}")
    logger.info(f"  ✓ Success: {success}")
    logger.info(f"  ✓ Already analyzed: {already}")
    logger.info(f"  ✗ Failed: {failed}")

    # Results by model
    logger.info(f"\n{'='*80}")
    logger.info("RESULTS BY MODEL")
    logger.info(f"{'='*80}")

    for model_name in results_df['model'].unique():
        model_results = results_df[results_df['model'] == model_name]
        success_count = len(model_results[model_results['status'].isin(['Success', 'Already analyzed'])])
        logger.info(f"\n{model_name}: {success_count}/{len(model_results)} completed")

        for _, row in model_results.iterrows():
            if row['auroc']:
                logger.info(f"  ✓ {row['probe_dir']:40s} AUROC: {row['auroc']:.4f}")
            elif row['status'] == 'Already analyzed':
                logger.info(f"  ✓ {row['probe_dir']:40s} (already done)")
            else:
                logger.info(f"  ✗ {row['probe_dir']:40s} ({row['status'][:50]})")

if __name__ == "__main__":
    main()
