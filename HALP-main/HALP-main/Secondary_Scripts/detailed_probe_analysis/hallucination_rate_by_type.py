#!/usr/bin/env python3
"""
Calculate hallucination rate for each model per basic_hallucination_type
"""
import pandas as pd

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

# Load metadata for hallucination types
metadata_df = pd.read_csv('/root/akhil/final_data/sampled_10k_with_hallucination_types.csv')
metadata_lookup = {}
for _, row in metadata_df.iterrows():
    metadata_lookup[row['question_id']] = {
        'basic_hallucination_type': row.get('basic_hallucination_type', 'Unknown'),
    }

print("="*80)
print("HALLUCINATION RATE BY BASIC HALLUCINATION TYPE")
print("="*80)

all_results = []

for model_name, csv_path in MODEL_CSVS.items():
    print(f"\nProcessing {model_name}...")

    # Load model CSV
    model_df = pd.read_csv(csv_path, low_memory=False)

    # Convert hallucination label
    model_df['is_hallucinating'] = model_df['is_hallucinating_manual'].apply(
        lambda x: True if (isinstance(x, str) and x.lower() in ['true', '1', 'yes']) or x == True or x == 1 else False
    )

    # Add metadata
    model_df['basic_hallucination_type'] = model_df['question_id'].map(
        lambda qid: metadata_lookup.get(qid, {}).get('basic_hallucination_type', 'Unknown')
    )

    # Calculate hallucination rate per type
    type_stats = model_df.groupby('basic_hallucination_type').agg({
        'is_hallucinating': ['sum', 'count']
    }).reset_index()

    type_stats.columns = ['basic_hallucination_type', 'hallucination_count', 'total_count']
    type_stats['hallucination_rate'] = (type_stats['hallucination_count'] / type_stats['total_count'] * 100).round(2)
    type_stats['model'] = model_name

    all_results.append(type_stats)

    # Print for this model
    print(f"\n{model_name}:")
    for _, row in type_stats.iterrows():
        print(f"  {row['basic_hallucination_type']}: {row['hallucination_rate']:.2f}% ({row['hallucination_count']}/{row['total_count']})")

# Combine all results
combined_df = pd.concat(all_results, ignore_index=True)

# Pivot table for easy comparison
pivot_df = combined_df.pivot(
    index='basic_hallucination_type',
    columns='model',
    values='hallucination_rate'
).fillna(0)

print("\n" + "="*80)
print("SUMMARY TABLE (Hallucination Rate %)")
print("="*80)
print(pivot_df.to_string())

# Save to CSV
output_csv = "/root/akhil/detailed_probe_analysis/hallucination_rate_by_type.csv"
combined_df.to_csv(output_csv, index=False)

# Save pivot table
pivot_output = "/root/akhil/detailed_probe_analysis/hallucination_rate_by_type_pivot.csv"
pivot_df.to_csv(pivot_output)

print(f"\n{'='*80}")
print(f"Detailed results: {output_csv}")
print(f"Pivot table: {pivot_output}")
print('='*80)

# Calculate overall hallucination rate per model
print("\n" + "="*80)
print("OVERALL HALLUCINATION RATE PER MODEL")
print("="*80)

overall_stats = combined_df.groupby('model').agg({
    'hallucination_count': 'sum',
    'total_count': 'sum'
}).reset_index()
overall_stats['overall_hallucination_rate'] = (overall_stats['hallucination_count'] / overall_stats['total_count'] * 100).round(2)

for _, row in overall_stats.iterrows():
    print(f"{row['model']}: {row['overall_hallucination_rate']:.2f}% ({row['hallucination_count']}/{row['total_count']})")
