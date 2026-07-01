"""Test running analysis on single probe to debug"""
import sys
sys.path.insert(0, '/root/akhil/probe_analysis')
sys.path.insert(0, '/root/akhil/detailed_probe_analysis')

print("Importing modules...")
try:
    from analyze_hallucination_types import run_detailed_analysis
    print("✓ Successfully imported run_detailed_analysis")
except Exception as e:
    print(f"✗ Failed to import: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test with Llama first probe
model_config = {
    "name": "Llama-3.2-11B",
    "h5_dir": "/root/akhil/HALP_EACL_Models/Models/LLama_32/llama_output",
    "csv_path": "/root/akhil/FInal_CSV_Hallucination/llama32_manually_reviewed.csv",
    "probe_base": "/root/akhil/probe_training_scripts/llama32_model_probe/results",
}

probe_info = {
    'probe_dir': 'query_token_layer10',
    'embedding_type': 'query_token_representation',
    'layer_name': 'layer_10',
    'checkpoint_path': '/root/akhil/probe_training_scripts/llama32_model_probe/results/query_token_layer10/probe_model.pt'
}

output_dir = "/root/akhil/detailed_probe_analysis/results/llama_3_2_11b/query_token_layer10"

print(f"\nRunning analysis for {model_config['name']}/{probe_info['probe_dir']}")
print(f"Output: {output_dir}\n")

import os
os.makedirs(output_dir, exist_ok=True)

try:
    auroc, status = run_detailed_analysis(model_config, probe_info, output_dir)
    print(f"\n✓ SUCCESS!")
    print(f"  AUROC: {auroc}")
    print(f"  Status: {status}")
except Exception as e:
    print(f"\n✗ FAILED: {e}")
    import traceback
    traceback.print_exc()
