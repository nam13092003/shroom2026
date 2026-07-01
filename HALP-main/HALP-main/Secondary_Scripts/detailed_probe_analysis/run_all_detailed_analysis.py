"""
Run Detailed Analysis for All Probes
=====================================
Analyzes all probes by basic_hallucination_type, domain_type, and answer_type.
"""

import os
import sys
import torch
import pandas as pd
import glob
from datetime import datetime
import logging

sys.path.insert(0, '/root/akhil/probe_analysis')
sys.path.insert(0, '/root/akhil/detailed_probe_analysis')

from analyze_hallucination_types import run_detailed_analysis, CONFIG_PARAMS

# Setup logging
log_file = f'/root/akhil/detailed_probe_analysis/batch_analysis_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'
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
    },
    {
        "name": "FastVLM-7B",
        "h5_dir": "/root/akhil/HALP_EACL_Models/Models/FastVLM_model/fastvlm_output",
        "csv_path": "/root/akhil/FInal_CSV_Hallucination/fastvlm_manually_reviewed.csv",
        "probe_base": "/root/akhil/probe_training_scripts/fastvlm_model_probe/results",
    },
    {
        "name": "LLaVA-Next-8B",
        "h5_dir": "/root/akhil/HALP_EACL_Models/Models/LLaVa_model/llava_output",
        "csv_path": "/root/akhil/FInal_CSV_Hallucination/llava_manually_reviewed.csv",
        "probe_base": "/root/akhil/probe_training_scripts/llava_model_probe/results",
    },
    {
        "name": "Molmo-V1",
        "h5_dir": "/root/akhil/HALP_EACL_Models/Models/Molmo_V1/molmo_output",
        "csv_path": "/root/akhil/FInal_CSV_Hallucination/molmo_manually_reviewed.csv",
        "probe_base": "/root/akhil/probe_training_scripts/molmo_model_probe/results",
    },
    {
        "name": "Qwen2.5-VL-7B",
        "h5_dir": "/root/akhil/HALP_EACL_Models/Models/Qwen25_VL/qwen25_output",
        "csv_path": "/root/akhil/FInal_CSV_Hallucination/qwen25vl_manually_reviewed.csv",
        "probe_base": "/root/akhil/probe_training_scripts/qwen25vl_model_probe/results",
    },
    {
        "name": "SmolVLM2-2.2B",
        "h5_dir": "/root/akhil/HALP_EACL_Models/Models/Smol_VL/smolvlm_output",
        "csv_path": "/root/akhil/FInal_CSV_Hallucination/smolvlm_manually_reviewed.csv",
        "probe_base": "/root/akhil/probe_training_scripts/smolvlm_model_probe/results",
    },
    {
        "name": "Llama-3.2-11B",
        "h5_dir": "/root/akhil/HALP_EACL_Models/Models/LLama_32/llama_output",
        "csv_path": "/root/akhil/FInal_CSV_Hallucination/llama32_manually_reviewed.csv",
        "probe_base": "/root/akhil/probe_training_scripts/llama32_model_probe/results",
    },
    {
        "name": "Phi4-VL",
        "h5_dir": "/root/akhil/HALP_EACL_Models/Models/Phi4_VL/phi4_output",
        "csv_path": "/root/akhil/FInal_CSV_Hallucination/phi4vl_manually_reviewed.csv",
        "probe_base": "/root/akhil/probe_training_scripts/phi4vl_model_probe/results",
    },
]

def discover_probes(probe_base):
    """Discover all trained probes."""
    probes = []
    checkpoint_files = glob.glob(os.path.join(probe_base, "*/probe_model.pt"))

    for checkpoint_path in sorted(checkpoint_files):
        probe_dir = os.path.basename(os.path.dirname(checkpoint_path))

        try:
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

def main():
    logger.info("="*80)
    logger.info("BATCH DETAILED ANALYSIS - ALL PROBES")
    logger.info("="*80)
    logger.info(f"Analyzing by: basic_hallucination_type, domain_type, answer_type")
    logger.info("")

    results = []
    base_output_dir = "/root/akhil/detailed_probe_analysis/results"

    for model_config in MODEL_CONFIGS:
        logger.info(f"\n{'='*80}")
        logger.info(f"Processing: {model_config['name']}")
        logger.info(f"{'='*80}")

        # Discover probes
        probes = discover_probes(model_config['probe_base'])
        logger.info(f"Found {len(probes)} trained probes")

        for probe_info in probes:
            output_dir = os.path.join(
                base_output_dir,
                model_config['name'].lower().replace('-', '_').replace('.', '_'),
                probe_info['probe_dir']
            )

            # Check if already analyzed
            if os.path.exists(os.path.join(output_dir, 'detailed_summary.json')):
                logger.info(f"✓ SKIP {model_config['name']}/{probe_info['probe_dir']}: Already analyzed")
                results.append({
                    'model': model_config['name'],
                    'probe_dir': probe_info['probe_dir'],
                    'status': 'Already analyzed',
                    'auroc': None
                })
                continue

            os.makedirs(output_dir, exist_ok=True)

            # Run analysis
            auroc, status = run_detailed_analysis(model_config, probe_info, output_dir)

            results.append({
                'model': model_config['name'],
                'probe_dir': probe_info['probe_dir'],
                'embedding_type': probe_info['embedding_type'],
                'layer_name': probe_info['layer_name'] if probe_info['layer_name'] else 'N/A',
                'auroc': auroc,
                'status': status
            })

    # Save summary
    results_df = pd.DataFrame(results)
    summary_path = "/root/akhil/detailed_probe_analysis/detailed_analysis_summary.csv"
    results_df.to_csv(summary_path, index=False)

    logger.info(f"\n{'='*80}")
    logger.info("BATCH ANALYSIS COMPLETE")
    logger.info(f"{'='*80}")
    logger.info(f"\nResults: {summary_path}")

    # Summary stats
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
        completed = len(model_results[model_results['status'].isin(['Success', 'Already analyzed'])])
        logger.info(f"\n{model_name}: {completed}/{len(model_results)} completed")

        for _, row in model_results.iterrows():
            if row['auroc']:
                logger.info(f"  ✓ {row['probe_dir']:40s} AUROC: {row['auroc']:.4f}")
            elif row['status'] == 'Already analyzed':
                logger.info(f"  ✓ {row['probe_dir']:40s} (already done)")
            else:
                logger.info(f"  ✗ {row['probe_dir']:40s} ({row['status'][:50]})")

if __name__ == "__main__":
    main()
