# Probe Performance Analysis by Category

This folder contains scripts to analyze trained probe performance broken down by question categories and source datasets.

## Overview

The analysis script:
1. ✅ Recreates the **exact same train/test split** used during probe training (using `random_state=42`)
2. ✅ Loads the **saved model checkpoint** from probe training results
3. ✅ Gets predictions on the test set
4. ✅ Merges with category metadata from `sampled_10k_relational_dataset.csv`
5. ✅ Calculates **per-category AUROC**, **per-source AUROC**, and **overall AUROC**

## Key Features

- **Path Verification**: Automatically verifies all required paths exist before analysis
- **Consistent Splits**: Uses same random state (42) and test size (0.2) as training
- **Model Architecture Matching**: Reconstructs exact same model architecture to load weights
- **Comprehensive Reports**: Generates CSV files and human-readable markdown reports

## Current Implementation Status

✅ **SmolVLM Query Token Layer 18** - Fully implemented and tested
- Overall Test AUROC: **0.9272** (matches training results ✓)
- Category analysis: 37 unique categories
- Source analysis: 6 source datasets (AMBER, POPE, MME, HallusionBench, HaloQuest, MathVista)

## Files

```
probe_analysis/
├── README.md                          # This file
├── analyze_probe_by_category.py       # Main analysis script (SmolVLM Layer 18)
└── results/
    └── smolvlm_query_token_layer18/
        ├── category_auroc.csv         # Per-category AUROC scores
        ├── source_auroc.csv           # Per-source dataset AUROC scores
        ├── analysis_report.md         # Human-readable markdown report
        ├── analysis_summary.json      # JSON summary
        └── analysis_*.log             # Detailed execution logs
```

## Usage

### Analyzing SmolVLM Query Token Layer 18

```bash
cd /root/akhil/probe_analysis
python3 analyze_probe_by_category.py
```

### Configuration for Different Models/Layers

To analyze a different probe, modify the `CONFIG` section in `analyze_probe_by_category.py`:

```python
CONFIG = {
    # Model configuration (must match training)
    "MODEL_NAME": "SmolVLM2-2.2B",
    "EMBEDDING_TYPE": "query_token_representation",  # or "vision_token_representation" or "vision_only_representation"
    "LAYER_NAME": "layer_18",  # or "layer_0", "layer_6", "layer_12", "layer_23", or None for vision_only

    # Data paths
    "H5_DIR": "/root/akhil/HALP_EACL_Models/Models/Smol_VL/smolvlm_output",
    "CSV_PATH": "/root/akhil/FInal_CSV_Hallucination/smolvlm_manually_reviewed.csv",
    "CATEGORY_CSV_PATH": "/root/akhil/final_data/sampled_10k_relational_dataset.csv",

    # Model checkpoint path (IMPORTANT: Must point to correct saved model)
    "MODEL_CHECKPOINT": "/root/akhil/probe_training_scripts/smolvlm_model_probe/results/query_token_layer18/probe_model.pt",

    # Output directory
    "OUTPUT_DIR": "/root/akhil/probe_analysis/results/smolvlm_query_token_layer18",

    # ... other parameters ...
}
```

### Example: Analyzing Vision Token Layer 6

```python
CONFIG = {
    "MODEL_NAME": "SmolVLM2-2.2B",
    "EMBEDDING_TYPE": "vision_token_representation",
    "LAYER_NAME": "layer_6",

    # ... same H5_DIR and CSV paths ...

    "MODEL_CHECKPOINT": "/root/akhil/probe_training_scripts/smolvlm_model_probe/results/vision_token_layer6/probe_model.pt",
    "OUTPUT_DIR": "/root/akhil/probe_analysis/results/smolvlm_vision_token_layer6",

    # ... same other parameters ...
}
```

### Example: Analyzing Different Model (Gemma3)

```python
CONFIG = {
    "MODEL_NAME": "Gemma3-12B",
    "EMBEDDING_TYPE": "query_token_representation",
    "LAYER_NAME": "layer_31",  # 3n/4 for Gemma3's 42 layers

    "H5_DIR": "/root/akhil/HALP_EACL_Models/Models/Gemma3/gemma3_output",
    "CSV_PATH": "/root/akhil/FInal_CSV_Hallucination/gemma3_manually_reviewed.csv",
    "CATEGORY_CSV_PATH": "/root/akhil/final_data/sampled_10k_relational_dataset.csv",

    "MODEL_CHECKPOINT": "/root/akhil/probe_training_scripts/gemma3_model_probe/results/query_token_layer31/probe_model.pt",
    "OUTPUT_DIR": "/root/akhil/probe_analysis/results/gemma3_query_token_layer31",

    # ... same other parameters ...
}
```

