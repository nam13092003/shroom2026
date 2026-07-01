#!/usr/bin/env python3
"""
Copy all images used in mixed hallucination examples to a new folder
"""
import pandas as pd
import os
import shutil
from pathlib import Path

# Load the Excel file to get the list of images
excel_path = '/root/akhil/detailed_probe_analysis/mixed_hallucination_examples.xlsx'
df = pd.read_excel(excel_path, sheet_name='Mixed Examples')

# Get unique image names
unique_images = df['Image'].unique()

print(f"Found {len(unique_images)} unique images in the examples")

# Create output directory
output_dir = "/root/akhil/detailed_probe_analysis/mixed_example_images"
os.makedirs(output_dir, exist_ok=True)

# Common image directories to search
image_search_paths = [
    '/root/akhil/final_data/images',
    '/root/akhil/HALP_EACL_Models/images',
    '/root/akhil/images',
    '/root/akhil/final_data',
]

# Also look in subdirectories
for base_path in ['/root/akhil/final_data', '/root/akhil']:
    if os.path.exists(base_path):
        for root, dirs, files in os.walk(base_path):
            if 'image' in root.lower() or 'img' in root.lower():
                if root not in image_search_paths:
                    image_search_paths.append(root)

print(f"\nSearching in {len(image_search_paths)} directories...")

copied_count = 0
not_found = []

for image_name in unique_images:
    found = False

    # Search in all paths
    for search_path in image_search_paths:
        if not os.path.exists(search_path):
            continue

        image_path = os.path.join(search_path, image_name)

        if os.path.exists(image_path):
            # Copy the image
            dest_path = os.path.join(output_dir, image_name)
            shutil.copy2(image_path, dest_path)
            print(f"✓ Copied: {image_name}")
            copied_count += 1
            found = True
            break

    if not found:
        not_found.append(image_name)

print(f"\n{'='*80}")
print(f"SUMMARY")
print('='*80)
print(f"Total images needed: {len(unique_images)}")
print(f"Successfully copied: {copied_count}")
print(f"Not found: {len(not_found)}")

if not_found:
    print(f"\nImages not found:")
    for img in not_found:
        print(f"  - {img}")

    # Save list of missing images
    with open(os.path.join(output_dir, 'missing_images.txt'), 'w') as f:
        for img in not_found:
            f.write(f"{img}\n")
    print(f"\nList saved to: {output_dir}/missing_images.txt")

print(f"\nImages copied to: {output_dir}")
print('='*80)
