# SHROOM-Vision 2026: Multitask Probing Model for Hallucination Detection

This repository contains a complete, research-grade framework for **SHROOM-Vision 2026**, a model-agnostic hallucination detection task focusing on Large Vision-Language Models (LVLMs).

The architecture is built upon the pre-generation representation probing concept of **HALP** (EACL 2026 Oral). Rather than running binary classification on a single token hidden state, this codebase implements a post-generation multitask sequence labeling network that processes VLM features (hidden states, cross-attention weights, and vision representations) and predicts token-level BIO spans, category classification, and confidence calibration.

## Project Structure

```
project/
├── configs/
│   └── config.yaml           # Hydra configuration settings
├── datasets/
│   ├── alignment.py          # Character-to-token offset mapping & BIO tags alignment
│   └── shroom_dataset.py     # PyTorch Dataset, Collator, and HDF5 feature caching
├── models/
│   ├── grounding.py          # Grounding interface for OCR and object verification modules
│   ├── extractor.py          # Qwen2.5-VL hidden state, attention, and ViT feature extractor
│   ├── heads.py              # Prediction heads (Risk, BIO, Category, and Calibration)
│   └── multitask_model.py    # Feature fusion layer & shared Transformer encoder
├── losses/
│   └── multitask_losses.py   # Focal, Dice, Span, Calibration, and Multitask loss functions
├── evaluation/
│   └── metrics.py            # Official metrics: Character IoU, ECE, Precision, Recall, F1
├── trainer/
│   └── lightning_module.py   # PyTorch Lightning module for multitask training
├── scripts/
│   ├── download_data.py      # Script to download dataset splits and images
│   ├── cache_features.py     # Extracts and saves VLM activations to HDF5 cache
│   └── train.py              # Training entrypoint using PyTorch Lightning and Hydra
├── submission/
│   └── make_submission.py    # Test inference engine and submission JSON writer
├── tests/
│   ├── test_dataset.py       # Unit tests for alignment and tokenization
│   ├── test_metrics.py       # Unit tests for official evaluation metrics
│   └── test_model.py         # Unit tests for model forward, heads, and loss gradients
├── README.md                 # Project documentation (this file)
└── requirements.txt          # Python dependencies
```

## Setup Instructions

### 1. Environment Requirements
- Python 3.11+
- PyTorch 2.x
- Transformers & Accelerate
- PyTorch Lightning
- Hydra (for configuration)
- h5py (for caching activations)
- tqdm, numpy, pandas, pillow

Install all dependencies:
```bash
pip install -r requirements.txt
```

### 2. Download and Decompress Dataset
Run the automated downloader script to fetch the SHROOM-Vision data:
```bash
python scripts/download_data.py
```
This extracts the English, French, Italian, and Chinese training and test sets under `data/distrib/` and the VLM images.

### 3. Pre-Extract and Cache VLM features
To avoid running the massive Qwen2.5-VL model on every training epoch, run the pre-extractor script once to capture hidden states, cross-attentions, and ViT features to HDF5 cache files:
```bash
python scripts/cache_features.py \
    --jsonl-path data/distrib/shroom-vision.train.en.labeled.jsonl \
    --images-dir data \
    --output-cache-dir data/cache
```

### 4. Train the Model
Train the multitask model on the cached features:
```bash
python scripts/train.py
```
This will train the Shared Feature Encoder and prediction heads, monitoring character-level IoU and ECE on the validation split, and save checkpoints to `checkpoints/`.

### 5. Generate Submission Predictions
Run inference on the unlabeled test set to generate the JSON submission file:
```bash
python submission/make_submission.py
```

### 6. Run Unit Tests
Verify model correctness, token alignments, and loss gradients by running the test suite:
```bash
pytest tests/
```

## Methodology

### 1. Representation Fusion
For each generated response token $t$, the system fuses:
- **Decoder Hidden State**: The language model's hidden representation $h_t \in \mathbb{R}^{d_{\text{hidden}}}$.
- **Attended Vision Feature**: The visual patch activations weighted by the token's cross-attention weights over the image patches:
  $$v_t^{\text{attended}} = \sum_i a_{t, i} u_i$$
- **Global Query Context**: The final query token representation representing prompt encoding.
- **Grounding Features**: Verification signals from pluggable OCR/Object verification modules.

### 2. Predictions & Optimization
- **Hallucination Risk (Head 1)**: Sequence-level and token-level binary logit.
- **BIO Spans (Head 2)**: Sequence tagging classification (O, B, I) optimized using **Span Loss** (a combined Focal Loss and Dice Loss to counter heavy label imbalance).
- **Taxonomy (Head 3)**: Classifier predicting error categories: *Invention*, *Mischaracterization*, *OCR Problem*, *Miscounting*, and *Other*. Loss is masked to train only on tokens within hallucination spans.
- **Confidence Calibration (Head 4)**: Fuses predictions using a calibration network or learned temperature scaling to output well-calibrated token probabilities, optimized using a continuous **Calibration Loss** (Brier Score/MSE).
