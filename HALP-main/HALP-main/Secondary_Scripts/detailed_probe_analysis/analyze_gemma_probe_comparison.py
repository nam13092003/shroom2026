#!/usr/bin/env python3
"""
Deep analysis: Compare probe predictions across representation types for Gemma
Find cases where:
1. Vision-only probe failed BUT query token probe succeeded
2. Both vision-only and vision token failed BUT query token succeeded
"""
import pandas as pd
import numpy as np
import torch
import h5py
import os
import sys
import glob
from tqdm import tqdm

sys.path.insert(0, '/root/akhil/probe_analysis')

from analyze_probe_by_category import (
    load_hallucination_labels,
    load_embeddings_from_h5,
    HallucinationProbe,
    get_predictions
)
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score

# Load detailed metadata
metadata_df = pd.read_csv('/root/akhil/final_data/sampled_10k_with_hallucination_types.csv')
metadata_lookup = {}
for _, row in metadata_df.iterrows():
    metadata_lookup[row['question_id']] = {
        'basic_hallucination_type': row.get('basic_hallucination_type', 'Unknown'),
        'domain_type': row.get('domain_type', 'Unknown'),
        'answer_type': row.get('answer_type', 'Unknown'),
        'image_id': row.get('image_id', 'Unknown'),
        'question': row.get('question', 'Unknown')
    }

# Gemma configuration
GEMMA_CONFIG = {
    "name": "Gemma3-12B",
    "h5_dir": "/root/akhil/HALP_EACL_Models/Models/Gemma3_12B/gemma_output",
    "csv_path": "/root/akhil/FInal_CSV_Hallucination/gemma3_manually_reviewed.csv",
}

# Load labels
labels_dict = load_hallucination_labels(GEMMA_CONFIG["csv_path"])

print("="*80)
print("GEMMA PROBE COMPARISON ANALYSIS")
print("="*80)

# Function to load probe and get predictions
def get_probe_predictions(probe_path, h5_dir, embedding_type, layer_name=None):
    """Load a probe and get its predictions on test set"""

    # Load embeddings
    if embedding_type == 'vision_only_representation':
        # Special handling for vision_only with padding
        embeddings_list = []
        labels_list = []
        question_ids = []

        h5_files = sorted(glob.glob(os.path.join(h5_dir, "*.h5")))
        for h5_file in h5_files:
            with h5py.File(h5_file, 'r') as f:
                for question_id in f.keys():
                    if question_id not in labels_dict:
                        continue
                    sample_group = f[question_id]
                    if embedding_type in sample_group:
                        embedding = sample_group[embedding_type][:]
                        embeddings_list.append(embedding)
                        labels_list.append(labels_dict[question_id]['label'])
                        question_ids.append(question_id)

        # Pad to max length
        shapes = [emb.shape for emb in embeddings_list]
        if len(set(shapes)) > 1:
            max_len = max(emb.shape[0] for emb in embeddings_list)
            padded_embeddings = []
            for emb in embeddings_list:
                padded = np.zeros(max_len, dtype=emb.dtype)
                padded[:len(emb)] = emb
                padded_embeddings.append(padded)
            embeddings = np.stack(padded_embeddings)
        else:
            embeddings = np.stack(embeddings_list)
        labels = np.array(labels_list)
    else:
        embeddings, labels, question_ids = load_embeddings_from_h5(
            h5_dir, embedding_type, labels_dict, layer_name=layer_name
        )

    # Split (same as training)
    X_train, X_test, y_train, y_test, train_ids, test_ids = train_test_split(
        embeddings, labels, question_ids, test_size=0.2, random_state=42, stratify=labels
    )

    # Load probe
    device = 'cpu'
    checkpoint = torch.load(probe_path, map_location=device)
    input_dim = checkpoint.get('input_dim', X_train.shape[1])

    model = HallucinationProbe(
        input_dim=input_dim,
        layer_sizes=[512, 256, 128],
        dropout_rate=0.3
    ).to(device)

    if 'model_state_dict' in checkpoint:
        model.load_state_dict(checkpoint['model_state_dict'])
    else:
        model.load_state_dict(checkpoint)

    model.eval()

    # Get predictions manually to ensure CPU
    X_test_tensor = torch.tensor(X_test, dtype=torch.float32).to(device)
    with torch.no_grad():
        test_probs = model(X_test_tensor).cpu().numpy()
        if len(test_probs.shape) > 1:
            test_probs = test_probs.squeeze()

    # Binary predictions (threshold 0.5)
    test_preds = (test_probs > 0.5).astype(int)

    return test_ids, y_test, test_preds, test_probs

print("\nLoading probe predictions...")

# Get predictions from all three representation types
vision_only_ids, vision_only_y, vision_only_preds, vision_only_probs = get_probe_predictions(
    '/root/akhil/probe_training_scripts/gemma_model_probe/results/vision_only/probe_model.pt',
    GEMMA_CONFIG["h5_dir"],
    'vision_only_representation'
)

print("✓ Vision-only predictions loaded")

