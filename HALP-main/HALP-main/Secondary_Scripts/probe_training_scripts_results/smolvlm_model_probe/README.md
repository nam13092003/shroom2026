# SmolVLM2-2.2B Hallucination Detection Probe Training

This directory contains all scripts for training hallucination detection probes on SmolVLM2-2.2B embeddings.

## 📁 Directory Structure

```
smolvlm_model_probe/
├── README.md                           # This file
├── verify_setup.py                     # Pre-flight verification script
├── run_all_probes.py                   # Master execution script (Python)
├── run_all_probes.sh                   # Master execution script (Bash)
├── generate_all_probe_scripts.py       # Script generator (already executed)
│
├── 01_vision_only_probe.py             # Vision encoder probe
│
├── 02_vision_token_layer0_probe.py     # Vision token layer 0
├── 03_vision_token_layer6_probe.py     # Vision token layer 6 (n/4)
├── 04_vision_token_layer12_probe.py    # Vision token layer 12 (n/2)
├── 05_vision_token_layer18_probe.py    # Vision token layer 18 (3n/4)
├── 06_vision_token_layer23_probe.py    # Vision token layer 23 (final)
│
├── 07_query_token_layer0_probe.py      # Query token layer 0
├── 08_query_token_layer6_probe.py      # Query token layer 6 (n/4)
├── 09_query_token_layer12_probe.py     # Query token layer 12 (n/2)
├── 10_query_token_layer18_probe.py     # Query token layer 18 (3n/4)
└── 11_query_token_layer23_probe.py     # Query token layer 23 (final)
```

## 🎯 Probe Configuration

**Model:** SmolVLM2-2.2B-Instruct
**Total Layers:** 24 text decoder layers
**Selected Layers:** [0, 6, 12, 18, 23]

### Embeddings

- **Vision Only:** (1152,) - Vision encoder output
- **Vision Token:** (2048,) - Vision token at last image position
- **Query Token:** (2048,) - Query token at last question position

### Training Configuration

- **Architecture:** [512, 256, 128] → 1 (Binary classifier)
- **Dropout:** 0.3
- **Learning Rate:** 0.001
- **Batch Size:** 32
- **Epochs:** 50
- **Train/Test Split:** 80/20
- **Device:** CUDA (RTX 4090)

## 📊 Data Sources

- **H5 Files:** `/root/akhil/HALP_EACL_Models/Models/Smol_VL/smolvlm_output/`
  - 10 files: `smolvlm_2.2b_embeddings_part_001.h5` to `part_010.h5`
  - Total: 10,000 samples

- **Labels:** `/root/akhil/FInal_CSV_Hallucination/smolvlm_manually_reviewed.csv`
  - Total: 10,000 samples
  - No Hallucination: 9,009 (90.1%)
  - Hallucination: 991 (9.9%)

## 🚀 How to Run

### Option 1: Run All Probes Sequentially (Recommended)

```bash
# Verify setup first
python3 verify_setup.py

# Run all 11 probes
python3 run_all_probes.py
```

### Option 2: Run Individual Probes

```bash
# Run specific probe
python3 01_vision_only_probe.py
python3 02_vision_token_layer0_probe.py
# ... etc
```

### Option 3: Run with Bash Script

```bash
./run_all_probes.sh
```

## 📈 Expected Outputs

Each probe creates a results directory:

```
results/
├── vision_only/
│   ├── probe_model.pt              # Trained model
│   ├── results.json                # Metrics (AUROC, F1, etc.)
│   ├── confusion_matrix.png        # Confusion matrices
│   ├── roc_curve.png              # ROC curves
│   ├── training_history.png       # Training curves
│   └── training_YYYYMMDD_HHMMSS.log
│
├── vision_token_layer0/
├── vision_token_layer6/
├── vision_token_layer12/
├── vision_token_layer18/
├── vision_token_layer23/
│
├── query_token_layer0/
├── query_token_layer6/
├── query_token_layer12/
├── query_token_layer18/
└── query_token_layer23/
```

## 📋 Key Metrics

Each `results.json` contains:

```json
{
  "model_name": "SmolVLM2-2.2B",
  "embedding_type": "vision_token_representation",
  "layer_name": "layer_23",
  "input_dim": 2048,

  "test_set": {
    "accuracy": 0.xxxx,
    "precision": 0.xxxx,
    "recall": 0.xxxx,
    "f1": 0.xxxx,
    "auroc": 0.xxxx
  }
}
```

## ⏱️ Estimated Runtime

- **Per Probe:** ~5-10 minutes (50 epochs)
- **All 11 Probes:** ~1-2 hours total

## ✅ Verification

Before running, verify setup:

```bash
python3 verify_setup.py
```

This checks:
- ✓ CSV file exists with correct columns
- ✓ H5 files exist with correct structure
- ✓ All dependencies installed
- ✓ CUDA available

## 🔧 Troubleshooting

**Issue:** CUDA out of memory
**Solution:** Reduce `BATCH_SIZE` in probe scripts (default: 32)

**Issue:** H5 files not found
**Solution:** Verify extraction completed: `ls /root/akhil/HALP_EACL_Models/Models/Smol_VL/smolvlm_output/`

**Issue:** Missing CSV columns
**Solution:** Check CSV has: `question_id`, `image_id`, `question`, `is_hallucinating_manual`

## 📝 Notes

- All probes use the same random seed (42) for reproducibility
- Training uses stratified split to maintain class balance
- Results are saved after each probe completes
- Can interrupt and resume individual probes

## 🎓 Model Architecture Details

**SmolVLM2-2.2B:**
- Vision Encoder: 27 layers (1152-dim)
- Text Decoder: 24 layers (2048-dim)
- Layer Selection Strategy: [0, n/4, n/2, 3n/4, n-1]
- Extraction Points:
  - Vision token: After last image token
  - Query token: After last question token

## 📊 Expected Results

Based on other VLM models, expected test AUROC ranges:
- Vision Only: 0.50 - 0.70
- Early Layers (0, 6): 0.60 - 0.80
- Middle Layers (12): 0.70 - 0.85
- Late Layers (18, 23): 0.80 - 0.95

Query tokens typically perform better than vision tokens in later layers.
