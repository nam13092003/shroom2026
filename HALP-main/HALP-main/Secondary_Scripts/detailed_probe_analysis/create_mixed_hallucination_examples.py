#!/usr/bin/env python3
"""
Create markdown file with mixed hallucination examples
One example per basic_hallucination_type and domain_type for each model
"""
import pandas as pd
import os

# Load the mixed hallucination images CSV
mixed_images_df = pd.read_csv('/root/akhil/detailed_probe_analysis/mixed_hallucination_images.csv')

# Load detailed metadata
metadata_df = pd.read_csv('/root/akhil/final_data/sampled_10k_with_hallucination_types.csv')

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

# Create metadata lookup
metadata_lookup = {}
for _, row in metadata_df.iterrows():
    metadata_lookup[row['question_id']] = {
        'basic_hallucination_type': row.get('basic_hallucination_type', 'Unknown'),
        'domain_type': row.get('domain_type', 'Unknown'),
        'answer_type': row.get('answer_type', 'Unknown')
    }

print("Creating mixed hallucination examples markdown...")

output_md = []
output_md.append("# Mixed Hallucination Examples\n")
output_md.append("Examples of images where models showed inconsistent behavior - hallucinating on some questions but not others.\n")
output_md.append("One example per basic_hallucination_type and domain_type for each model.\n")
output_md.append("\n---\n")

for model_name, csv_path in MODEL_CSVS.items():
    print(f"\nProcessing {model_name}...")

    output_md.append(f"\n## {model_name}\n")

    # Load model CSV
    model_df = pd.read_csv(csv_path, low_memory=False)

    # Convert hallucination label
    model_df['is_hallucinating'] = model_df['is_hallucinating_manual'].apply(
        lambda x: True if (isinstance(x, str) and x.lower() in ['true', '1', 'yes']) or x == True or x == 1 else False
    )

    # Get mixed images for this model
    model_mixed = mixed_images_df[mixed_images_df['model'] == model_name]

    if len(model_mixed) == 0:
        output_md.append("No mixed hallucination patterns found.\n")
        continue

    # Add metadata to model_df
    model_df['basic_hallucination_type'] = model_df['question_id'].map(
        lambda qid: metadata_lookup.get(qid, {}).get('basic_hallucination_type', 'Unknown')
    )
    model_df['domain_type'] = model_df['question_id'].map(
        lambda qid: metadata_lookup.get(qid, {}).get('domain_type', 'Unknown')
    )

    # Track which types we've covered
    covered_basic_types = set()
    covered_domain_types = set()

    examples_found = 0

    # Iterate through mixed images (sorted by most balanced)
    for _, mixed_img in model_mixed.iterrows():
        if examples_found >= 15:  # Limit examples per model
            break

        image_id = mixed_img['image_id']

        # Get all questions for this image
        image_questions = model_df[model_df['image_id'] == image_id]

        # Get hallucinated questions
        hall_questions = image_questions[image_questions['is_hallucinating'] == True]
        # Get non-hallucinated questions
        no_hall_questions = image_questions[image_questions['is_hallucinating'] == False]

        # Try to find a pair with uncovered types
        for _, hall_q in hall_questions.iterrows():
            basic_type = hall_q['basic_hallucination_type']
            domain_type = hall_q['domain_type']

            # Check if this type combination is new
            if basic_type not in covered_basic_types or domain_type not in covered_domain_types:
                # Find a matching non-hallucinated question from same image
                if len(no_hall_questions) > 0:
                    no_hall_q = no_hall_questions.iloc[0]

                    # Add this example
                    output_md.append(f"\n### Image: `{image_id}`\n")
                    output_md.append(f"**Total questions on this image:** {len(image_questions)} "
                                   f"({int(mixed_img['hallucinated_questions'])} hallucinated, "
                                   f"{int(mixed_img['no_hallucination_questions'])} correct)\n")

                    # Hallucinated question
                    output_md.append(f"\n#### ❌ Hallucinated Question\n")
                    output_md.append(f"- **Question ID:** `{hall_q['question_id']}`\n")
                    output_md.append(f"- **Question:** {hall_q['question']}\n")
                    output_md.append(f"- **Ground Truth:** {hall_q['ground_truth_answer']}\n")
                    output_md.append(f"- **Model Answer:** {hall_q['model_answer']}\n")
                    output_md.append(f"- **Basic Hallucination Type:** {basic_type}\n")
                    output_md.append(f"- **Domain Type:** {domain_type}\n")

                    # Non-hallucinated question
                    output_md.append(f"\n#### ✅ Correct Question (Same Image)\n")
                    output_md.append(f"- **Question ID:** `{no_hall_q['question_id']}`\n")
                    output_md.append(f"- **Question:** {no_hall_q['question']}\n")
                    output_md.append(f"- **Ground Truth:** {no_hall_q['ground_truth_answer']}\n")
                    output_md.append(f"- **Model Answer:** {no_hall_q['model_answer']}\n")

                    no_hall_basic = no_hall_q['basic_hallucination_type']
                    no_hall_domain = no_hall_q['domain_type']
                    if no_hall_basic != 'Unknown':
                        output_md.append(f"- **Basic Hallucination Type:** {no_hall_basic}\n")
                    if no_hall_domain != 'Unknown':
                        output_md.append(f"- **Domain Type:** {no_hall_domain}\n")

                    output_md.append("\n---\n")

                    # Mark types as covered
                    covered_basic_types.add(basic_type)
                    covered_domain_types.add(domain_type)
                    examples_found += 1

                    break

    print(f"  Found {examples_found} examples")
    print(f"  Covered basic types: {len(covered_basic_types)}")
    print(f"  Covered domain types: {len(covered_domain_types)}")

# Write to file
output_path = "/root/akhil/detailed_probe_analysis/mixed_hallucination_examples.md"
with open(output_path, 'w', encoding='utf-8') as f:
    f.write(''.join(output_md))

print(f"\n{'='*80}")
print(f"Examples saved to: {output_path}")
print('='*80)