## Output Files

### 1. `category_auroc.csv`
Per-category AUROC scores with sample counts and class distribution.

**Columns:**
- `category`: Question category name
- `auroc`: AUROC score (or None if single class)
- `num_samples`: Total test samples in this category
- `num_hallucination`: Number of hallucination samples
- `num_no_hallucination`: Number of no-hallucination samples
- `note`: Notes (e.g., "Single class only")

### 2. `source_auroc.csv`
Per-source dataset AUROC scores.

**Columns:**
- `source_dataset`: Source dataset name (amber, pope, mme, etc.)
- `auroc`: AUROC score (or None if single class)
- `num_samples`: Total test samples from this source
- `num_hallucination`: Number of hallucination samples
- `num_no_hallucination`: Number of no-hallucination samples
- `note`: Notes

### 3. `analysis_report.md`
Human-readable markdown report with:
- Overall test AUROC
- Performance by source dataset (table)
- Top 20 categories by AUROC
- Bottom 20 categories by AUROC
- Categories with single class (no AUROC calculable)

### 4. `analysis_summary.json`
JSON summary with metadata about the analysis run.

## Key Results: SmolVLM Query Token Layer 18

### Overall Performance
- **Test AUROC: 0.9272** ✓ (matches training results)

### Top Performing Categories
| Category | AUROC | Samples |
|----------|-------|---------|
| figure | 1.0000 | 5 |
| ocr | 1.0000 | 6 |
| discriminative-hallucination | 0.9793 | 126 |
| relation | 0.9783 | 131 |
| posters | 0.9565 | 24 |

### Bottom Performing Categories
| Category | AUROC | Samples |
|----------|-------|---------|
| landmark | 0.2000 | 11 |
| map | 0.3000 | 7 |
| video | 0.3571 | 30 |
| text_translation | 0.5625 | 8 |
| chart | 0.5833 | 17 |

### Performance by Source Dataset
| Source | AUROC | Samples |
|--------|-------|---------|
| amber | 0.9088 | 786 |
| pope | 0.8841 | 242 |
| mme | 0.8430 | 176 |
| hallusionbench | 0.6454 | 123 |
| haloquest | N/A (single class) | 569 |
| mathvista | N/A (single class) | 104 |

## Important Notes

### ⚠️ Critical: Model Checkpoint Path Mapping

When analyzing different models or layers, you **MUST** ensure the model checkpoint path matches the configuration:

**SmolVLM Checkpoint Paths:**
```
vision_only → /root/akhil/probe_training_scripts/smolvlm_model_probe/results/vision_only/probe_model.pt

vision_token_layer0 → /root/akhil/probe_training_scripts/smolvlm_model_probe/results/vision_token_layer0/probe_model.pt
vision_token_layer6 → /root/akhil/probe_training_scripts/smolvlm_model_probe/results/vision_token_layer6/probe_model.pt
vision_token_layer12 → /root/akhil/probe_training_scripts/smolvlm_model_probe/results/vision_token_layer12/probe_model.pt
vision_token_layer18 → /root/akhil/probe_training_scripts/smolvlm_model_probe/results/vision_token_layer18/probe_model.pt
vision_token_layer23 → /root/akhil/probe_training_scripts/smolvlm_model_probe/results/vision_token_layer23/probe_model.pt

query_token_layer0 → /root/akhil/probe_training_scripts/smolvlm_model_probe/results/query_token_layer0/probe_model.pt
query_token_layer6 → /root/akhil/probe_training_scripts/smolvlm_model_probe/results/query_token_layer6/probe_model.pt
query_token_layer12 → /root/akhil/probe_training_scripts/smolvlm_model_probe/results/query_token_layer12/probe_model.pt
query_token_layer18 → /root/akhil/probe_training_scripts/smolvlm_model_probe/results/query_token_layer18/probe_model.pt
query_token_layer23 → /root/akhil/probe_training_scripts/smolvlm_model_probe/results/query_token_layer23/probe_model.pt
```

