#!/usr/bin/env python3
"""
Analyze LLaVA vision_only probe - special handling for variable-length embeddings
Uses padding to max length like the training script did
"""
import os
import sys
sys.path.insert(0, '/root/akhil/probe_analysis')

import torch
import torch.nn as nn
import pandas as pd
import numpy as np
import h5py
import glob
import json
from tqdm import tqdm
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score
from datetime import datetime

# LLaVA probe class (uses self.model, with Linear → ReLU → BatchNorm → Dropout order)
class LLaVAHallucinationProbe(nn.Module):
    def __init__(self, input_dim, layer_sizes=[512, 256, 128], dropout_rate=0.3):
        super(LLaVAHallucinationProbe, self).__init__()
        layers = []
        prev_dim = input_dim
        for size in layer_sizes:
            layers.append(nn.Linear(prev_dim, size))
            layers.append(nn.ReLU())
            layers.append(nn.BatchNorm1d(size))
            layers.append(nn.Dropout(dropout_rate))
            prev_dim = size
        layers.append(nn.Linear(prev_dim, 1))
        layers.append(nn.Sigmoid())
        self.model = nn.Sequential(*layers)

    def forward(self, x):
        return self.model(x).squeeze()

def load_hallucination_labels(csv_path):
    """Load labels from CSV"""
    df = pd.read_csv(csv_path, low_memory=False)
    labels = {}
    for _, row in df.iterrows():
        target_value = row['is_hallucinating_manual']
        if isinstance(target_value, str):
            target_value = target_value.lower() in ['true', '1', 'yes']
        else:
            target_value = bool(target_value)
        labels[row['question_id']] = {'label': int(target_value)}
    return labels

def load_embeddings_with_padding(h5_dir, labels_dict):
    """Load vision_only embeddings with padding for variable lengths"""
    h5_files = sorted(glob.glob(os.path.join(h5_dir, "*.h5")))

    embeddings_list = []
    labels_list = []
    question_ids = []

    for h5_file in tqdm(h5_files, desc="Processing H5 files"):
        with h5py.File(h5_file, 'r') as f:
            for question_id in f.keys():
                if question_id not in labels_dict:
                    continue
                sample_group = f[question_id]
                if 'vision_only_representation' in sample_group:
                    embedding = sample_group['vision_only_representation'][:]
                    embeddings_list.append(embedding)
                    labels_list.append(labels_dict[question_id]['label'])
                    question_ids.append(question_id)

    # Pad to max length (like training script does)
    shapes = [emb.shape for emb in embeddings_list]
    if len(set(shapes)) > 1:
        max_len = max(emb.shape[0] for emb in embeddings_list)
        print(f"Variable shapes detected. Padding to max length: {max_len}")
        padded_embeddings = []
        for emb in embeddings_list:
            padded = np.zeros(max_len, dtype=emb.dtype)
            padded[:len(emb)] = emb
            padded_embeddings.append(padded)
        embeddings = np.stack(padded_embeddings)
    else:
        embeddings = np.stack(embeddings_list)

    labels = np.array(labels_list)
    return embeddings, labels, question_ids

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

print("="*80)
print("ANALYZING LLAVA VISION_ONLY")
print("="*80)

MODEL_CONFIG = {
    "name": "LLaVA-Next-8B",
    "h5_dir": "/root/akhil/HALP_EACL_Models/Models/LLaVa_model/llava_output",
    "csv_path": "/root/akhil/FInal_CSV_Hallucination/llava_manually_reviewed.csv",
}

probe_info = {
    'probe_dir': 'vision_only',
    'embedding_type': 'vision_only_representation',
    'layer_name': 'N/A',
    'checkpoint_path': '/root/akhil/probe_training_scripts/llava_model_probe/results/vision_only/probe_model.pt'
}

output_dir = "/root/akhil/detailed_probe_analysis/results/llava_next_8b/vision_only"
os.makedirs(output_dir, exist_ok=True)

print(f"\nProcessing: {probe_info['probe_dir']}")

