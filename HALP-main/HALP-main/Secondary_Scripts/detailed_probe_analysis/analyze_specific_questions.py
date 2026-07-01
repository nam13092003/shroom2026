#!/usr/bin/env python3
"""
Analyze specific questions: Get Gemma answers and probe AUROC scores
"""
import pandas as pd
import numpy as np
import torch
import h5py
import os
import sys
import glob
from sklearn.metrics import roc_auc_score

sys.path.insert(0, '/root/akhil/probe_analysis')

from analyze_probe_by_category import (
    load_hallucination_labels,
    load_embeddings_from_h5,
    HallucinationProbe,
    get_predictions
)

# Target questions with image IDs
target_questions = [
    ('Is there direct contact between the egg and blueberry?', 'AMBER_157.jpg'),
    ('Is the answer to the arithmetic question in the image 65?', 'mme_numerical_calculation_0003.png'),
    ('Are there two footballs in this image?', 'AMBER_132.jpg'),
    ('Is there a beach in this image?', 'AMBER_17.jpg'),
    ('Does the image show "Hot dry noodles from Wuhan"?', 'hallusionbench_ocr_0_0.png'),
    ('Describe this image.', 'AMBER_484.jpg'),
    ('Is the actor inside the red bounding box called Harrison Ford?', 'mme_celebrity_tt0076759_shot_0930_img_0.jpg'),
    ('According to the positive sequence of the images, does the man open the door?', 'hallusionbench_video_3_1.png'),
    ('Does the person stand in this image?', 'AMBER_389.jpg'),
    ('Is there a person in this image?', 'AMBER_868.jpg'),
    ('Is there direct contact between the bat and grass?', 'AMBER_778.jpg'),
    ('Is the forest withering in this image?', 'AMBER_348.jpg')
]

print("="*80)
print("ANALYZING SPECIFIC QUESTIONS")
print("="*80)

# Load metadata
metadata_df = pd.read_csv('/root/akhil/final_data/sampled_10k_with_hallucination_types.csv')

# Load Gemma CSV
gemma_csv = pd.read_csv('/root/akhil/FInal_CSV_Hallucination/gemma3_manually_reviewed.csv', low_memory=False)

# Load Gemma labels
labels_dict = load_hallucination_labels('/root/akhil/FInal_CSV_Hallucination/gemma3_manually_reviewed.csv')

# Find question IDs
found_questions = []
for question_text, image_id in target_questions:
    # Clean up question text for matching
    q_clean = question_text.strip().lower()

    # Try exact match first
    match = metadata_df[
        (metadata_df['question'].str.lower().str.strip() == q_clean) &
        (metadata_df['image_name'] == image_id)
    ]

    # If no exact match, try contains
    if len(match) == 0:
        match = metadata_df[
            (metadata_df['question'].str.lower().str.contains(q_clean[:20], na=False)) &
            (metadata_df['image_name'] == image_id)
        ]

    if len(match) > 0:
        question_id = match.iloc[0]['question_id']

        # Get Gemma's answer
        gemma_row = gemma_csv[gemma_csv['question_id'] == question_id]
        if len(gemma_row) > 0:
            gemma_answer = gemma_row.iloc[0]['model_answer']
            is_hallucinating = gemma_row.iloc[0]['is_hallucinating_manual']
            ground_truth = gemma_row.iloc[0]['ground_truth_answer']

            found_questions.append({
                'question_id': question_id,
                'image_id': image_id,
                'question': match.iloc[0]['question'],
                'ground_truth': ground_truth,
                'gemma_answer': gemma_answer,
                'is_hallucinating': is_hallucinating,
                'basic_hallucination_type': match.iloc[0].get('basic_hallucination_type', 'Unknown'),
                'domain_type': match.iloc[0].get('domain_type', 'Unknown')
            })
            print(f"✓ Found: {question_id} ({image_id})")
        else:
            print(f"✗ Question ID {question_id} not found in Gemma CSV")
    else:
        print(f"✗ Not found: {question_text[:50]}... ({image_id})")

print(f"\nFound {len(found_questions)} questions")

# Load probe predictions
print("\n" + "="*80)
print("LOADING PROBE PREDICTIONS")
print("="*80)

GEMMA_CONFIG = {
    "name": "Gemma3-12B",
    "h5_dir": "/root/akhil/HALP_EACL_Models/Models/Gemma3_12B/gemma_output",
    "csv_path": "/root/akhil/FInal_CSV_Hallucination/gemma3_manually_reviewed.csv",
}

# Get question IDs
target_qids = [q['question_id'] for q in found_questions]

# Load vision-only probe predictions
print("\nLoading vision-only probe...")
vision_only_embeddings, vision_only_labels, vision_only_qids = load_embeddings_from_h5(
    GEMMA_CONFIG["h5_dir"],
    'vision_only_representation',
    labels_dict
)

vision_only_probe = torch.load(
    '/root/akhil/probe_training_scripts/gemma_model_probe/results/vision_only/probe_model.pt',
    map_location='cpu'
)
vo_model = HallucinationProbe(
    input_dim=vision_only_probe['input_dim'],
    layer_sizes=[512, 256, 128],
    dropout_rate=0.3
)
vo_model.load_state_dict(vision_only_probe['model_state_dict'])
vo_model.eval()

with torch.no_grad():
    vo_probs = vo_model(torch.tensor(vision_only_embeddings, dtype=torch.float32)).numpy()

