#!/usr/bin/env python3
"""
Analyze Llama-3.2-11B and Phi4-VL probes
Reads layer names from results.json files
"""
import os
import sys
sys.path.insert(0, '/root/akhil/probe_analysis')
sys.path.insert(0, '/root/akhil/detailed_probe_analysis')

import torch
import pandas as pd
import json
import glob
from analyze_hallucination_types import run_detailed_analysis

# Model configurations
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
    """Discover probes by reading results.json files"""
    probes = []

    for probe_dir in sorted(os.listdir(probe_base)):
        probe_path = os.path.join(probe_base, probe_dir)

        if not os.path.isdir(probe_path):
            continue

        results_json = os.path.join(probe_path, 'results.json')
        checkpoint_path = os.path.join(probe_path, 'probe_model.pt')

        if not os.path.exists(results_json) or not os.path.exists(checkpoint_path):
            continue

        try:
            # Read layer info from results.json
            with open(results_json, 'r') as f:
                results = json.load(f)

            embedding_type = results.get('embedding_type')
            layer_name = results.get('layer_name')

            if embedding_type:
                probes.append({
                    'probe_dir': probe_dir,
                    'embedding_type': embedding_type,
                    'layer_name': layer_name if layer_name else 'N/A',
                    'checkpoint_path': checkpoint_path
                })
        except Exception as e:
            print(f"Warning: Could not read {results_json}: {e}")

    return probes

print("=" * 80)
print("ANALYZING LLAMA-3.2-11B AND PHI4-VL")
print("=" * 80)
print()

all_results = []
base_output_dir = "/root/akhil/detailed_probe_analysis/results"

for model_config in MODELS:
    print(f"\n{'='*80}")
    print(f"MODEL: {model_config['name']}")
    print('='*80)

    # Discover probes
    probes = discover_probes(model_config['probe_base'])
    print(f"Found {len(probes)} probes")
    print()

    for i, probe_info in enumerate(probes, 1):
        # Create output directory
        model_dir = model_config['name'].lower().replace('-', '_').replace('.', '_')
        output_dir = os.path.join(base_output_dir, model_dir, probe_info['probe_dir'])

        # Check if already analyzed
        if os.path.exists(os.path.join(output_dir, 'detailed_summary.json')):
            print(f"[{i:2d}/{len(probes)}] ✓ SKIP {probe_info['probe_dir']:35s} (already analyzed)")
            continue

        os.makedirs(output_dir, exist_ok=True)

        print(f"[{i:2d}/{len(probes)}] Analyzing {probe_info['probe_dir']:35s} ", end='', flush=True)
        print(f"(layer={probe_info['layer_name']}) ...", flush=True)

        try:
            # Run detailed analysis
            auroc, status = run_detailed_analysis(model_config, probe_info, output_dir)

            if status == "Success":
                print(f"             ✓ SUCCESS - AUROC: {auroc:.4f}")
            else:
                print(f"             ✗ FAILED - {status}")

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
            print(f"             ✗ ERROR: {error_msg}")

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

    # Read existing and filter out old Llama/Phi entries
    if os.path.exists(summary_path):
        existing_df = pd.read_csv(summary_path)
        # Remove old Llama/Phi entries
        existing_df = existing_df[~existing_df['model'].isin(['Llama-3.2-11B', 'Phi4-VL'])]
        # Combine with new results
        combined_df = pd.concat([existing_df, new_df], ignore_index=True)
        combined_df.to_csv(summary_path, index=False)
        print(f"✓ Replaced old entries and added {len(new_df)} new results")
    else:
        new_df.to_csv(summary_path, index=False)
        print(f"✓ Created new summary with {len(new_df)} results")

# Print summary
print("\n" + "=" * 80)
print("FINAL SUMMARY")
print("=" * 80)

for model_config in MODELS:
    model_results = [r for r in all_results if r['model'] == model_config['name']]
    if model_results:
        success_count = sum(1 for r in model_results if r['status'] == 'Success')
        print(f"\n{model_config['name']}: {success_count}/{len(model_results)} successful")

        for r in model_results:
            if r['auroc'] is not None:
                print(f"  ✓ {r['probe_dir']:35s} {r['layer_name']:10s} AUROC: {r['auroc']:.4f}")
            else:
                print(f"  ✗ {r['probe_dir']:35s} {r['layer_name']:10s} {r['status']}")

print("\n" + "=" * 80)
print("COMPLETE!")
print("=" * 80)
print(f"\nResults directory: {base_output_dir}")
print(f"Summary CSV: {summary_path}")
