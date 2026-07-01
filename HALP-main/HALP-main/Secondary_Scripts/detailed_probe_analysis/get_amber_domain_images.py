#!/usr/bin/env python3
"""
Get all image_ids from Amber dataset for specific domain types:
- Knowledge & Identity
- Math & Calculation
- Text & OCR
- General QA
- Temporal & Video
"""
import pandas as pd

# Load metadata
df = pd.read_csv('/root/akhil/final_data/sampled_10k_with_hallucination_types.csv')

print("="*80)
print("AMBER DATASET IMAGES BY DOMAIN TYPE")
print("="*80)

# Filter for Amber dataset only
amber_df = df[df['dataset'] == 'amber'].copy()

print(f"\nTotal samples: {len(df)}")
print(f"Amber samples: {len(amber_df)}")

# Target domain types
target_domains = [
    'Knowledge & Identity',
    'Math & Calculation',
    'Text & OCR',
    'General QA',
    'Temporal & Video'
]

output = []
output.append("# Amber Dataset Images by Domain Type\n\n")
output.append("---\n\n")

all_images = []

for domain in target_domains:
    # Filter for this domain type
    domain_df = amber_df[amber_df['domain_type'] == domain]

    # Get unique image names
    unique_images = domain_df['image_name'].unique()

    output.append(f"## {domain}\n\n")
    output.append(f"**Total questions:** {len(domain_df)}\n")
    output.append(f"**Unique images:** {len(unique_images)}\n\n")

    if len(unique_images) > 0:
        output.append("**Image IDs:**\n")
        for img in sorted(unique_images):
            output.append(f"- `{img}`\n")
            all_images.append({'domain_type': domain, 'image_name': img})
        output.append("\n")
    else:
        output.append("_No images found for this domain type_\n\n")

    output.append("---\n\n")

    print(f"\n{domain}: {len(unique_images)} unique images")

# Summary
output.append(f"\n## Summary\n\n")
output.append(f"- Total unique images across all target domains: {len(set([x['image_name'] for x in all_images]))}\n")

# Write to file
output_path = "/root/akhil/detailed_probe_analysis/amber_domain_images.md"
with open(output_path, 'w', encoding='utf-8') as f:
    f.write(''.join(output))

# Save as CSV
all_images_df = pd.DataFrame(all_images)
csv_path = "/root/akhil/detailed_probe_analysis/amber_domain_images.csv"
all_images_df.to_csv(csv_path, index=False)

print(f"\n{'='*80}")
print(f"Markdown report: {output_path}")
print(f"CSV file: {csv_path}")
print(f"Total unique images: {len(set([x['image_name'] for x in all_images]))}")
print('='*80)
