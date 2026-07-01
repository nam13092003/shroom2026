#!/usr/bin/env python3
"""
Find specific patterns where actual hallucinations exist (true_label=1):
Example 1: Vision-only fails ❌ AND Vision-token fails ❌ BUT Query-token succeeds ✅
Example 2: Vision-only fails ❌ BUT Vision-token succeeds ✅ AND Query-token succeeds ✅

2 examples per basic_hallucination_type
"""
import pandas as pd

# Load the full comparison data
df = pd.read_csv('/root/akhil/detailed_probe_analysis/gemma_probe_comparison_full.csv')

print("="*80)
print("GEMMA HALLUCINATION DETECTION PATTERNS")
print("="*80)
print(f"\nTotal samples: {len(df)}")
print(f"Actual hallucinations: {len(df[df['true_label'] == 1])}")

# Filter for actual hallucinations only
hall_df = df[df['true_label'] == 1].copy()

print(f"\nFiltered to hallucinations: {len(hall_df)}")

# Pattern 1: Vision-only WRONG (pred=0) AND Vision-token WRONG (pred=0) BUT Query-token CORRECT (pred=1)
pattern1 = hall_df[
    (hall_df['vision_only_pred'] == 0) &
    (hall_df['vision_token_pred'] == 0) &
    (hall_df['query_token_pred'] == 1)
]

print(f"\nPattern 1 (VO❌ VT❌ QT✅): {len(pattern1)} examples")

# Pattern 2: Vision-only WRONG (pred=0) BUT Vision-token CORRECT (pred=1) AND Query-token CORRECT (pred=1)
pattern2 = hall_df[
    (hall_df['vision_only_pred'] == 0) &
    (hall_df['vision_token_pred'] == 1) &
    (hall_df['query_token_pred'] == 1)
]

print(f"Pattern 2 (VO❌ VT✅ QT✅): {len(pattern2)} examples")

# Create output
output = []
output.append("# Gemma Hallucination Detection Patterns\n")
output.append("Analyzing cases where actual hallucinations exist (true_label=1)\n\n")
output.append("---\n\n")

basic_types = ['Object-Related', 'Relationship', 'Attribute-Related', 'Other']

for basic_type in basic_types:
    output.append(f"\n## Basic Hallucination Type: {basic_type}\n\n")

    # Pattern 1: Both vision probes fail, only query succeeds
    p1_type = pattern1[pattern1['basic_hallucination_type'] == basic_type].head(2)

    if len(p1_type) > 0:
        output.append(f"### Pattern 1: Vision-only ❌ AND Vision-token ❌ → Query-token ✅\n")
        output.append("_Both vision probes failed to detect hallucination, only query-token succeeded_\n\n")

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
        output.append(f"### Pattern 1: Vision-only ❌ AND Vision-token ❌ → Query-token ✅\n")
        output.append("_No examples found for this pattern_\n\n")

    # Pattern 2: Vision-only fails, but both vision-token and query succeed
    p2_type = pattern2[pattern2['basic_hallucination_type'] == basic_type].head(2)

    if len(p2_type) > 0:
        output.append(f"### Pattern 2: Vision-only ❌ → Vision-token ✅ AND Query-token ✅\n")
        output.append("_Vision-only failed, but both vision-token and query-token detected the hallucination_\n\n")

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
        output.append(f"### Pattern 2: Vision-only ❌ → Vision-token ✅ AND Query-token ✅\n")
        output.append("_No examples found for this pattern_\n\n")

# Summary statistics
output.append("\n## Summary Statistics\n\n")
output.append(f"- Total actual hallucinations: {len(hall_df)}\n")
output.append(f"- Pattern 1 (VO❌ VT❌ QT✅): {len(pattern1)} examples\n")
output.append(f"- Pattern 2 (VO❌ VT✅ QT✅): {len(pattern2)} examples\n\n")

# Breakdown by type
output.append("### Pattern 1 Breakdown by Hallucination Type:\n")
for basic_type in basic_types:
    count = len(pattern1[pattern1['basic_hallucination_type'] == basic_type])
    output.append(f"- {basic_type}: {count} examples\n")

output.append("\n### Pattern 2 Breakdown by Hallucination Type:\n")
for basic_type in basic_types:
    count = len(pattern2[pattern2['basic_hallucination_type'] == basic_type])
    output.append(f"- {basic_type}: {count} examples\n")

# Write to file
output_path = "/root/akhil/detailed_probe_analysis/gemma_hallucination_detection_patterns.md"
with open(output_path, 'w', encoding='utf-8') as f:
    f.write(''.join(output))

print(f"\n{'='*80}")
print(f"Report saved to: {output_path}")
print('='*80)

# Also save filtered datasets
pattern1.to_csv('/root/akhil/detailed_probe_analysis/gemma_pattern1_vo_vt_fail_qt_success.csv', index=False)
pattern2.to_csv('/root/akhil/detailed_probe_analysis/gemma_pattern2_vo_fail_vt_qt_success.csv', index=False)

print(f"\nPattern 1 CSV: /root/akhil/detailed_probe_analysis/gemma_pattern1_vo_vt_fail_qt_success.csv")
print(f"Pattern 2 CSV: /root/akhil/detailed_probe_analysis/gemma_pattern2_vo_fail_vt_qt_success.csv")
