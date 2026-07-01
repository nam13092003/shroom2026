#!/usr/bin/env python3
"""
Get all General QA questions and images from Amber dataset
"""
import pandas as pd

# Load metadata
df = pd.read_csv('/root/akhil/final_data/sampled_10k_with_hallucination_types.csv')

# Filter for Amber dataset and General QA domain
amber_general_qa = df[(df['dataset'] == 'amber') & (df['domain_type'] == 'General QA')].copy()

print("="*80)
print("AMBER DATASET - GENERAL QA")
print("="*80)
print(f"\nTotal General QA questions from Amber: {len(amber_general_qa)}")
print(f"Unique images: {amber_general_qa['image_name'].nunique()}")

# Get unique images
unique_images = amber_general_qa['image_name'].unique()

print(f"\n{'='*80}")
print("IMAGES WITH QUESTIONS")
print('='*80)

for idx, image_name in enumerate(sorted(unique_images), 1):
    # Get all questions for this image
    image_questions = amber_general_qa[amber_general_qa['image_name'] == image_name]

    print(f"\n{idx}. **Image:** `{image_name}`")
    print(f"   **Total questions:** {len(image_questions)}")
    print(f"\n   **Questions:**")

    for i, (_, row) in enumerate(image_questions.iterrows(), 1):
        print(f"   {i}. Q: {row['question']}")
        print(f"      GT: {row['gt_answer']}")
        print(f"      Question ID: {row['question_id']}")
        print()

print("\n" + "="*80)
print(f"Total: {len(unique_images)} images, {len(amber_general_qa)} questions")
print("="*80)