# Best vision token layer (last layer - layer 47)
vision_token_ids, vision_token_y, vision_token_preds, vision_token_probs = get_probe_predictions(
    '/root/akhil/probe_training_scripts/gemma_model_probe/results/vision_token_layer_n/probe_model.pt',
    GEMMA_CONFIG["h5_dir"],
    'vision_token_representation',
    layer_name='layer_47'
)

print("✓ Vision token (layer 47) predictions loaded")

# Best query token layer (layer 47 based on results)
query_token_ids, query_token_y, query_token_preds, query_token_probs = get_probe_predictions(
    '/root/akhil/probe_training_scripts/gemma_model_probe/results/query_token_layer_n/probe_model.pt',
    GEMMA_CONFIG["h5_dir"],
    'query_token_representation',
    layer_name='layer_47'
)

print("✓ Query token (layer 47) predictions loaded")

# Create a combined dataframe
# First, create lookup dictionaries for faster access
vision_only_dict = {qid: i for i, qid in enumerate(vision_only_ids)}
vision_token_dict = {qid: i for i, qid in enumerate(vision_token_ids)}

results = []
for i, qid in enumerate(query_token_ids):
    # Find corresponding indices using dictionaries
    if qid in vision_only_dict and qid in vision_token_dict:
        vo_idx = vision_only_dict[qid]
        vt_idx = vision_token_dict[qid]

        results.append({
            'question_id': qid,
            'true_label': query_token_y[i],
            'vision_only_pred': vision_only_preds[vo_idx],
            'vision_only_prob': vision_only_probs[vo_idx],
            'vision_token_pred': vision_token_preds[vt_idx],
            'vision_token_prob': vision_token_probs[vt_idx],
            'query_token_pred': query_token_preds[i],
            'query_token_prob': query_token_probs[i],
            'vision_only_correct': int(vision_only_preds[vo_idx] == query_token_y[i]),
            'vision_token_correct': int(vision_token_preds[vt_idx] == query_token_y[i]),
            'query_token_correct': int(query_token_preds[i] == query_token_y[i])
        })

df = pd.DataFrame(results)

# Add metadata
df['basic_hallucination_type'] = df['question_id'].map(
    lambda qid: metadata_lookup.get(qid, {}).get('basic_hallucination_type', 'Unknown')
)
df['domain_type'] = df['question_id'].map(
    lambda qid: metadata_lookup.get(qid, {}).get('domain_type', 'Unknown')
)
df['image_id'] = df['question_id'].map(
    lambda qid: metadata_lookup.get(qid, {}).get('image_id', 'Unknown')
)
df['question'] = df['question_id'].map(
    lambda qid: metadata_lookup.get(qid, {}).get('question', 'Unknown')
)

# Load model answers
gemma_csv = pd.read_csv(GEMMA_CONFIG["csv_path"], low_memory=False)
answer_lookup = {}
for _, row in gemma_csv.iterrows():
    answer_lookup[row['question_id']] = {
        'ground_truth': row['ground_truth_answer'],
        'model_answer': row['model_answer']
    }

df['ground_truth'] = df['question_id'].map(lambda qid: answer_lookup.get(qid, {}).get('ground_truth', 'N/A'))
df['model_answer'] = df['question_id'].map(lambda qid: answer_lookup.get(qid, {}).get('model_answer', 'N/A'))

print(f"\nTotal test samples: {len(df)}")

# Find cases where vision-only failed but query token succeeded
case1 = df[(df['vision_only_correct'] == 0) & (df['query_token_correct'] == 1)]
print(f"\nCase 1 (Vision-only failed, Query token succeeded): {len(case1)} examples")

# Find cases where BOTH vision-only and vision-token failed but query token succeeded
case2 = df[(df['vision_only_correct'] == 0) & (df['vision_token_correct'] == 0) & (df['query_token_correct'] == 1)]
print(f"Case 2 (Vision-only AND Vision-token failed, Query token succeeded): {len(case2)} examples")

# Find cases where only vision-token succeeded (vision-only and query failed)
case3 = df[(df['vision_only_correct'] == 0) & (df['vision_token_correct'] == 1) & (df['query_token_correct'] == 0)]
print(f"Case 3 (Only Vision-token succeeded): {len(case3)} examples")

# Get 2 examples per basic_hallucination_type for each case
output = []

output.append("# Gemma Probe Comparison Analysis\n")
output.append("Comparing predictions across Vision-only, Vision-token (layer 47), and Query-token (layer 47) probes\n\n")
output.append("---\n\n")

basic_types = ['Object-Related', 'Relationship', 'Attribute-Related', 'Other']