**Other Models:**
- Gemma3: `/root/akhil/probe_training_scripts/gemma3_model_probe/results/{probe_type}/probe_model.pt`
- FastVLM: `/root/akhil/probe_training_scripts/fastvlm_model_probe/results/{probe_type}/probe_model.pt`
- LLaVA-Next: `/root/akhil/probe_training_scripts/llava_next_model_probe/results/{probe_type}/probe_model.pt`
- Molmo-V1: `/root/akhil/probe_training_scripts/molmo_model_probe/results/{probe_type}/probe_model.pt`
- Qwen2.5-VL: `/root/akhil/probe_training_scripts/qwen_model_probe/results/{probe_type}/probe_model.pt`
- Llama-3.2: `/root/akhil/probe_training_scripts/llama_model_probe/results/{probe_type}/probe_model.pt`
- Phi4-VL: `/root/akhil/probe_training_scripts/phi4_model_probe/results/{probe_type}/probe_model.pt`

### ⚠️ Data Path Mapping

Each model has different H5 and CSV paths:

| Model | H5_DIR | CSV_PATH |
|-------|--------|----------|
| SmolVLM | `/root/akhil/HALP_EACL_Models/Models/Smol_VL/smolvlm_output` | `/root/akhil/FInal_CSV_Hallucination/smolvlm_manually_reviewed.csv` |
| Gemma3 | `/root/akhil/HALP_EACL_Models/Models/Gemma3/gemma3_output` | `/root/akhil/FInal_CSV_Hallucination/gemma3_manually_reviewed.csv` |
| FastVLM | `/root/akhil/HALP_EACL_Models/Models/FastVLM/fastvlm_output` | `/root/akhil/FInal_CSV_Hallucination/fastvlm_manually_reviewed.csv` |
| LLaVA-Next | `/root/akhil/HALP_EACL_Models/Models/LLaVA_Next/llava_next_output` | `/root/akhil/FInal_CSV_Hallucination/llava_next_manually_reviewed.csv` |
| Molmo-V1 | `/root/akhil/HALP_EACL_Models/Models/Molmo/molmo_output` | `/root/akhil/FInal_CSV_Hallucination/molmo_manually_reviewed.csv` |
| Qwen2.5-VL | `/root/akhil/HALP_EACL_Models/Models/Qwen/qwen_output` | `/root/akhil/FInal_CSV_Hallucination/qwen_manually_reviewed.csv` |
| Llama-3.2 | `/root/akhil/HALP_EACL_Models/Models/Llama/llama_output` | `/root/akhil/FInal_CSV_Hallucination/llama_manually_reviewed.csv` |
| Phi4-VL | `/root/akhil/HALP_EACL_Models/Models/Phi4/phi4_output` | `/root/akhil/FInal_CSV_Hallucination/phi4_manually_reviewed.csv` |

### Training Parameters (Same for All Models)

All models use the same training configuration:
- `TEST_SIZE`: 0.2 (80/20 train/test split)
- `RANDOM_STATE`: 42 (for reproducibility)
- `LAYER_SIZES`: [512, 256, 128]
- `DROPOUT_RATE`: 0.3

**These must match exactly to ensure correct split and model loading!**

## Troubleshooting

### Issue: AUROC doesn't match training results
**Solution**: Verify you're using the correct `RANDOM_STATE` (42) and `TEST_SIZE` (0.2)

### Issue: Model loading error
**Solution**: Check that `MODEL_CHECKPOINT` path points to the correct `.pt` file and that `EMBEDDING_TYPE` and `LAYER_NAME` match the checkpoint

### Issue: No embeddings found
**Solution**: Verify `H5_DIR` contains the correct H5 files and `EMBEDDING_TYPE`/`LAYER_NAME` match the H5 structure

### Issue: Categories not found
**Solution**: Ensure `CATEGORY_CSV_PATH` points to `/root/akhil/final_data/sampled_10k_relational_dataset.csv`

## Next Steps

To analyze all models and all layers systematically:
1. Create separate analysis scripts for each model (or use a template generator)
2. Run analysis for all 11 probes per model (8 models × 11 probes = 88 analyses)
3. Compile aggregate results across all models
4. Compare category performance across different models
