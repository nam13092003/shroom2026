#!/usr/bin/env python3
"""
Get exactly 3 examples for each pattern and basic hallucination type
"""
import pandas as pd

# Load the full comparison data
df = pd.read_csv('/root/akhil/detailed_probe_analysis/gemma_probe_comparison_full.csv')

# Filter for actual hallucinations only
hall_df = df[df['true_label'] == 1].copy()

# Pattern 1: Vision-only WRONG (pred=0) AND Vision-token WRONG (pred=0) BUT Query-token CORRECT (pred=1)
pattern1 = hall_df[
    (hall_df['vision_only_pred'] == 0) &
    (hall_df['vision_token_pred'] == 0) &
    (hall_df['query_token_pred'] == 1)
]

# Pattern 2: Vision-only WRONG (pred=0) BUT Vision-token CORRECT (pred=1) AND Query-token CORRECT (pred=1)
pattern2 = hall_df[
    (hall_df['vision_only_pred'] == 0) &
    (hall_df['vision_token_pred'] == 1) &
    (hall_df['query_token_pred'] == 1)
]

# Create output
output = []
output.append("# Gemma Hallucination Detection - 3 Examples Per Type\n\n")
output.append("---\n\n")

basic_types = ['Object-Related', 'Relationship', 'Attribute-Related', 'Other']

for basic_type in basic_types:
    output.append(f"\n## Basic Hallucination Type: {basic_type}\n\n")

    # Pattern 1: 3 examples
    p1_type = pattern1[pattern1['basic_hallucination_type'] == basic_type].head(3)

    output.append(f"### Pattern 1: Vision-only ❌ AND Vision-token ❌ → Query-token ✅\n")
    output.append("_Both vision probes failed to detect hallucination, only query-token succeeded_\n\n")

    if len(p1_type) > 0:
        for idx, (i, row) in enumerate(p1_type.iterrows(), 1):
            output.append(f"**Example {idx}**\n\n")
            output.append(f"- **Question ID:** `{row['question_id']}`\n")
            output.append(f"- **Image:** `{row['image_id']}`\n")
            output.append(f"- **Question:** {row['question']}\n")
            output.append(f"- **Ground Truth:** {row['ground_truth']}\n")
            output.append(f"- **Model Answer:** {row['model_answer']}\n")
            output.append(f"- **True Label:** Hallucination ✓\n")
            output.append(f"- **Domain Type:** {row['domain_type']}\n\n")
            output.append("**Probe Predictions:**\n")
            output.append(f"- Vision-only: No Hallucination (prob: {row['vision_only_prob']:.3f}) ❌ MISSED\n")
            output.append(f"- Vision-token (L47): No Hallucination (prob: {row['vision_token_prob']:.3f}) ❌ MISSED\n")
            output.append(f"- Query-token (L47): Hallucination (prob: {row['query_token_prob']:.3f}) ✅ DETECTED\n\n")
            output.append("---\n\n")
    else:
        output.append("_No examples found for this pattern_\n\n")

    # Pattern 2: 3 examples
    p2_type = pattern2[pattern2['basic_hallucination_type'] == basic_type].head(3)

    output.append(f"### Pattern 2: Vision-only ❌ → Vision-token ✅ AND Query-token ✅\n")
    output.append("_Vision-only failed, but both vision-token and query-token detected the hallucination_\n\n")

    if len(p2_type) > 0:
        for idx, (i, row) in enumerate(p2_type.iterrows(), 1):
            output.append(f"**Example {idx}**\n\n")
            output.append(f"- **Question ID:** `{row['question_id']}`\n")
            output.append(f"- **Image:** `{row['image_id']}`\n")
            output.append(f"- **Question:** {row['question']}\n")
            output.append(f"- **Ground Truth:** {row['ground_truth']}\n")
            output.append(f"- **Model Answer:** {row['model_answer']}\n")
            output.append(f"- **True Label:** Hallucination ✓\n")
            output.append(f"- **Domain Type:** {row['domain_type']}\n\n")
            output.append("**Probe Predictions:**\n")
            output.append(f"- Vision-only: No Hallucination (prob: {row['vision_only_prob']:.3f}) ❌ MISSED\n")
            output.append(f"- Vision-token (L47): Hallucination (prob: {row['vision_token_prob']:.3f}) ✅ DETECTED\n")
            output.append(f"- Query-token (L47): Hallucination (prob: {row['query_token_prob']:.3f}) ✅ DETECTED\n\n")
            output.append("---\n\n")
    else:
        output.append("_No examples found for this pattern_\n\n")

# Write to file
output_path = "/root/akhil/detailed_probe_analysis/gemma_3_examples_per_type.md"
with open(output_path, 'w', encoding='utf-8') as f:
    f.write(''.join(output))

print(f"Report saved to: {output_path}")
