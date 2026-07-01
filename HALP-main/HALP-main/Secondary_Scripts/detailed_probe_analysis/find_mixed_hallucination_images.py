#!/usr/bin/env python3
"""
Find images where the model hallucinated on some questions but not others
This shows cases where the model's behavior is inconsistent for the same image
"""
import pandas as pd
import os

# Model CSV files
MODEL_CSVS = {
    'Gemma3-12B': '/root/akhil/FInal_CSV_Hallucination/gemma3_manually_reviewed.csv',
    'FastVLM-7B': '/root/akhil/FInal_CSV_Hallucination/fastvlm_manually_reviewed.csv',
    'LLaVA-Next-8B': '/root/akhil/FInal_CSV_Hallucination/llava_manually_reviewed.csv',
    'Molmo-V1': '/root/akhil/FInal_CSV_Hallucination/molmo_manually_reviewed.csv',
    'Qwen2.5-VL-7B': '/root/akhil/FInal_CSV_Hallucination/qwen25vl_manually_reviewed.csv',
    'SmolVLM2-2.2B': '/root/akhil/FInal_CSV_Hallucination/smolvlm_manually_reviewed.csv',
    'Llama-3.2-11B': '/root/akhil/FInal_CSV_Hallucination/llama32_manually_reviewed.csv',
    'Phi4-VL': '/root/akhil/FInal_CSV_Hallucination/phi4vl_manually_reviewed.csv',
}

print("="*80)
print("FINDING IMAGES WITH MIXED HALLUCINATION PATTERNS")
print("="*80)
print("\nLooking for images where model hallucinates on some questions but not others\n")

all_results = []

for model_name, csv_path in MODEL_CSVS.items():
    print(f"\n{'='*80}")
    print(f"Model: {model_name}")
    print('='*80)

    # Load CSV
    df = pd.read_csv(csv_path, low_memory=False)

    # Convert hallucination label to boolean
    df['is_hallucinating'] = df['is_hallucinating_manual'].apply(
        lambda x: True if (isinstance(x, str) and x.lower() in ['true', '1', 'yes']) or x == True or x == 1 else False
    )

    # Group by image_id
    image_groups = df.groupby('image_id')

    mixed_images = []

    for image_id, group in image_groups:
        # Check if there are both hallucinations and non-hallucinations
        has_hallucination = group['is_hallucinating'].any()
        has_no_hallucination = (~group['is_hallucinating']).any()

        if has_hallucination and has_no_hallucination:
            num_hallucinated = group['is_hallucinating'].sum()
            num_no_hallucination = (~group['is_hallucinating']).sum()
            total_questions = len(group)

            hall_rate = num_hallucinated / total_questions
            mixed_images.append({
                'model': model_name,
                'image_id': image_id,
                'total_questions': total_questions,
                'hallucinated_questions': int(num_hallucinated),
                'no_hallucination_questions': int(num_no_hallucination),
                'hallucination_rate': hall_rate,
                'balance_score': abs(hall_rate - 0.5)
            })

    if mixed_images:
        # Sort by most balanced (closest to 50/50 split)
        mixed_images_df = pd.DataFrame(mixed_images)
        mixed_images_df['balance_score'] = abs(mixed_images_df['hallucination_rate'] - 0.5)
        mixed_images_df = mixed_images_df.sort_values('balance_score')

        print(f"\nFound {len(mixed_images)} images with mixed hallucination patterns")
        print(f"\nTop 5 most balanced cases (closest to 50/50 split):")
        print("-" * 80)

        for idx, row in mixed_images_df.head(5).iterrows():
            print(f"\nImage ID: {row['image_id']}")
            print(f"  Total questions: {row['total_questions']}")
            print(f"  Hallucinated: {row['hallucinated_questions']} ({row['hallucination_rate']*100:.1f}%)")
            print(f"  No hallucination: {row['no_hallucination_questions']} ({(1-row['hallucination_rate'])*100:.1f}%)")

            # Show example questions
            image_data = df[df['image_id'] == row['image_id']]

            # Get one hallucinated question
            hall_example = image_data[image_data['is_hallucinating'] == True].iloc[0] if len(image_data[image_data['is_hallucinating'] == True]) > 0 else None
            # Get one non-hallucinated question
            no_hall_example = image_data[image_data['is_hallucinating'] == False].iloc[0] if len(image_data[image_data['is_hallucinating'] == False]) > 0 else None

            if hall_example is not None:
                print(f"\n  Example HALLUCINATED question:")
                print(f"    Q: {hall_example['question'][:100]}...")
                if 'model_answer' in hall_example:
                    print(f"    Model A: {str(hall_example['model_answer'])[:100]}...")
                if 'ground_truth_answer' in hall_example:
                    print(f"    Truth: {str(hall_example['ground_truth_answer'])[:80]}...")
                print(f"    Question ID: {hall_example['question_id']}")

            if no_hall_example is not None:
                print(f"\n  Example NO HALLUCINATION question:")
                print(f"    Q: {no_hall_example['question'][:100]}...")
                if 'model_answer' in no_hall_example:
                    print(f"    Model A: {str(no_hall_example['model_answer'])[:100]}...")
                if 'ground_truth_answer' in no_hall_example:
                    print(f"    Truth: {str(no_hall_example['ground_truth_answer'])[:80]}...")
                print(f"    Question ID: {no_hall_example['question_id']}")

        all_results.extend(mixed_images)
    else:
        print(f"\nNo images found with mixed patterns")

# Save all results
if all_results:
    output_path = "/root/akhil/detailed_probe_analysis/mixed_hallucination_images.csv"
    results_df = pd.DataFrame(all_results)
    results_df = results_df.sort_values(['model', 'balance_score'])
    results_df.to_csv(output_path, index=False)

    print("\n" + "="*80)
    print("SUMMARY STATISTICS")
    print("="*80)

    for model_name in results_df['model'].unique():
        model_data = results_df[results_df['model'] == model_name]
        print(f"\n{model_name}:")
        print(f"  Total images with mixed patterns: {len(model_data)}")
        print(f"  Avg hallucination rate: {model_data['hallucination_rate'].mean()*100:.1f}%")
        print(f"  Most balanced image: {model_data.iloc[0]['image_id']}")

    print("\n" + "="*80)
    print(f"Results saved to: {output_path}")
    print("="*80)
else:
    print("\nNo mixed hallucination images found across any model")
