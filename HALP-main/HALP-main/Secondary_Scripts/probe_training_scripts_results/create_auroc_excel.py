#!/usr/bin/env python3
"""
Create Excel file with Test AUROC metrics for all models and probes.
"""

import json
import pandas as pd
from pathlib import Path

# Define all models and their probe result paths
models_config = {
    "Gemma3-12B": {
        "base_path": "/root/akhil/probe_training_scripts/gemma_model_probe/results",
        "probes": [
            "vision_only",
            "vision_token_layer0",
            "vision_token_layer_n_4",
            "vision_token_layer_n_2",
            "vision_token_layer_3n_4",
            "vision_token_layer_n",
            "query_token_layer0",
            "query_token_layer_n_4",
            "query_token_layer_n_2",
            "query_token_layer_3n_4",
            "query_token_layer_n"
        ]
    },
    "FastVLM-7B": {
        "base_path": "/root/akhil/probe_training_scripts/fastvlm_model_probe/results",
        "probes": [
            "vision_only",
            "vision_token_layer0",
            "vision_token_layer_n_4",
            "vision_token_layer_n_2",
            "vision_token_layer_3n_4",
            "vision_token_layer_n",
            "query_token_layer0",
            "query_token_layer_n_4",
            "query_token_layer_n_2",
            "query_token_layer_3n_4",
            "query_token_layer_n"
        ]
    },
    "LLaVa-Next-8B": {
        "base_path": "/root/akhil/probe_training_scripts/llava_model_probe/results",
        "probes": [
            "vision_only",
            "vision_token_layer0",
            "vision_token_layer_n_4",
            "vision_token_layer_n_2",
            "vision_token_layer_3n_4",
            "vision_token_layer_n",
            "query_token_layer0",
            "query_token_layer_n_4",
            "query_token_layer_n_2",
            "query_token_layer_3n_4",
            "query_token_layer_n"
        ]
    },
    "Molmo-V1": {
        "base_path": "/root/akhil/probe_training_scripts/molmo_model_probe/results",
        "probes": [
            "vision_only",
            "vision_token_layer0",
            "vision_token_layer_n_4",
            "vision_token_layer_n_2",
            "vision_token_layer_3n_4",
            "vision_token_layer_n",
            "query_token_layer0",
            "query_token_layer_n_4",
            "query_token_layer_n_2",
            "query_token_layer_3n_4",
            "query_token_layer_n"
        ]
    },
    "Qwen2.5-VL-7B": {
        "base_path": "/root/akhil/probe_training_scripts/qwen25vl_model_probe/results",
        "probes": [
            "vision_only",
            "vision_token_layer0",
            "vision_token_layer_n_4",
            "vision_token_layer_n_2",
            "vision_token_layer_3n_4",
            "vision_token_layer_n",
            "query_token_layer0",
            "query_token_layer_n_4",
            "query_token_layer_n_2",
            "query_token_layer_3n_4",
            "query_token_layer_n"
        ]
    },
    "Llama-3.2-11B-Vision": {
        "base_path": "/root/akhil/probe_training_scripts/llama32_model_probe/results",
        "probes": [
            "vision_only",
            "vision_token_layer0",
            "vision_token_layer10",
            "vision_token_layer20",
            "vision_token_layer30",
            "vision_token_layer39",
            "query_token_layer0",
            "query_token_layer10",
            "query_token_layer20",
            "query_token_layer30",
            "query_token_layer39"
        ]
    },
    "Phi4-VL": {
        "base_path": "/root/akhil/probe_training_scripts/phi4vl_model_probe/results",
        "probes": [
            "vision_only",
            "vision_token_layer0",
            "vision_token_layer8",
            "vision_token_layer16",
            "vision_token_layer24",
            "vision_token_layer31",
            "query_token_layer0",
            "query_token_layer8",
            "query_token_layer16",
            "query_token_layer24",
            "query_token_layer31"
        ]
    }
}

# Column headers
columns = [
    "Model Name",
    "Vision Only",
    "Vision Token - Layer 0",
    "Vision Token - Layer n/4",
    "Vision Token - Layer n/2",
    "Vision Token - Layer 3n/4",
    "Vision Token - Layer n",
    "Query Token - Layer 0",
    "Query Token - Layer n/4",
    "Query Token - Layer n/2",
    "Query Token - Layer 3n/4",
    "Query Token - Layer n"
]

# Collect data
data = []

for model_name, config in models_config.items():
    row = [model_name]

    for probe_dir in config["probes"]:
        results_file = Path(config["base_path"]) / probe_dir / "results.json"

        try:
            with open(results_file, 'r') as f:
                results = json.load(f)
                auroc = results["test_set"]["auroc"]
                row.append(round(auroc, 4))
                print(f"✓ {model_name} - {probe_dir}: {auroc:.4f}")
        except Exception as e:
            print(f"✗ Error reading {model_name} - {probe_dir}: {e}")
            row.append(None)

    data.append(row)

# Create DataFrame
df = pd.DataFrame(data, columns=columns)

# Save to Excel
output_file = "/root/akhil/probe_training_scripts/test_auroc_results.xlsx"
df.to_excel(output_file, index=False, sheet_name="Test AUROC Metrics")

print(f"\n✓ Excel file created successfully: {output_file}")
print(f"\nDataFrame:\n{df.to_string(index=False)}")
