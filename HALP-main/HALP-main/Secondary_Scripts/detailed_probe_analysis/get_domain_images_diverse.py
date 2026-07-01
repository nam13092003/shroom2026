#!/usr/bin/env python3
"""
Get 5 images for each domain type from different datasets:
- Knowledge & Identity
- Math & Calculation
- Text & OCR
- Temporal & Video
"""
import pandas as pd

# Load metadata
df = pd.read_csv('/root/akhil/final_data/sampled_10k_with_hallucination_types.csv')

print("="*80)
print("DIVERSE DATASET IMAGES BY DOMAIN TYPE")
print("="*80)

# Target domain types
target_domains = [
    'Knowledge & Identity',
    'Math & Calculation',
    'Text & OCR',
    'Temporal & Video'
]

results = {}

for domain in target_domains:
    # Filter for this domain type
    domain_df = df[df['domain_type'] == domain]

    print(f"\n{domain}:")
    print(f"  Total questions: {len(domain_df)}")
    print(f"  Datasets: {domain_df['dataset'].value_counts().to_dict()}")

    # Get diverse images - try to get from different datasets
    selected_images = []
    datasets_used = set()

    # First pass: get one from each dataset
    for dataset in domain_df['dataset'].unique():
        dataset_images = domain_df[domain_df['dataset'] == dataset]['image_name'].unique()
        if len(dataset_images) > 0:
            selected_images.append({
                'domain_type': domain,
                'image_name': dataset_images[0],
                'dataset': dataset
            })
            datasets_used.add(dataset)
            if len(selected_images) >= 5:
                break

    # Second pass: if we need more, cycle through datasets
    if len(selected_images) < 5:
        for dataset in domain_df['dataset'].unique():
            dataset_images = domain_df[domain_df['dataset'] == dataset]['image_name'].unique()
            # Skip first one (already added)
            for img in dataset_images[1:]:
                if len(selected_images) >= 5:
                    break
                selected_images.append({
                    'domain_type': domain,
                    'image_name': img,
                    'dataset': dataset
                })
            if len(selected_images) >= 5:
                break

    results[domain] = selected_images[:5]

    print(f"  Selected {len(results[domain])} images:")
    for item in results[domain]:
        print(f"    - {item['image_name']} ({item['dataset']})")

# Print formatted output
print("\n" + "="*80)
print("FORMATTED OUTPUT")
print("="*80)

for domain in target_domains:
    print(f"\n## {domain}")
    if domain in results and len(results[domain]) > 0:
        for i, item in enumerate(results[domain], 1):
            print(f"{i}. `{item['image_name']}` (from {item['dataset']} dataset)")
    else:
        print("No images found")

print("\n" + "="*80)
