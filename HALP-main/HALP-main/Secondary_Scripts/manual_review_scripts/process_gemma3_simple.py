#!/usr/bin/env python3
"""
Process Gemma 3 12B Hallucination Dataset
SIMPLE VERSION - Uses basic text similarity without sentence transformers
Much faster for initial processing
"""

import pandas as pd
import os
from pathlib import Path
from difflib import SequenceMatcher
from tqdm import tqdm

print("="*80)
print("GEMMA 3 12B - HALLUCINATION DETECTION (SIMPLE VERSION)")
print("="*80)
print()

def text_similarity(text1, text2):
    """Calculate similarity ratio using SequenceMatcher (0-1)"""
    return SequenceMatcher(None, str(text1).lower(), str(text2).lower()).ratio()

def classify_hallucination_simple(row, similarity_threshold=0.5):
    """
    Simple classification based on text similarity ratio
    Returns True if hallucinated (similarity < threshold)
    """
    generated = str(row['model_answer'])
    ground_truth = str(row['ground_truth_answer'])

    # Calculate similarity
    similarity_score = text_similarity(generated, ground_truth)

    # If similarity is too low, it's a hallucination
    return similarity_score < similarity_threshold

# Define paths
base_path = Path('/Users/saiakhil/Documents/Thesis/HALP_EACL')
input_file = base_path / 'Gemma_3' / 'gemma3_hallucination_dataset.csv'
output_dir = base_path / 'Final_CSV_Hallucination'
output_file = output_dir / 'gemma3_hallucination_flagged.csv'

# Create output directory
os.makedirs(output_dir, exist_ok=True)

# Read the CSV file
print(f"Reading input file: {input_file}")
df = pd.read_csv(input_file)
print(f"✓ Loaded {len(df):,} rows\n")

# Apply classification with progress bar
print("Classifying hallucinations (simple text similarity)...")
print("This should take about 1-2 minutes...\n")

tqdm.pandas(desc="Processing")
df['is_hallucinating'] = df.progress_apply(classify_hallucination_simple, axis=1)

print("\n✓ Classification complete!\n")

# Statistics
total = len(df)
hallucinating = df['is_hallucinating'].sum()
not_hallucinating = total - hallucinating

print("=" * 80)
print("HALLUCINATION DETECTION RESULTS - GEMMA 3 12B")
print("=" * 80)
print(f"\nTotal samples:              {total:,}")
print(f"Hallucinated (True):        {hallucinating:,} ({hallucinating/total*100:.2f}%)")
print(f"Not Hallucinated (False):   {not_hallucinating:,} ({not_hallucinating/total*100:.2f}%)")
print()

# Save results
df.to_csv(output_file, index=False)
print(f"✓ Results saved to: {output_file}")
print()

# Preview
print("=" * 80)
print("PREVIEW - First 5 samples:")
print("=" * 80)
for idx in range(min(5, len(df))):
    row = df.iloc[idx]
    print(f"\n[{idx+1}] Question: {row['question'][:70]}...")
    print(f"    Ground Truth: {row['ground_truth_answer'][:80]}")
    print(f"    Model Answer: {row['model_answer'][:80]}")
    print(f"    → {'HALLUCINATED' if row['is_hallucinating'] else 'CORRECT'}")

print()
print("=" * 80)
print("✅ GEMMA 3 12B PROCESSING COMPLETE")
print("=" * 80)
