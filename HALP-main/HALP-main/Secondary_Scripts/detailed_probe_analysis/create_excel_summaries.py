#!/usr/bin/env python3
"""
Create one Excel file per model with AUROC scores across all probe types and representations
Each sheet contains: basic_hallucination_type, domain_type, answer_type results
"""
import os
import pandas as pd
import glob

results_base = "/root/akhil/detailed_probe_analysis/results"

# Get all model directories (skip llama and phi4 for now)
model_dirs = [d for d in os.listdir(results_base) if os.path.isdir(os.path.join(results_base, d)) and d in ['llama_3_2_11b']]

print("="*80)
print("CREATING EXCEL SUMMARIES PER MODEL")
print("="*80)

for model_dir in sorted(model_dirs):
    model_path = os.path.join(results_base, model_dir)

    # Create Excel writer
    excel_path = os.path.join(results_base, f"{model_dir}_summary.xlsx")

    print(f"\nProcessing: {model_dir}")

    # Get all probe directories
    probe_dirs = [d for d in os.listdir(model_path) if os.path.isdir(os.path.join(model_path, d))]

    if not probe_dirs:
        print(f"  No probes found, skipping...")
        continue

    # Collect data for each analysis type
    all_data = {
        'basic_hallucination_type': [],
        'domain_type': [],
        'answer_type': []
    }

    for probe_dir in sorted(probe_dirs):
        probe_path = os.path.join(model_path, probe_dir)

        # Read each CSV type
        for analysis_type in ['basic_hallucination_type', 'domain_type', 'answer_type']:
            csv_path = os.path.join(probe_path, f'{analysis_type}_auroc.csv')

            if os.path.exists(csv_path):
                df = pd.read_csv(csv_path)
                df['probe'] = probe_dir  # Add probe name as column
                all_data[analysis_type].append(df)

    # Create Excel file with multiple sheets
    with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:

        # Sheet 1: Basic Hallucination Type
        if all_data['basic_hallucination_type']:
            combined_df = pd.concat(all_data['basic_hallucination_type'], ignore_index=True)
            # Pivot to show probes as rows, types as columns
            pivot_df = combined_df.pivot_table(
                index='probe',
                columns='type',
                values='auroc',
                aggfunc='first'
            )
            pivot_df.to_excel(writer, sheet_name='Hallucination_Type')

            # Also add detailed view
            combined_df[['probe', 'type', 'auroc', 'num_samples', 'num_hallucination', 'num_no_hallucination', 'note']].to_excel(
                writer, sheet_name='Hallucination_Type_Detail', index=False
            )

        # Sheet 2: Domain Type
        if all_data['domain_type']:
            combined_df = pd.concat(all_data['domain_type'], ignore_index=True)
            pivot_df = combined_df.pivot_table(
                index='probe',
                columns='type',
                values='auroc',
                aggfunc='first'
            )
            pivot_df.to_excel(writer, sheet_name='Domain_Type')

            combined_df[['probe', 'type', 'auroc', 'num_samples', 'num_hallucination', 'num_no_hallucination', 'note']].to_excel(
                writer, sheet_name='Domain_Type_Detail', index=False
            )

        # Sheet 3: Answer Type
        if all_data['answer_type']:
            combined_df = pd.concat(all_data['answer_type'], ignore_index=True)
            pivot_df = combined_df.pivot_table(
                index='probe',
                columns='type',
                values='auroc',
                aggfunc='first'
            )
            pivot_df.to_excel(writer, sheet_name='Answer_Type')

            combined_df[['probe', 'type', 'auroc', 'num_samples', 'num_hallucination', 'num_no_hallucination', 'note']].to_excel(
                writer, sheet_name='Answer_Type_Detail', index=False
            )

        # Sheet 4: Overall Summary (overall AUROC per probe)
        summary_data = []
        for probe_dir in sorted(probe_dirs):
            summary_json = os.path.join(model_path, probe_dir, 'detailed_summary.json')
            if os.path.exists(summary_json):
                import json
                with open(summary_json) as f:
                    data = json.load(f)
                summary_data.append({
                    'probe': probe_dir,
                    'embedding_type': data.get('embedding_type', ''),
                    'layer_name': data.get('layer_name', ''),
                    'overall_auroc': data.get('overall_auroc', None),
                    'test_samples': data.get('test_samples', 0)
                })

        if summary_data:
            summary_df = pd.DataFrame(summary_data)
            summary_df.to_excel(writer, sheet_name='Overall_Summary', index=False)

    print(f"  ✓ Created: {excel_path}")
    print(f"    Sheets: Hallucination_Type, Domain_Type, Answer_Type, Overall_Summary")
    print(f"    Plus detail sheets for each type")

print("\n" + "="*80)
print("EXCEL CREATION COMPLETE")
print("="*80)
print(f"\nExcel files saved in: {results_base}/")
print("Files created:")
for model_dir in sorted(model_dirs):
    excel_path = os.path.join(results_base, f"{model_dir}_summary.xlsx")
    if os.path.exists(excel_path):
        print(f"  - {model_dir}_summary.xlsx")
