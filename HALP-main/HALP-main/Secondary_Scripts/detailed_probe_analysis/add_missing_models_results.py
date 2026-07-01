#!/usr/bin/env python3
"""
Add results for missing 2 models (Llama-3.2 and Phi4-VL) to the detailed analysis
This script can be executed independently
"""

import os
import sys

# Add necessary paths
sys.path.insert(0, '/root/akhil/probe_analysis')
sys.path.insert(0, '/root/akhil/detailed_probe_analysis')

import torch
import pandas as pd
import glob
from datetime import datetime

# Import the analysis function
from analyze_hallucination_types import run_detailed_analysis

# Model configurations for the 2 missing models
MODELS = [
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
    """Find all trained probes in a directory"""
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
                    'layer_name': layer_name if layer_name else 'N/A',
                    'checkpoint_path': checkpoint_path
                })
        except Exception as e:
            print(f"Warning: Could not load {checkpoint_path}: {e}")
            continue

    return probes

def main():
    print("=" * 80)
    print("ADDING DETAILED ANALYSIS FOR MISSING MODELS")
    print("=" * 80)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    all_results = []
    base_output_dir = "/root/akhil/detailed_probe_analysis/results"

    for model_config in MODELS:
        print(f"\nProcessing: {model_config['name']}")
        print("-" * 80)

        # Find all probes for this model
        probes = discover_probes(model_config['probe_base'])
        print(f"Found {len(probes)} trained probes")

        for i, probe_info in enumerate(probes, 1):
            # Create output directory
            model_dir_name = model_config['name'].lower().replace('-', '_').replace('.', '_')
            output_dir = os.path.join(base_output_dir, model_dir_name, probe_info['probe_dir'])

            # Skip if already analyzed
            if os.path.exists(os.path.join(output_dir, 'detailed_summary.json')):
                print(f"  [{i}/{len(probes)}] ✓ SKIP {probe_info['probe_dir']} (already analyzed)")
                continue

            os.makedirs(output_dir, exist_ok=True)

            print(f"  [{i}/{len(probes)}] Analyzing {probe_info['probe_dir']}...", end=' ')

            try:
                # Run detailed analysis
                auroc, status = run_detailed_analysis(model_config, probe_info, output_dir)

                if status == "Success":
                    print(f"✓ AUROC: {auroc:.4f}")
                else:
                    print(f"✗ {status}")

                all_results.append({
                    'model': model_config['name'],
                    'probe_dir': probe_info['probe_dir'],
                    'embedding_type': probe_info['embedding_type'],
                    'layer_name': probe_info['layer_name'],
                    'auroc': auroc,
                    'status': status
                })

            except Exception as e:
                error_msg = str(e)[:100]
                print(f"✗ ERROR: {error_msg}")
                all_results.append({
                    'model': model_config['name'],
                    'probe_dir': probe_info['probe_dir'],
                    'embedding_type': probe_info['embedding_type'],
                    'layer_name': probe_info['layer_name'],
                    'auroc': None,
                    'status': f"Error: {error_msg}"
                })

    # Update summary CSV
    print("\n" + "=" * 80)
    print("UPDATING SUMMARY CSV")
    print("=" * 80)

    summary_path = "/root/akhil/detailed_probe_analysis/detailed_analysis_summary.csv"

    if len(all_results) > 0:
        new_df = pd.DataFrame(all_results)

        # Read existing summary
        if os.path.exists(summary_path):
            existing_df = pd.read_csv(summary_path)
            # Combine and remove duplicates
            combined_df = pd.concat([existing_df, new_df], ignore_index=True)
            combined_df.to_csv(summary_path, index=False)
            print(f"✓ Added {len(new_df)} new results to {summary_path}")
        else:
            new_df.to_csv(summary_path, index=False)
            print(f"✓ Created {summary_path} with {len(new_df)} results")

    # Print summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)

    for model_config in MODELS:
        model_results = [r for r in all_results if r['model'] == model_config['name']]
        if model_results:
            success_count = sum(1 for r in model_results if r['status'] == 'Success')
            print(f"\n{model_config['name']}: {success_count}/{len(model_results)} successful")

            for r in model_results:
                if r['auroc'] is not None:
                    print(f"  ✓ {r['probe_dir']:35s} AUROC: {r['auroc']:.4f}")
                else:
                    print(f"  ✗ {r['probe_dir']:35s} {r['status']}")

    print("\n" + "=" * 80)
    print("COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    main()
