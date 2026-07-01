"""
Verify H5 file access for vision_only_representation
"""

import h5py
import pandas as pd
import numpy as np
import glob
from tqdm import tqdm

# Paths
H5_DIR = "/root/akhil/HALP_EACL_Models/Models/Gemma3_12B/gemma_output"
CSV_PATH = "/root/akhil/FInal_CSV_Hallucination/gemma3_manually_reviewed.csv"
EMBEDDING_TYPE = "vision_only_representation"
TARGET_COLUMN = "is_hallucinating_manual"

print("=" * 80)
print("VERIFYING H5 FILE ACCESS")
print("=" * 80)

# Load labels
print(f"\n1. Loading labels from CSV...")
df = pd.read_csv(CSV_PATH, low_memory=False)
print(f"   Loaded {len(df)} labels from CSV")

labels_dict = {}
for _, row in df.iterrows():
    question_id = row['question_id']
    target_value = row[TARGET_COLUMN]
    if isinstance(target_value, str):
        target_value = target_value.lower() in ['true', '1', 'yes']
    else:
        target_value = bool(target_value)

    labels_dict[question_id] = int(target_value)

print(f"   Created {len(labels_dict)} labels")
print(f"   Sample question_ids: {list(labels_dict.keys())[:5]}")

# Find H5 files
print(f"\n2. Finding H5 files...")
h5_files = sorted(glob.glob(f"{H5_DIR}/*.h5"))
print(f"   Found {len(h5_files)} H5 files")
for i, f in enumerate(h5_files[:3], 1):
    print(f"   {i}. {f}")
if len(h5_files) > 3:
    print(f"   ... and {len(h5_files) - 3} more")

# Test accessing embeddings
print(f"\n3. Testing H5 file access...")
print(f"   Looking for: '{EMBEDDING_TYPE}'")

embeddings_found = 0
embeddings_list = []
labels_list = []
question_ids_list = []

# Check first H5 file in detail
print(f"\n4. Detailed inspection of first H5 file:")
first_h5 = h5_files[0]
print(f"   File: {first_h5}")

with h5py.File(first_h5, 'r') as f:
    question_ids_in_file = list(f.keys())
    print(f"   Number of samples in file: {len(question_ids_in_file)}")
    print(f"   First 5 question_ids: {question_ids_in_file[:5]}")

    # Check first sample
    first_qid = question_ids_in_file[0]
    print(f"\n   Inspecting sample: {first_qid}")
    sample_group = f[first_qid]
    print(f"   Keys in sample group: {list(sample_group.keys())}")

    # Check if vision_only_representation exists
    if EMBEDDING_TYPE in sample_group:
        print(f"   ✅ Found '{EMBEDDING_TYPE}'")
        embedding = sample_group[EMBEDDING_TYPE][:]
        print(f"   Shape: {embedding.shape}")
        print(f"   Dtype: {embedding.dtype}")
        print(f"   Min value: {embedding.min():.4f}")
        print(f"   Max value: {embedding.max():.4f}")
        print(f"   Mean value: {embedding.mean():.4f}")
        print(f"   First 10 values: {embedding[:10]}")
    else:
        print(f"   ❌ '{EMBEDDING_TYPE}' NOT found in sample")
        print(f"   Available keys: {list(sample_group.keys())}")

# Load all embeddings
print(f"\n5. Loading all embeddings from all H5 files...")

for h5_file in tqdm(h5_files, desc="   Processing H5 files"):
    with h5py.File(h5_file, 'r') as f:
        for question_id in f.keys():
            # Skip if no label
            if question_id not in labels_dict:
                continue

            sample_group = f[question_id]

            # Try to extract vision_only_representation
            try:
                if EMBEDDING_TYPE in sample_group:
                    embedding = sample_group[EMBEDDING_TYPE][:]

                    embeddings_list.append(embedding)
                    labels_list.append(labels_dict[question_id])
                    question_ids_list.append(question_id)
                    embeddings_found += 1
            except Exception as e:
                print(f"   ⚠️  Error loading {question_id}: {e}")

print(f"\n6. Summary:")
print(f"   Total embeddings found: {embeddings_found}")
print(f"   Total labels matched: {len(embeddings_list)}")

if len(embeddings_list) > 0:
    embeddings_array = np.stack(embeddings_list)
    labels_array = np.array(labels_list)

    print(f"\n7. Final arrays:")
    print(f"   Embeddings shape: {embeddings_array.shape}")
    print(f"   Labels shape: {labels_array.shape}")
    print(f"   Embedding dimension: {embeddings_array.shape[1]}")

    print(f"\n8. Label distribution:")
    class_0_count = (labels_array == 0).sum()
    class_1_count = (labels_array == 1).sum()
    print(f"   Class 0 (No Hallucination): {class_0_count} ({class_0_count/len(labels_array)*100:.1f}%)")
    print(f"   Class 1 (Hallucination):    {class_1_count} ({class_1_count/len(labels_array)*100:.1f}%)")

    print(f"\n9. Sample matching check:")
    print(f"   Question ID | Label | Embedding shape")
    print(f"   " + "-" * 50)
    for i in range(min(5, len(question_ids_list))):
        print(f"   {question_ids_list[i]:<15} | {labels_list[i]} | {embeddings_list[i].shape}")

    print("\n" + "=" * 80)
    print("✅ VERIFICATION SUCCESSFUL!")
    print("=" * 80)
    print(f"Successfully loaded {embeddings_found} embeddings")
    print(f"Embedding dimension: {embeddings_array.shape[1]}")
    print(f"Ready for training!")

else:
    print("\n" + "=" * 80)
    print("❌ VERIFICATION FAILED!")
    print("=" * 80)
    print("No embeddings were loaded. Please check:")
    print(f"1. H5 files exist in: {H5_DIR}")
    print(f"2. Embedding type '{EMBEDDING_TYPE}' exists in H5 files")
    print(f"3. Question IDs match between CSV and H5 files")
