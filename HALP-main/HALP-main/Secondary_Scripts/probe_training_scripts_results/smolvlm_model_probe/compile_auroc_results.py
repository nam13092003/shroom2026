#!/usr/bin/env python3
"""
Compile Test AUROC results from all SmolVLM probe trainings.
"""

import json
from pathlib import Path

# Define all probe result directories
PROBE_DIRS = [
    ("Vision Only", "vision_only"),
    ("Vision Token - Layer 0", "vision_token_layer0"),
    ("Vision Token - Layer 6", "vision_token_layer6"),
    ("Vision Token - Layer 12", "vision_token_layer12"),
    ("Vision Token - Layer 18", "vision_token_layer18"),
    ("Vision Token - Layer 23", "vision_token_layer23"),
    ("Query Token - Layer 0", "query_token_layer0"),
    ("Query Token - Layer 6", "query_token_layer6"),
    ("Query Token - Layer 12", "query_token_layer12"),
    ("Query Token - Layer 18", "query_token_layer18"),
    ("Query Token - Layer 23", "query_token_layer23"),
]

BASE_DIR = Path("/root/akhil/probe_training_scripts/smolvlm_model_probe/results")

print("=" * 80)
print("SmolVLM2-2.2B Probe Training - Test AUROC Results")
print("=" * 80)
print()

results = []

for probe_name, probe_dir in PROBE_DIRS:
    results_file = BASE_DIR / probe_dir / "results.json"

    try:
        with open(results_file, 'r') as f:
            data = json.load(f)
            test_auroc = data["test_set"]["auroc"]
            train_auroc = data["train_set"]["auroc"]

            results.append({
                "probe": probe_name,
                "test_auroc": test_auroc,
                "train_auroc": train_auroc
            })

            print(f"{probe_name:<35} Test AUROC: {test_auroc:.4f}  |  Train AUROC: {train_auroc:.4f}")

    except Exception as e:
        print(f"{probe_name:<35} ERROR: {e}")

print()
print("=" * 80)
print("Summary Statistics")
print("=" * 80)

if results:
    test_aurocs = [r["test_auroc"] for r in results]

    print(f"Best Test AUROC:  {max(test_aurocs):.4f} - {results[test_aurocs.index(max(test_aurocs))]['probe']}")
    print(f"Worst Test AUROC: {min(test_aurocs):.4f} - {results[test_aurocs.index(min(test_aurocs))]['probe']}")
    print(f"Mean Test AUROC:  {sum(test_aurocs) / len(test_aurocs):.4f}")
    print()

# Save to CSV
csv_output = BASE_DIR / "test_auroc_summary.csv"
with open(csv_output, 'w') as f:
    f.write("Probe Name,Test AUROC,Train AUROC\n")
    for result in results:
        f.write(f"{result['probe']},{result['test_auroc']:.4f},{result['train_auroc']:.4f}\n")

print(f"✓ Results saved to: {csv_output}")
