"""
Run detailed analysis for the 2 missing models: Llama-3.2 and Phi4-VL
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

from analyze_hallucination_types import run_detailed_analysis

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Missing models
MODEL_CONFIGS = [
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
    logger.info("ANALYZING MISSING MODELS: Llama-3.2 and Phi4-VL")
    logger.info("="*80)

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
                continue

            os.makedirs(output_dir, exist_ok=True)

            logger.info(f"\nAnalyzing {model_config['name']}/{probe_info['probe_dir']}...")

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

            if status == 'Success':
                logger.info(f"✓ SUCCESS: AUROC = {auroc:.4f}")
            else:
                logger.info(f"✗ FAILED: {status}")

    # Append to existing summary
    summary_path = "/root/akhil/detailed_probe_analysis/detailed_analysis_summary.csv"

    if os.path.exists(summary_path):
        existing_df = pd.read_csv(summary_path)
        new_results_df = pd.DataFrame(results)
        combined_df = pd.concat([existing_df, new_results_df], ignore_index=True)
        combined_df.to_csv(summary_path, index=False)
        logger.info(f"\nAppended {len(results)} new results to {summary_path}")
    else:
        results_df = pd.DataFrame(results)
        results_df.to_csv(summary_path, index=False)
        logger.info(f"\nCreated new summary at {summary_path}")

    logger.info(f"\n{'='*80}")
    logger.info("ANALYSIS COMPLETE")
    logger.info(f"{'='*80}")

    # Summary
    for model_name in MODEL_CONFIGS:
        model_results = [r for r in results if r['model'] == model_name['name']]
        success = sum(1 for r in model_results if r['status'] == 'Success')
        logger.info(f"\n{model_name['name']}: {success}/{len(model_results)} successful")
        for r in model_results:
            if r['auroc']:
                logger.info(f"  ✓ {r['probe_dir']:40s} AUROC: {r['auroc']:.4f}")
            else:
                logger.info(f"  ✗ {r['probe_dir']:40s} ({r['status'][:50]})")

if __name__ == "__main__":
    main()
