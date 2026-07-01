# SmolVLM Probe Training - Quick Start Guide

## ✅ All Scripts Created Successfully!

**Location:** `/root/akhil/probe_training_scripts/smolvlm_model_probe/`

## 📊 What Was Built

### 11 Probe Training Scripts:
1. **Vision Only** (1 probe)
   - `01_vision_only_probe.py`

2. **Vision Token Probes** (5 probes)
   - `02_vision_token_layer0_probe.py` (first layer)
   - `03_vision_token_layer6_probe.py` (n/4)
   - `04_vision_token_layer12_probe.py` (n/2, middle)
   - `05_vision_token_layer18_probe.py` (3n/4)
   - `06_vision_token_layer23_probe.py` (final layer)

3. **Query Token Probes** (5 probes)
   - `07_query_token_layer0_probe.py` (first layer)
   - `08_query_token_layer6_probe.py` (n/4)
   - `09_query_token_layer12_probe.py` (n/2, middle)
   - `10_query_token_layer18_probe.py` (3n/4)
   - `11_query_token_layer23_probe.py` (final layer)

### Execution & Verification Scripts:
- `verify_setup.py` - Pre-flight checks
- `run_all_probes.py` - Run all probes sequentially (Python)
- `run_all_probes.sh` - Run all probes sequentially (Bash)

## 🚀 How to Execute

### Step 1: Verify Setup (IMPORTANT!)
```bash
cd /root/akhil/probe_training_scripts/smolvlm_model_probe
python3 verify_setup.py
```

Expected output:
```
✅ All checks passed! Ready to run probe training.
```

### Step 2: Run All Probes
```bash
python3 run_all_probes.py
```

This will:
- Train all 11 probes sequentially
- Save results to `results/<probe_name>/`
- Show progress and timing for each probe
- Generate final summary

### Alternative: Run Individual Probes
```bash
# Example: Run only vision_only probe
python3 01_vision_only_probe.py

# Example: Run only query_token layer 23
python3 11_query_token_layer23_probe.py
```

## 📈 What to Expect

**Total Runtime:** ~1-2 hours for all 11 probes
**Per Probe:** ~5-10 minutes (50 epochs each)

**Output per probe:**
- `results/<probe_name>/`
  - `probe_model.pt` - Trained model checkpoint
  - `results.json` - Test AUROC, F1, accuracy, etc.
  - `confusion_matrix.png` - Visualization
  - `roc_curve.png` - ROC curves
  - `training_history.png` - Loss/accuracy curves
  - `training_*.log` - Detailed logs

## 📊 Data Configuration

**H5 Files:** 10,000 samples
- Location: `/root/akhil/HALP_EACL_Models/Models/Smol_VL/smolvlm_output/`
- Files: `smolvlm_2.2b_embeddings_part_001.h5` to `part_010.h5`

**CSV Labels:** 10,000 samples
- Location: `/root/akhil/FInal_CSV_Hallucination/smolvlm_manually_reviewed.csv`
- No Hallucination: 9,009 (90.1%)
- Hallucination: 991 (9.9%)

## 🎯 Model Details

**Model:** SmolVLM2-2.2B-Instruct
**Text Layers:** 24 (0-23)
**Selected Layers:** [0, 6, 12, 18, 23]

**Embedding Dimensions:**
- Vision only: 1152
- Vision token: 2048
- Query token: 2048

**Probe Architecture:**
- Input → [512, 256, 128] → 1 (binary)
- Dropout: 0.3, LR: 0.001, Batch: 32, Epochs: 50

## 📝 Monitoring Progress

While running, each probe will display:
```
[X/11] Running: XX_probe_name.py
Epoch 10/50: Train Loss: 0.XXXX, Train Acc: 0.XXXX
...
TRAIN METRICS:
  Accuracy:  0.XXXX
  AUROC:     0.XXXX
TEST METRICS:
  Accuracy:  0.XXXX
  AUROC:     0.XXXX
✓ SUCCESS: XX_probe_name.py (Xm XXs)
```

## ⚡ Quick Commands

```bash
# Navigate to directory
cd /root/akhil/probe_training_scripts/smolvlm_model_probe

# Verify everything is ready
python3 verify_setup.py

# Run all probes
python3 run_all_probes.py

# Check results after completion
ls -R results/
```

## 🎉 Ready to Execute!

All scripts are generated and verified. You can start training whenever ready.