for basic_type in basic_types:
    output.append(f"\n## Basic Hallucination Type: {basic_type}\n\n")

    # Case 1: Vision-only failed, Query token succeeded (2 examples)
    type_case1 = case1[case1['basic_hallucination_type'] == basic_type].head(2)

    if len(type_case1) > 0:
        output.append(f"### Case 1: Vision-only failed ❌ → Query-token succeeded ✅\n\n")

        for idx, row in type_case1.iterrows():
            output.append(f"**Example {idx+1}**\n\n")
            output.append(f"- **Question ID:** `{row['question_id']}`\n")
            output.append(f"- **Image:** `{row['image_id']}`\n")
            output.append(f"- **Question:** {row['question']}\n")
            output.append(f"- **Ground Truth:** {row['ground_truth']}\n")
            output.append(f"- **Model Answer:** {row['model_answer']}\n")
            output.append(f"- **True Label:** {'Hallucination' if row['true_label'] == 1 else 'No Hallucination'}\n")
            output.append(f"- **Domain Type:** {row['domain_type']}\n\n")

            output.append("**Probe Predictions:**\n")
            output.append(f"- Vision-only: {'Hallucination' if row['vision_only_pred'] == 1 else 'No Hallucination'} (prob: {row['vision_only_prob']:.3f}) ❌\n")
            output.append(f"- Vision-token (L47): {'Hallucination' if row['vision_token_pred'] == 1 else 'No Hallucination'} (prob: {row['vision_token_prob']:.3f}) {'✅' if row['vision_token_correct'] == 1 else '❌'}\n")
            output.append(f"- Query-token (L47): {'Hallucination' if row['query_token_pred'] == 1 else 'No Hallucination'} (prob: {row['query_token_prob']:.3f}) ✅\n\n")
            output.append("---\n\n")

    # Case 2: Both vision-only AND vision-token failed, but query token succeeded (1 example)
    type_case2 = case2[case2['basic_hallucination_type'] == basic_type].head(1)

    if len(type_case2) > 0:
        output.append(f"### Case 2: Vision-only ❌ AND Vision-token ❌ → Query-token succeeded ✅\n\n")

        for idx, row in type_case2.iterrows():
            output.append(f"**Example**\n\n")
            output.append(f"- **Question ID:** `{row['question_id']}`\n")
            output.append(f"- **Image:** `{row['image_id']}`\n")
            output.append(f"- **Question:** {row['question']}\n")
            output.append(f"- **Ground Truth:** {row['ground_truth']}\n")
            output.append(f"- **Model Answer:** {row['model_answer']}\n")
            output.append(f"- **True Label:** {'Hallucination' if row['true_label'] == 1 else 'No Hallucination'}\n")
            output.append(f"- **Domain Type:** {row['domain_type']}\n\n")

            output.append("**Probe Predictions:**\n")
            output.append(f"- Vision-only: {'Hallucination' if row['vision_only_pred'] == 1 else 'No Hallucination'} (prob: {row['vision_only_prob']:.3f}) ❌\n")
            output.append(f"- Vision-token (L47): {'Hallucination' if row['vision_token_pred'] == 1 else 'No Hallucination'} (prob: {row['vision_token_prob']:.3f}) ❌\n")
            output.append(f"- Query-token (L47): {'Hallucination' if row['query_token_pred'] == 1 else 'No Hallucination'} (prob: {row['query_token_prob']:.3f}) ✅\n\n")
            output.append("---\n\n")

    # Case 3: Only vision-token succeeded (1 example)
    type_case3 = case3[case3['basic_hallucination_type'] == basic_type].head(1)

    if len(type_case3) > 0:
        output.append(f"### Case 3: Vision-only ❌ AND Query-token ❌ → Vision-token succeeded ✅\n\n")

        for idx, row in type_case3.iterrows():
            output.append(f"**Example**\n\n")
            output.append(f"- **Question ID:** `{row['question_id']}`\n")
            output.append(f"- **Image:** `{row['image_id']}`\n")
            output.append(f"- **Question:** {row['question']}\n")
            output.append(f"- **Ground Truth:** {row['ground_truth']}\n")
            output.append(f"- **Model Answer:** {row['model_answer']}\n")
            output.append(f"- **True Label:** {'Hallucination' if row['true_label'] == 1 else 'No Hallucination'}\n")
            output.append(f"- **Domain Type:** {row['domain_type']}\n\n")

            output.append("**Probe Predictions:**\n")
            output.append(f"- Vision-only: {'Hallucination' if row['vision_only_pred'] == 1 else 'No Hallucination'} (prob: {row['vision_only_prob']:.3f}) ❌\n")
            output.append(f"- Vision-token (L12): {'Hallucination' if row['vision_token_pred'] == 1 else 'No Hallucination'} (prob: {row['vision_token_prob']:.3f}) ✅\n")
            output.append(f"- Query-token (L47): {'Hallucination' if row['query_token_pred'] == 1 else 'No Hallucination'} (prob: {row['query_token_prob']:.3f}) ❌\n\n")
            output.append("---\n\n")

# Write to file
output_path = "/root/akhil/detailed_probe_analysis/gemma_probe_comparison.md"
with open(output_path, 'w', encoding='utf-8') as f:
    f.write(''.join(output))

# Also save the full dataframe for further analysis
df.to_csv('/root/akhil/detailed_probe_analysis/gemma_probe_comparison_full.csv', index=False)

print(f"\n{'='*80}")
print(f"Markdown report saved to: {output_path}")
print(f"Full CSV saved to: /root/akhil/detailed_probe_analysis/gemma_probe_comparison_full.csv")
print('='*80)
