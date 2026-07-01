#!/usr/bin/env python3
"""
Analyze Llama-3.2-11B probes
Uses Llama-specific model architecture with 'network' instead of 'model'
"""
import os
import sys
sys.path.insert(0, '/root/akhil/probe_analysis')

import torch
import torch.nn as nn
import pandas as pd
import json
from analyze_probe_by_category import (
    load_hallucination_labels,
    load_embeddings_from_h5,
    get_predictions
)
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score
import numpy as np
from datetime import datetime

# Llama-specific probe class (uses self.network)
class LlamaHallucinationProbe(nn.Module):
    def __init__(self, input_dim, layer_sizes=[512, 256, 128], dropout_rate=0.3):
        super(LlamaHallucinationProbe, self).__init__()
        layers = []
        prev_size = input_dim
        for size in layer_sizes:
            layers.extend([
                nn.Linear(prev_size, size),
                nn.BatchNorm1d(size),
                nn.ReLU(),
                nn.Dropout(dropout_rate)
            ])
            prev_size = size
        layers.append(nn.Linear(prev_size, 1))
        layers.append(nn.Sigmoid())
        self.network = nn.Sequential(*layers)

    def forward(self, x):
        return self.network(x)

# Load detailed metadata
def load_detailed_metadata(csv_path):
    df = pd.read_csv(csv_path)
    metadata_map = {}
    for _, row in df.iterrows():
        metadata_map[row['question_id']] = {
            'basic_hallucination_type': row.get('basic_hallucination_type', 'Unknown'),
            'domain_type': row.get('domain_type', 'Unknown'),
            'answer_type': row.get('answer_type', 'Unknown')
        }
    return metadata_map

def analyze_by_type(test_ids, y_test, test_probs, metadata_map, column_name):
    df = pd.DataFrame({'question_id': test_ids, 'true_label': y_test, 'predicted_prob': test_probs})
    df['type_value'] = df['question_id'].map(lambda qid: metadata_map.get(qid, {}).get(column_name, 'Unknown'))

    results = []
    for type_value in sorted(df['type_value'].unique()):
        type_df = df[df['type_value'] == type_value]
        num_hall = (type_df['true_label'] == 1).sum()
        num_no_hall = (type_df['true_label'] == 0).sum()

        if len(type_df['true_label'].unique()) >= 2:
            auroc = roc_auc_score(type_df['true_label'], type_df['predicted_prob'])
            results.append({'type': type_value, 'num_samples': len(type_df), 'num_hallucination': num_hall, 'num_no_hallucination': num_no_hall, 'auroc': auroc, 'note': ''})
        else:
            results.append({'type': type_value, 'num_samples': len(type_df), 'num_hallucination': num_hall, 'num_no_hallucination': num_no_hall, 'auroc': None, 'note': 'Single class only'})

    return pd.DataFrame(results)

MODEL_CONFIG = {
    "name": "Llama-3.2-11B",
    "h5_dir": "/root/akhil/HALP_EACL_Models/Models/LLama_32/llama_output",
    "csv_path": "/root/akhil/FInal_CSV_Hallucination/llama32_manually_reviewed.csv",
    "probe_base": "/root/akhil/probe_training_scripts/llama32_model_probe/results",
}

print("="*80)
print("ANALYZING LLAMA-3.2-11B")
print("="*80)

# Discover probes
probes = []
for probe_dir in sorted(os.listdir(MODEL_CONFIG['probe_base'])):
    probe_path = os.path.join(MODEL_CONFIG['probe_base'], probe_dir)
    if not os.path.isdir(probe_path):
        continue
    results_json = os.path.join(probe_path, 'results.json')
    if os.path.exists(results_json):
        with open(results_json) as f:
            results = json.load(f)
        probes.append({
            'probe_dir': probe_dir,
            'embedding_type': results.get('embedding_type'),
            'layer_name': results.get('layer_name', 'N/A'),
            'checkpoint_path': os.path.join(probe_path, 'probe_model.pt')
        })

print(f"Found {len(probes)} probes\n")

all_results = []
base_output_dir = "/root/akhil/detailed_probe_analysis/results"
metadata_map = load_detailed_metadata("/root/akhil/final_data/sampled_10k_with_hallucination_types.csv")