try:
    # Load data with padding
    labels_dict = load_hallucination_labels(MODEL_CONFIG["csv_path"])
    embeddings, labels, question_ids = load_embeddings_with_padding(MODEL_CONFIG["h5_dir"], labels_dict)

    print(f"Loaded {len(embeddings)} samples")
    print(f"Embedding shape: {embeddings.shape}")

    # Train/test split
    X_train, X_test, y_train, y_test, train_ids, test_ids = train_test_split(
        embeddings, labels, question_ids, test_size=0.2, random_state=42, stratify=labels
    )

    # Load model
    device = 'cpu'
    checkpoint = torch.load(probe_info['checkpoint_path'], map_location=device)
    input_dim = checkpoint['input_dim']

    model = LLaVAHallucinationProbe(input_dim=input_dim).to(device)
    model.load_state_dict(checkpoint['model_state_dict'])
    model.eval()

    # Get predictions
    X_test_tensor = torch.tensor(X_test, dtype=torch.float32).to(device)
    with torch.no_grad():
        test_probs = model(X_test_tensor).squeeze().cpu().numpy()

    overall_auroc = roc_auc_score(y_test, test_probs)
    print(f"Overall AUROC: {overall_auroc:.4f}")

    # Load metadata and analyze by types
    metadata_map = load_detailed_metadata("/root/akhil/final_data/sampled_10k_with_hallucination_types.csv")

    for col_name in ['basic_hallucination_type', 'domain_type', 'answer_type']:
        type_df = analyze_by_type(test_ids, y_test, test_probs, metadata_map, col_name)
        type_df.to_csv(os.path.join(output_dir, f'{col_name}_auroc.csv'), index=False)
        print(f"  ✓ Saved {col_name}_auroc.csv")

    # Save JSON summary
    with open(os.path.join(output_dir, 'detailed_summary.json'), 'w') as f:
        json.dump({
            'probe_name': f"{MODEL_CONFIG['name']}/{probe_info['probe_dir']}",
            'model': MODEL_CONFIG['name'],
            'probe_dir': probe_info['probe_dir'],
            'embedding_type': probe_info['embedding_type'],
            'layer_name': probe_info['layer_name'],
            'overall_auroc': float(overall_auroc),
            'test_samples': len(X_test),
            'analysis_types': ['basic_hallucination_type', 'domain_type', 'answer_type'],
            'timestamp': datetime.now().strftime('%Y%m%d_%H%M%S')
        }, f, indent=2)

    # Generate markdown report
    with open(os.path.join(output_dir, 'detailed_analysis_report.md'), 'w') as f:
        f.write(f"# Detailed Hallucination Type Analysis\n\n")
        f.write(f"**Probe:** {MODEL_CONFIG['name']}/{probe_info['probe_dir']}\n")
        f.write(f"**Analysis Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n---\n\n")
        f.write(f"## Overall Performance\n\n**Test AUROC:** {overall_auroc:.4f}\n\n---\n\n")

        for col_name in ['basic_hallucination_type', 'domain_type', 'answer_type']:
            type_df = pd.read_csv(os.path.join(output_dir, f'{col_name}_auroc.csv'))
            f.write(f"## Performance by {col_name.replace('_', ' ').title()}\n\n")
            f.write(f"| Type | AUROC | Samples | Hallucination | No Hallucination |\n")
            f.write(f"|------|-------|---------|---------------|------------------|\n")
            for _, row in type_df.iterrows():
                auroc_str = f"{row['auroc']:.4f}" if pd.notna(row['auroc']) else "N/A"
                f.write(f"| {row['type']} | {auroc_str} | {row['num_samples']} | {row['num_hallucination']} | {row['num_no_hallucination']} |\n")
            f.write(f"\n---\n\n")

    # Update summary CSV
    summary_path = "/root/akhil/detailed_probe_analysis/detailed_analysis_summary.csv"
    new_row = {
        'model': MODEL_CONFIG['name'],
        'probe_dir': probe_info['probe_dir'],
        'embedding_type': probe_info['embedding_type'],
        'layer_name': '',
        'auroc': overall_auroc,
        'status': 'Success'
    }

    if os.path.exists(summary_path):
        existing_df = pd.read_csv(summary_path)
        # Remove old failed entry
        existing_df = existing_df[~((existing_df['model'] == MODEL_CONFIG['name']) & (existing_df['probe_dir'] == 'vision_only'))]
        # Add new entry
        new_df = pd.concat([existing_df, pd.DataFrame([new_row])], ignore_index=True)
        new_df.to_csv(summary_path, index=False)

    print(f"\n✓ SUCCESS - AUROC: {overall_auroc:.4f}")
    print(f"✓ Results saved to: {output_dir}")

except Exception as e:
    print(f"\n✗ ERROR: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*80)
print("LLAVA VISION_ONLY ANALYSIS COMPLETE!")
print("="*80)