# Load vision-token layer 47 probe predictions
print("Loading vision-token layer 47 probe...")
vt_embeddings, vt_labels, vt_qids = load_embeddings_from_h5(
    GEMMA_CONFIG["h5_dir"],
    'vision_token_representation',
    labels_dict,
    layer_name='layer_47'
)

vt_probe = torch.load(
    '/root/akhil/probe_training_scripts/gemma_model_probe/results/vision_token_layer_n/probe_model.pt',
    map_location='cpu'
)
vt_model = HallucinationProbe(
    input_dim=vt_probe['input_dim'],
    layer_sizes=[512, 256, 128],
    dropout_rate=0.3
)
vt_model.load_state_dict(vt_probe['model_state_dict'])
vt_model.eval()

with torch.no_grad():
    vt_probs = vt_model(torch.tensor(vt_embeddings, dtype=torch.float32)).numpy()

# Load query-token layer 47 probe predictions
print("Loading query-token layer 47 probe...")
qt_embeddings, qt_labels, qt_qids = load_embeddings_from_h5(
    GEMMA_CONFIG["h5_dir"],
    'query_token_representation',
    labels_dict,
    layer_name='layer_47'
)

qt_probe = torch.load(
    '/root/akhil/probe_training_scripts/gemma_model_probe/results/query_token_layer_n/probe_model.pt',
    map_location='cpu'
)
qt_model = HallucinationProbe(
    input_dim=qt_probe['input_dim'],
    layer_sizes=[512, 256, 128],
    dropout_rate=0.3
)
qt_model.load_state_dict(qt_probe['model_state_dict'])
qt_model.eval()

with torch.no_grad():
    qt_probs = qt_model(torch.tensor(qt_embeddings, dtype=torch.float32)).numpy()

# Create lookup dictionaries
vo_dict = {qid: (vision_only_labels[i], vo_probs[i]) for i, qid in enumerate(vision_only_qids)}
vt_dict = {qid: (vt_labels[i], vt_probs[i]) for i, qid in enumerate(vt_qids)}
qt_dict = {qid: (qt_labels[i], qt_probs[i]) for i, qid in enumerate(qt_qids)}

# Extract predictions for target questions
results = []
for q in found_questions:
    qid = q['question_id']

    result = {
        'question_id': qid,
        'image_id': q['image_id'],
        'question': q['question'],
        'ground_truth': q['ground_truth'],
        'gemma_answer': q['gemma_answer'],
        'is_hallucinating': q['is_hallucinating'],
        'basic_hallucination_type': q['basic_hallucination_type'],
        'domain_type': q['domain_type']
    }

    if qid in vo_dict:
        result['vision_only_label'] = vo_dict[qid][0]
        result['vision_only_prob'] = vo_dict[qid][1]

    if qid in vt_dict:
        result['vision_token_label'] = vt_dict[qid][0]
        result['vision_token_prob'] = vt_dict[qid][1]

    if qid in qt_dict:
        result['query_token_label'] = qt_dict[qid][0]
        result['query_token_prob'] = qt_dict[qid][1]

    results.append(result)

# Create DataFrame
df = pd.DataFrame(results)

# Calculate AUROC for these specific questions
print("\n" + "="*80)
print("PROBE AUROC SCORES ON THESE 12 QUESTIONS")
print("="*80)

labels = df['vision_only_label'].values if 'vision_only_label' in df.columns else None

if labels is not None and len(np.unique(labels)) > 1:
    vo_auroc = roc_auc_score(df['vision_only_label'], df['vision_only_prob'])
    vt_auroc = roc_auc_score(df['vision_token_label'], df['vision_token_prob'])
    qt_auroc = roc_auc_score(df['query_token_label'], df['query_token_prob'])

    print(f"Vision-only probe:          AUROC = {vo_auroc:.4f}")
    print(f"Vision-token (L47) probe:   AUROC = {vt_auroc:.4f}")
    print(f"Query-token (L47) probe:    AUROC = {qt_auroc:.4f}")
else:
    print("Cannot calculate AUROC - only one class present or missing data")

# Print detailed results
print("\n" + "="*80)
print("DETAILED RESULTS")
print("="*80)

for i, row in df.iterrows():
    print(f"\n{i+1}. {row['image_id']}")
    print(f"   Question: {row['question']}")
    print(f"   Ground Truth: {row['ground_truth']}")
    print(f"   Gemma Answer: {row['gemma_answer'][:200]}...")
    print(f"   Is Hallucinating: {row['is_hallucinating']}")
    print(f"   Type: {row['basic_hallucination_type']} / {row['domain_type']}")
    print(f"   Probe Predictions (hallucination probability):")
    print(f"     - Vision-only:    {row.get('vision_only_prob', 'N/A'):.4f}" if 'vision_only_prob' in row else "     - Vision-only: N/A")
    print(f"     - Vision-token:   {row.get('vision_token_prob', 'N/A'):.4f}" if 'vision_token_prob' in row else "     - Vision-token: N/A")
    print(f"     - Query-token:    {row.get('query_token_prob', 'N/A'):.4f}" if 'query_token_prob' in row else "     - Query-token: N/A")

# Save to CSV
output_csv = "/root/akhil/detailed_probe_analysis/specific_questions_analysis.csv"
df.to_csv(output_csv, index=False)

print("\n" + "="*80)
print(f"Results saved to: {output_csv}")
print("="*80)