for i, probe_info in enumerate(probes, 1):
    output_dir = os.path.join(base_output_dir, "llama_3_2_11b", probe_info['probe_dir'])

    if os.path.exists(os.path.join(output_dir, 'detailed_summary.json')):
        print(f"[{i:2d}/{len(probes)}] ✓ SKIP {probe_info['probe_dir']:35s}")
        continue

    os.makedirs(output_dir, exist_ok=True)
    print(f"[{i:2d}/{len(probes)}] {probe_info['probe_dir']:35s} ", end='', flush=True)

    try:
        labels_dict = load_hallucination_labels(MODEL_CONFIG["csv_path"])
        embeddings, labels, question_ids = load_embeddings_from_h5(MODEL_CONFIG["h5_dir"], probe_info['embedding_type'], labels_dict, layer_name=probe_info['layer_name'])

        X_train, X_test, y_train, y_test, train_ids, test_ids = train_test_split(embeddings, labels, question_ids, test_size=0.2, random_state=42, stratify=labels)

        # Ensure everything is on CPU
        device = 'cpu'
        input_dim = X_train.shape[1]
        model = LlamaHallucinationProbe(input_dim=input_dim).to(device)
        state_dict = torch.load(probe_info['checkpoint_path'], map_location=device)
        model.load_state_dict(state_dict)
        model.eval()  # Set to evaluation mode

        # Move data to CPU explicitly
        X_test_cpu = torch.tensor(X_test, dtype=torch.float32).to(device)

        # Get predictions manually to avoid device issues
        with torch.no_grad():
            test_probs = model(X_test_cpu).squeeze().cpu().numpy()
        overall_auroc = roc_auc_score(y_test, test_probs)

        # Analyze by types
        for col_name in ['basic_hallucination_type', 'domain_type', 'answer_type']:
            type_df = analyze_by_type(test_ids, y_test, test_probs, metadata_map, col_name)
            type_df.to_csv(os.path.join(output_dir, f'{col_name}_auroc.csv'), index=False)

        # Save summary
        with open(os.path.join(output_dir, 'detailed_summary.json'), 'w') as f:
            json.dump({'probe_name': f"{MODEL_CONFIG['name']}/{probe_info['probe_dir']}", 'model': MODEL_CONFIG['name'], 'probe_dir': probe_info['probe_dir'], 'embedding_type': probe_info['embedding_type'], 'layer_name': probe_info['layer_name'], 'overall_auroc': float(overall_auroc), 'test_samples': len(X_test), 'analysis_types': ['basic_hallucination_type', 'domain_type', 'answer_type'], 'timestamp': datetime.now().strftime('%Y%m%d_%H%M%S')}, f, indent=2)

        # Generate markdown report
        with open(os.path.join(output_dir, 'detailed_analysis_report.md'), 'w') as f:
            f.write(f"# Detailed Hallucination Type Analysis\n\n**Probe:** {MODEL_CONFIG['name']}/{probe_info['probe_dir']}\n**Analysis Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n---\n\n## Overall Performance\n\n**Test AUROC:** {overall_auroc:.4f}\n\n---\n\n")
            for col_name in ['basic_hallucination_type', 'domain_type', 'answer_type']:
                type_df = pd.read_csv(os.path.join(output_dir, f'{col_name}_auroc.csv'))
                f.write(f"## Performance by {col_name.replace('_', ' ').title()}\n\n| Type | AUROC | Samples | Hallucination | No Hallucination |\n|------|-------|---------|---------------|------------------|\n")
                for _, row in type_df.iterrows():
                    auroc_str = f"{row['auroc']:.4f}" if pd.notna(row['auroc']) else "N/A"
                    f.write(f"| {row['type']} | {auroc_str} | {row['num_samples']} | {row['num_hallucination']} | {row['num_no_hallucination']} |\n")
                f.write(f"\n---\n\n")

        print(f"✓ AUROC: {overall_auroc:.4f}")
        all_results.append({'model': MODEL_CONFIG['name'], 'probe_dir': probe_info['probe_dir'], 'embedding_type': probe_info['embedding_type'], 'layer_name': probe_info['layer_name'], 'auroc': overall_auroc, 'status': 'Success'})

    except Exception as e:
        error_msg = str(e)[:100]
        print(f"✗ ERROR: {error_msg}")
        all_results.append({'model': MODEL_CONFIG['name'], 'probe_dir': probe_info['probe_dir'], 'embedding_type': probe_info['embedding_type'], 'layer_name': probe_info['layer_name'], 'auroc': None, 'status': f"Error: {error_msg}"})

# Update summary CSV
summary_path = "/root/akhil/detailed_probe_analysis/detailed_analysis_summary.csv"
new_df = pd.DataFrame(all_results)

if os.path.exists(summary_path):
    existing_df = pd.read_csv(summary_path)
    existing_df = existing_df[existing_df['model'] != 'Llama-3.2-11B']
    combined_df = pd.concat([existing_df, new_df], ignore_index=True)
    combined_df.to_csv(summary_path, index=False)
    print(f"\n✓ Updated summary CSV ({len(new_df)} Llama results)")
else:
    new_df.to_csv(summary_path, index=False)

print("\n" + "="*80)
print("LLAMA ANALYSIS COMPLETE!")
print("="*80)
