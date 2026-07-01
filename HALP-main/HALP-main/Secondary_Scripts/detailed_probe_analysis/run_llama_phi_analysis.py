#!/usr/bin/env python3
"""
Direct execution script for Llama and Phi analysis
"""
import os
import sys

# Set paths
sys.path.insert(0, '/root/akhil/probe_analysis')
sys.path.insert(0, '/root/akhil/detailed_probe_analysis')

import torch
import pandas as pd
import glob
from datetime import datetime

print("Loading analysis modules...")
from analyze_hallucination_types import run_detailed_analysis

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

    return probes

print("=" * 80)
print("ANALYZING MISSING MODELS: Llama-3.2-11B and Phi4-VL")
print("=" * 80)
print()

all_results = []
base_output_dir = "/root/akhil/detailed_probe_analysis/results"

for model_config in MODELS:
    print(f"\n{'='*80}")
    print(f"MODEL: {model_config['name']}")
    print('='*80)

    probes = discover_probes(model_config['probe_base'])
    print(f"Found {len(probes)} probes\n")

    for i, probe_info in enumerate(probes, 1):
        model_dir = model_config['name'].lower().replace('-', '_').replace('.', '_')
        output_dir = os.path.join(base_output_dir, model_dir, probe_info['probe_dir'])

        if os.path.exists(os.path.join(output_dir, 'detailed_summary.json')):
            print(f"[{i:2d}/{len(probes)}] ✓ SKIP {probe_info['probe_dir']:35s} (already done)")
            continue

        os.makedirs(output_dir, exist_ok=True)
        print(f"[{i:2d}/{len(probes)}] Running {probe_info['probe_dir']:35s} ... ", end='', flush=True)

        try:
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
            error_msg = str(e)[:80]
            print(f"✗ ERROR: {error_msg}")
            all_results.append({
                'model': model_config['name'],
                'probe_dir': probe_info['probe_dir'],
                'embedding_type': probe_info['embedding_type'],
                'layer_name': probe_info['layer_name'],
                'auroc': None,
                'status': f"Error: {error_msg}"
            })

print("\n" + "=" * 80)
print("UPDATING SUMMARY CSV")
print("=" * 80)

summary_path = "/root/akhil/detailed_probe_analysis/detailed_analysis_summary.csv"

if len(all_results) > 0:
    new_df = pd.DataFrame(all_results)

    if os.path.exists(summary_path):
        existing_df = pd.read_csv(summary_path)
        combined_df = pd.concat([existing_df, new_df], ignore_index=True)
        combined_df.to_csv(summary_path, index=False)
        print(f"✓ Appended {len(new_df)} results to summary CSV")
    else:
        new_df.to_csv(summary_path, index=False)
        print(f"✓ Created summary CSV with {len(new_df)} results")

print("\n" + "=" * 80)
print("FINAL SUMMARY")
print("=" * 80)

for model_config in MODELS:
    model_results = [r for r in all_results if r['model'] == model_config['name']]
    if model_results:
        success = sum(1 for r in model_results if r['status'] == 'Success')
        print(f"\n{model_config['name']}: {success}/{len(model_results)} successful")

        for r in model_results:
            if r['auroc'] is not None:
                print(f"  ✓ {r['probe_dir']:35s} AUROC: {r['auroc']:.4f}")
            else:
                print(f"  ✗ {r['probe_dir']:35s} {r['status']}")

print("\n" + "=" * 80)
print("COMPLETE!")
print("=" * 80)
print(f"\nResults saved to: {base_output_dir}")
print(f"Summary CSV: {summary_path}")
