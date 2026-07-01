#!/usr/bin/env python3
"""
Get 5 images for each domain type with their associated questions
"""
import pandas as pd

# Load metadata
df = pd.read_csv('/root/akhil/final_data/sampled_10k_with_hallucination_types.csv')

# Target images per domain
target_images = {
    'Knowledge & Identity': [
        'mme_celebrity_tt0076759_shot_0930_img_0.jpg',
        'mme_celebrity_tt0090022_shot_0464_img_0.jpg',
        'mme_celebrity_tt0086856_shot_0929_img_0.jpg',
        'mme_scene_Places365_val_00000130.jpg',
        'mme_celebrity_tt0119008_shot_0979_img_0.jpg'
    ],
    'Math & Calculation': [
        'math_vista_2527.jpg',
        'hallusionbench_figure_14_0.png',
        'mme_numerical_calculation_0003.png',
        'math_vista_4544.jpg',
        'math_vista_522.jpg'
    ],
    'Text & OCR': [
        'hallusionbench_ocr_12_2.png',
        'haloquest_1513.png',
        'mme_posters_tt1438176.jpg',
        'hallusionbench_ocr_0_0.png',
        'hallusionbench_ocr_0_1.png'
    ],
    'Temporal & Video': [
        'hallusionbench_video_3_1.png',
        'hallusionbench_video_16_0.png',
        'hallusionbench_video_16_1.png',
        'hallusionbench_video_9_0.png',
        'hallusionbench_video_3_2.png'
    ]
}

print("="*80)
print("IMAGES WITH ASSOCIATED QUESTIONS")
print("="*80)

for domain, images in target_images.items():
    print(f"\n{'='*80}")
    print(f"## {domain}")
    print('='*80)

    for idx, image_name in enumerate(images, 1):
        # Get all questions for this image
        image_df = df[df['image_name'] == image_name]

        print(f"\n{idx}. **Image:** `{image_name}`")
        print(f"   **Dataset:** {image_df['dataset'].iloc[0] if len(image_df) > 0 else 'Unknown'}")
        print(f"   **Total questions:** {len(image_df)}")
        print(f"\n   **Questions:**")

        for i, (_, row) in enumerate(image_df.iterrows(), 1):
            print(f"   {i}. Q: {row['question']}")
            print(f"      Ground Truth: {row['gt_answer']}")
            print(f"      Question ID: {row['question_id']}")
            print()
