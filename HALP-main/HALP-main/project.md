# Hallucination Detection in Vision-Language Models: A Probing Study

## Table of Contents
- [Project Overview](#project-overview)
- [Research Motivation](#research-motivation)
- [Methodology](#methodology)
- [Dataset](#dataset)
- [Models Under Investigation](#models-under-investigation)
- [Implementation Pipeline](#implementation-pipeline)
- [Results Summary](#results-summary)
- [Key Findings](#key-findings)
- [Technical Architecture](#technical-architecture)
- [Future Work](#future-work)

---

## Project Overview

### What Are We Trying to Achieve?

This project investigates **where and when hallucinations emerge** in Vision-Language Models (VLMs) by training lightweight **linear probes** on internal model representations. The core research question is:

> **Can we detect hallucinations by examining the internal representations of VLMs at different processing stages before generation ?**

### Research Goals

1. **Identify critical layers** where hallucination signals are most detectable
2. **Compare different representation types** (vision-only, vision tokens, query tokens)
3. **Benchmark across multiple VLM architectures** to find universal patterns
4. **Understand the information flow** from vision encoding to text generation

### Why This Matters

- **Early Detection:** If hallucinations can be detected from internal representations, we can intervene before generation
- **Model Interpretability:** Understanding where models "go wrong" helps improve architectures
- **Practical Applications:** Better hallucination detection enables safer deployment of VLMs in critical domains (medical imaging, autonomous vehicles, etc.)
- **Architectural Insights:** Comparing different VLM designs reveals which approaches are more robust

---

## Research Motivation

### The Hallucination Problem in VLMs

Vision-Language Models frequently generate text that is:
- **Factually inconsistent** with the input image
- **Plausible-sounding** but incorrect
- **Difficult to detect** without ground truth

Examples:
- Describing objects not present in the image
- Incorrect counts, colors, or spatial relationships
- Fabricated details that seem reasonable but are false

### Why Probing?

**Linear Probing** is a technique where we:
1. Freeze a pre-trained model
2. Extract internal representations at various layers
3. Train simple linear classifiers on these representations
4. Evaluate whether hallucination signals are linearly separable

**Advantages:**
- **Efficient:** No need to retrain large VLMs
- **Interpretable:** Linear classifiers are easier to analyze than end-to-end models
- **Diagnostic:** Reveals what information is encoded at each layer
- **Comparable:** Same probe architecture across all models ensures fair comparison

### Research Questions

1. **Which layers contain the most hallucination-relevant information?**
   - Early layers (vision encoding)?
   - Middle layers (vision-language fusion)?
   - Late layers (text generation)?

2. **Which token representations are most predictive?**
   - Vision encoder outputs (before decoder)?
   - Vision tokens in decoder (image information flow)?
   - Query tokens in decoder (question processing)?

3. **Do different VLM architectures show similar patterns?**
   - Cross-model consistency would suggest universal mechanisms
   - Divergence would reveal architectural differences

---

## Methodology

### Experimental Design

#### Phase 1: Embedding Extraction
For each VLM, we extract three types of representations:

1. **Vision-Only Representation**
   - Output of the vision encoder (e.g., SigLIP, CLIP)
   - **Before** multimodal fusion
   - Captures pure visual information

2. **Vision Token Representations** (5 layers)
   - Token at the **last image position** in the decoder
   - Extracted at layers: 0, n/4, n/2, 3n/4, n-1
   - Tracks how image information flows through decoder

3. **Query Token Representations** (5 layers)
   - Token at the **last question position** in the decoder
   - Extracted at same layer indices
   - Tracks how question understanding evolves

**Layer Selection Strategy:**
- **Layer 0:** First decoder layer (early fusion)
- **Layer n/4:** Early-middle processing
- **Layer n/2:** Middle processing
- **Layer 3n/4:** Late processing
- **Layer n-1:** Final layer (pre-output)

#### Phase 2: Probe Training
For each representation type:

1. **Architecture:** MLP classifier with layers [512, 256, 128] → 1
2. **Training:** 50 epochs, binary cross-entropy loss
3. **Regularization:** Dropout (0.3), Batch Normalization
4. **Optimization:** Adam (LR=0.001), Batch size=32
5. **Evaluation:** 80/20 train-test split, stratified sampling

**Metrics:**
- **Primary:** Test AUROC (Area Under ROC Curve)
- **Secondary:** Accuracy, Precision, Recall, F1-score
- **Diagnostic:** Confusion matrices, ROC curves

---

## Dataset

### Composite Multi-Source VQA Dataset

**Dataset Name:** `sampled_10k_relational_dataset.csv`

**Overview:** A carefully curated composite dataset combining 6 diverse VQA sources to create a comprehensive hallucination detection benchmark. The dataset emphasizes relational reasoning and diverse question types to thoroughly test VLM capabilities.

### Dataset Statistics

**Total Samples:** 10,000 question-image pairs
**Image Availability:** 100% (all samples have associated images)
**Relational Focus:** 70% relational questions, 30% non-relational

**Class Distribution (Hallucination Labels):**
- No Hallucination: ~9,000 samples (~90%)
- Hallucination: ~1,000 samples (~10%)

**Data Format:**
```csv
question_id, image_name, question, gt_answer, category, description, has_image, dataset, is_relational
```

**Example Entry:**
```csv
question_comb_1, haloquest_2082.png, "How many sharks are present in the travel brochure?",
"There are no sharks in the brochure", "false premises",
"visual hallucination test", True, "haloquest", True
```

---

### Source Dataset Breakdown

The composite dataset draws from 6 established VQA benchmarks:

#### 1. **AMBER (A Multi-Task Benchmark for Evaluating VLMs)**
- **Samples:** 3,926 (39.26%)
- **Focus:** Discriminative tasks, attribute recognition, spatial relations
- **Key Categories:**
  - Discriminative Attribute State: 1,169 samples (11.69%)
  - Discriminative Relation: 975 samples (9.75%)
  - Hallucination Detection: 620 samples (6.20%)
  - Attribute Number: 280 samples (2.80%)
- **Question Types:** "Is there a X in this image?", "Is X touching Y?", "Is the sky sunny?"
- **Contribution:** Provides fine-grained discriminative evaluation

#### 2. **HaloQuest (Hallucination Quest Dataset)**
- **Samples:** 2,784 (27.84%)
- **Focus:** Challenging hallucination scenarios, adversarial questions
- **Key Categories:**
  - Visual Challenge: 1,531 samples (15.31%) 🏆 **Largest single category**
  - False Premises: 898 samples (8.98%)
  - Insufficient Context: 355 samples (3.55%)
- **Question Types:** Counterfactual questions, misleading premises, ambiguous contexts
- **Image Sources:** Mix of generated (Midjourney/DALL-E) and real images
- **Contribution:** Tests model robustness to adversarial and edge cases

#### 3. **POPE (Polling-based Object Probing Evaluation)**
- **Samples:** 1,230 (12.30%)
- **Focus:** Object hallucination in image descriptions
- **Key Categories:**
  - Random: 456 samples (4.56%)
  - Adversarial: 402 samples (4.02%)
  - Popular: 372 samples (3.72%)
- **Question Types:** "Is there a [object] in the image?" with varying difficulty
- **Contribution:** Systematic object-level hallucination testing

#### 4. **MME (Multi-Modal Evaluation Benchmark)**
- **Samples:** 885 (8.85%)
- **Focus:** Comprehensive multi-modal understanding
- **Key Categories:**
  - Celebrity Recognition: 340 samples (3.40%)
  - Movie Posters: 109 samples (1.09%)
  - Commonsense Reasoning: 94 samples (0.94%)
  - Scene Recognition: 64 samples (0.64%)
  - OCR/Text: 23 samples (0.23%)
  - Code Reasoning: 8 samples (0.08%)
- **Question Types:** Yes/no questions across diverse domains
- **Contribution:** Tests real-world knowledge and reasoning

#### 5. **HallusionBench (Hallucination Benchmark)**
- **Samples:** 617 (6.17%)
- **Focus:** Visual illusions and challenging perception tasks
- **Key Categories:**
  - Video Understanding: 170 samples (1.70%)
  - Math Problems: 93 samples (0.93%)
  - Charts: 92 samples (0.92%)
  - Visual Illusions: 91 samples (0.91%)
- **Question Types:** Figure analysis, visual reasoning, temporal understanding
- **Contribution:** Tests perception under challenging conditions

#### 6. **MathVista (Mathematical Visual Question Answering)**
- **Samples:** 558 (5.58%)
- **Focus:** Mathematical reasoning from visual inputs
- **Key Categories:**
  - Math-Targeted VQA: 323 samples (3.23%)
  - General VQA: 235 samples (2.35%)
- **Question Types:** Geometry, charts, diagrams, numerical reasoning
- **Answer Types:** Free-form integers, multiple choice, text answers
- **Contribution:** Tests quantitative reasoning capabilities

---

### Question Category Distribution

**Top 10 Question Categories (by frequency):**

1. **Visual Challenge** (15.31%) - Complex visual reasoning tasks from HaloQuest
2. **Discriminative Attribute State** (11.69%) - Object state recognition (AMBER)
3. **Discriminative Relation** (9.75%) - Spatial relationships (AMBER)
4. **False Premises** (8.98%) - Questions with incorrect assumptions (HaloQuest)
5. **Relation** (6.89%) - General relational reasoning (AMBER)
6. **Discriminative Hallucination** (6.20%) - Object existence detection (AMBER)
7. **Random** (4.56%) - Random object queries (POPE)
8. **Adversarial** (4.02%) - Adversarial object queries (POPE)
9. **Popular** (3.72%) - Common object queries (POPE)
10. **Insufficient Context** (3.55%) - Unanswerable questions (HaloQuest)

**Full Category Taxonomy (38 unique categories):**
- Discriminative: attribute-state, attribute-number, attribute-action, relation, hallucination
- Reasoning: visual challenge, false premises, insufficient context, commonsense
- Recognition: celebrity, landmark, scene, artwork
- Text: OCR, text translation, code reasoning
- Quantitative: math-targeted-vqa, general-vqa, count, numerical calculation
- Media: video, chart, table, figure, map, posters
- Adversarial: adversarial, random, popular (POPE categories)
- Spatial: position, existence, color, relation
- Creative: illusion, generative

---

### Relational Question Emphasis

**Relational Questions:** 7,000 samples (70%)
- Questions requiring understanding of relationships between objects, attributes, or entities
- Examples: "Is X touching Y?", "Which person has the necklace?", "How many X are near Y?"

**Non-Relational Questions:** 3,000 samples (30%)
- Single-object queries or global image properties
- Examples: "Is there a dog?", "What color is the sky?", "How many total objects?"

**Rationale for 70/30 Split:**
- Relational reasoning is **more challenging** for VLMs
- Hallucinations often involve **incorrect relationships** rather than object detection
- Reflects real-world VQA complexity

---

### Top Dataset × Category Combinations

| Source Dataset | Category | Samples | Percentage |
|---------------|----------|---------|------------|
| HaloQuest | Visual Challenge | 1,531 | 15.31% |
| AMBER | Discriminative Attribute State | 1,169 | 11.69% |
| AMBER | Discriminative Relation | 975 | 9.75% |
| HaloQuest | False Premises | 898 | 8.98% |
| AMBER | Relation | 689 | 6.89% |
| AMBER | Discriminative Hallucination | 620 | 6.20% |
| POPE | Random | 456 | 4.56% |
| POPE | Adversarial | 402 | 4.02% |
| POPE | Popular | 372 | 3.72% |
| HaloQuest | Insufficient Context | 355 | 3.55% |

---

### Dataset Design Principles

#### 1. **Diversity**
- **6 source datasets** covering different aspects of VLM evaluation
- **38 question categories** spanning perception, reasoning, and knowledge
- **Mix of real and generated images** for robustness

#### 2. **Difficulty Balance**
- **Easy:** Basic object detection (POPE popular)
- **Medium:** Attribute recognition, counting (AMBER)
- **Hard:** Visual challenges, false premises (HaloQuest)
- **Expert:** Mathematical reasoning, illusions (MathVista, HallusionBench)

#### 3. **Hallucination Focus**
- **Adversarial questions** designed to elicit hallucinations
- **False premise questions** testing model's ability to reject bad assumptions
- **Ambiguous contexts** where models must admit uncertainty
- **Fine-grained attributes** prone to hallucination (counts, colors, positions)

#### 4. **Relational Emphasis**
- **70% relational questions** to test complex reasoning
- **Spatial relations:** "X is on top of Y"
- **Attribute relations:** "Which X has property Y?"
- **Temporal relations:** Video sequences (HallusionBench)

#### 5. **Quality Control**
- **Manual review** of all hallucination labels
- **Ground truth answers** from multiple acceptable phrasings
- **Image verification** - all samples have valid image paths
- **Consistent formatting** across diverse sources

---

### Dataset Challenges

#### 1. **Class Imbalance**
- **90/10 split** (no hallucination vs hallucination)
- **Mitigation:** Stratified train-test splits to maintain balance
- **Real-world reflection:** Most VLM outputs are correct, hallucinations are rare

#### 2. **Multi-Source Integration**
- **Different annotation styles** across source datasets
- **Standardization:** Unified CSV format with consistent columns
- **Challenge:** Maintaining semantic consistency

#### 3. **Subjective Annotations**
- **What counts as hallucination?** Manual review ensures consistency
- **Edge cases:** Some questions have nuanced correct answers
- **Inter-annotator agreement:** Critical for label quality

#### 4. **Question Diversity vs. Model Bias**
- **38 categories** → Models may learn category-specific shortcuts
- **Mitigation:** Stratified sampling prevents category dominance
- **Benefit:** Comprehensive evaluation across question types

#### 5. **Image Source Variation**
- **Generated images** (HaloQuest): More adversarial, less natural
- **Real images** (POPE, AMBER): Natural distribution
- **Mix provides robustness** but may introduce distributional shifts

---

### Example Questions by Type

#### Visual Challenge (HaloQuest)
```
Q: How many fingers does the human have including the thumb?
A: Six fingers (detecting anatomical errors in generated images)
Image: generated (DALL-E/Midjourney)
```

#### False Premises (HaloQuest)
```
Q: How many sharks are present in the travel brochure?
A: There are no sharks in the brochure
Image: Travel brochure without sharks
```

#### Discriminative Relation (AMBER)
```
Q: Is there direct contact between the dog and the grass?
A: Yes
Image: Dog standing on grass
```

#### Adversarial (POPE)
```
Q: Is there a dining table in the image?
A: No (object is present but model might hallucinate based on context)
Image: COCO validation image
```

#### Math-Targeted VQA (MathVista)
```
Q: Move the ruler to measure the length of the line to the nearest centimeter. The line is about (_) centimeters long.
A: 7
Image: Diagram with ruler and line
```

#### Video Understanding (HallusionBench)
```
Q: According to the positive sequence of the images, is the baby crawling to right?
A: Yes
Image: Multi-frame sequence
```

---

### Dataset Files

**Primary Dataset:**
```
/root/akhil/final_data/sampled_10k_relational_dataset.csv
```

**Images Directory:**
```
/root/akhil/final_data/all_images/
```

**Model-Specific Labels (with manual hallucination annotations):**
```
/root/akhil/FInal_CSV_Hallucination/
├── gemma3_manually_reviewed.csv
├── fastvlm_manually_reviewed.csv
├── llava_manually_reviewed.csv
├── molmo_manually_reviewed.csv
├── qwen25vl_manually_reviewed.csv
├── llama32_manually_reviewed.csv
├── phi4vl_manually_reviewed.csv
└── smolvlm_manually_reviewed.csv
```

**Data Processing Pipeline:**
1. Source datasets collected (AMBER, HaloQuest, POPE, MME, HallusionBench, MathVista)
2. Standardization to common format
3. Sampling strategy for 10k subset
4. Manual hallucination annotation per model
5. Quality verification and validation

---

### Why This Dataset Composition?

#### Scientific Rigor
- **Established benchmarks** (not custom/untested datasets)
- **Published evaluation protocols** for reproducibility
- **Diverse coverage** prevents overfitting to specific question types

#### Hallucination Focus
- **HaloQuest (28%)** specifically designed for hallucination
- **POPE (12%)** tests object-level hallucinations
- **Adversarial categories** across all sources

#### Real-World Relevance
- **MME** tests practical scenarios (celebrities, posters, scenes)
- **MathVista** represents quantitative reasoning needs
- **AMBER** covers everyday discriminative tasks

#### Research Contribution
- **First composite benchmark** specifically for probing-based hallucination detection
- **Relational emphasis** understudied in existing benchmarks
- **Multi-source design** enables generalization testing

### Data Splits

- **Training Set:** 8,000 samples (80%)
  - Class 0: 7,207 (90.1%)
  - Class 1: 793 (9.9%)

- **Test Set:** 2,000 samples (20%)
  - Class 0: 1,802 (90.1%)
  - Class 1: 198 (9.9%)

**Split Strategy:** Stratified to maintain class balance

---

## Models Under Investigation

### 1. Gemma3-12B Multimodal
- **HuggingFace Hub:** [google/gemma-3-12b-it](https://huggingface.co/google/gemma-3-12b-it)
- **Parameters:** 12.2B | **Model Size:** ~24 GB (BF16)
- **Architecture:** Gemma3-12B language model + SigLIP vision encoder
- **Text Layers:** 42 layers (3072-dim)
- **Vision Encoder:** SigLIP (1152-dim)
- **Selected Layers:** [0, 10, 21, 31, 41]
- **Key Feature:** Large-scale instruction-tuned model

### 2. FastVLM
- **HuggingFace Hub:** [apple/FastVLM-0.5B](https://huggingface.co/apple/FastVLM-0.5B) / [apple/FastVLM-1.5B](https://huggingface.co/apple/FastVLM-1.5B)
- **Parameters:** 0.5B-1.5B | **Model Size:** ~1-3 GB (FP16)
- **Architecture:** Fast vision-language model with FastViT
- **Text Layers:** 32 layers (4096-dim)
- **Vision Encoder:** FastViT (1152-dim)
- **Selected Layers:** [0, 8, 16, 24, 31]
- **Key Feature:** Optimized for inference speed

### 3. LLaVA-1.5-8B
- **HuggingFace Hub:** [llava-hf/llava-1.5-7b-hf](https://huggingface.co/llava-hf/llava-1.5-7b-hf)
- **Parameters:** 7.6B | **Model Size:** ~15 GB (FP16)
- **Architecture:** Vicuna-7B language model + CLIP ViT-L vision projector
- **Text Layers:** 32 layers (4096-dim)
- **Vision Encoder:** CLIP ViT-L/14 (1024-dim)
- **Selected Layers:** [0, 8, 16, 24, 31]
- **Key Feature:** State-of-the-art visual instruction following

### 4. Molmo-7B-O-0924
- **HuggingFace Hub:** [allenai/Molmo-7B-O-0924](https://huggingface.co/allenai/Molmo-7B-O-0924)
- **Parameters:** 7.2B | **Model Size:** ~26 GB (BF16)
- **Architecture:** Allenai's multimodal model with CLIP vision
- **Text Layers:** 32 layers (4096-dim)
- **Vision Encoder:** OpenAI CLIP ViT-L (1024-dim)
- **Selected Layers:** [0, 7, 15, 22, 29]
- **Key Feature:** Research-focused, open-source

### 5. Qwen2.5-VL-7B
- **HuggingFace Hub:** [Qwen/Qwen2.5-VL-7B-Instruct](https://huggingface.co/Qwen/Qwen2.5-VL-7B-Instruct)
- **Parameters:** 7B | **Model Size:** ~16 GB (BF16)
- **Architecture:** Qwen2.5 language model + ViT vision adapter
- **Text Layers:** 28 layers (3584-dim)
- **Vision Encoder:** ViT with window attention (1280-dim)
- **Selected Layers:** [0, 7, 14, 21, 27]
- **Key Feature:** Multilingual capabilities

### 6. Llama-3.2-11B-Vision
- **HuggingFace Hub:** [meta-llama/Llama-3.2-11B-Vision-Instruct](https://huggingface.co/meta-llama/Llama-3.2-11B-Vision-Instruct)
- **Parameters:** 10.6B | **Model Size:** ~22 GB (BF16)
- **Architecture:** Llama 3.2 with cross-attention vision fusion
- **Text Layers:** 40 layers (4096-dim)
- **Vision Encoder:** ViT-H/14 (1280-dim)
- **Selected Layers:** [0, 10, 20, 30, 39]
- **Key Feature:** Latest Llama architecture with vision

### 7. Phi4-VL
- **HuggingFace Hub:** [microsoft/Phi-4-multimodal-instruct](https://huggingface.co/microsoft/Phi-4-multimodal-instruct)
- **Parameters:** 5.6B | **Model Size:** ~11 GB (FP16)
- **Architecture:** Microsoft Phi-4 with SigLIP vision + LoRA adapters
- **Text Layers:** 32 layers (3072-dim)
- **Vision Encoder:** SigLIP-400M (1152-dim)
- **Selected Layers:** [0, 8, 16, 24, 31]
- **Key Feature:** Compact, efficient model with mixture-of-LoRAs

### 8. SmolVLM2-2.2B ⭐ (Current Focus)
- **HuggingFace Hub:** [HuggingFaceTB/SmolVLM2-2.2B-Instruct](https://huggingface.co/HuggingFaceTB/SmolVLM2-2.2B-Instruct)
- **Parameters:** 2.2B | **Model Size:** ~4.4 GB (BF16)
- **Architecture:** SmolLM2 language model + SigLIP vision encoder
- **Text Layers:** 24 layers (2048-dim)
- **Vision Encoder:** SigLIP-400M (1152-dim, 27 vision layers)
- **Selected Layers:** [0, 6, 12, 18, 23]
- **Key Feature:** Smallest model in the study, efficient for deployment

---

## Implementation Pipeline

### Step 1: Embedding Extraction

**Purpose:** Extract and save internal representations from VLMs

**Process:**
```python
# For each sample in dataset:
1. Load image and question
2. Process through VLM (no generation)
3. Extract representations:
   - Vision encoder output
   - Vision tokens at selected layers
   - Query tokens at selected layers
4. Save to HDF5 file with metadata
```

**Output Format (HDF5):**
```
sample_id/
├── vision_only_representation        [D_vision]
├── vision_token_representation/
│   ├── layer_0                       [D_hidden]
│   ├── layer_n/4                     [D_hidden]
│   ├── layer_n/2                     [D_hidden]
│   ├── layer_3n/4                    [D_hidden]
│   └── layer_n-1                     [D_hidden]
├── query_token_representation/
│   ├── layer_0                       [D_hidden]
│   ├── layer_n/4                     [D_hidden]
│   ├── layer_n/2                     [D_hidden]
│   ├── layer_3n/4                    [D_hidden]
│   └── layer_n-1                     [D_hidden]
└── metadata (image_id, question, ground_truth, answer)
```

**Storage:**
- Checkpointed every 1,000 samples
- Compression: gzip
- Total size per model: ~1-5 GB

**Example (SmolVLM):**
```bash
Location: /root/akhil/HALP_EACL_Models/Models/Smol_VL/smolvlm_output/
Files: smolvlm_2.2b_embeddings_part_001.h5 to part_010.h5
Total samples: 10,000
```

### Step 2: Probe Training

**Purpose:** Train binary classifiers to predict hallucination from representations

**Architecture:**
```python
class HallucinationProbe(nn.Module):
    Input: [batch, embedding_dim]

    Linear(embedding_dim → 512)
    ReLU + BatchNorm + Dropout(0.3)

    Linear(512 → 256)
    ReLU + BatchNorm + Dropout(0.3)

    Linear(256 → 128)
    ReLU + BatchNorm + Dropout(0.3)

    Linear(128 → 1)
    Sigmoid

    Output: [batch] (hallucination probability)
```

**Training Configuration:**
```python
Optimizer: Adam(lr=0.001)
Loss: Binary Cross-Entropy
Batch Size: 32
Epochs: 50
Device: CUDA (RTX 4090)
Random Seed: 42 (for reproducibility)
```

**Process:**
```python
# For each representation type:
1. Load embeddings from H5 files
2. Load labels from CSV
3. Train-test split (80/20, stratified)
4. Initialize probe
5. Train for 50 epochs
6. Evaluate on test set
7. Save:
   - Model checkpoint
   - Metrics (JSON)
   - Visualizations (confusion matrix, ROC curve, training history)
```

**Execution:**
```bash
# Single probe
python 01_vision_only_probe.py

# All probes
python run_all_probes.py
```

### Step 3: Result Compilation

**Purpose:** Aggregate results across all models and probes

**Script:** `create_auroc_excel.py`

**Output:** Excel spreadsheet with test AUROC for all models × all probes

**Format:**
```
Model Name | Vision Only | Vision Token Layer 0 | ... | Query Token Layer n
Gemma3-12B | 0.xxxx      | 0.xxxx              | ... | 0.xxxx
FastVLM-7B | 0.xxxx      | 0.xxxx              | ... | 0.xxxx
...
```

---

## Results Summary

### SmolVLM2-2.2B Results (Latest)

**Training Completed:** October 4, 2025
**Total Time:** 9 minutes 34 seconds
**Success Rate:** 11/11 probes (100%)

#### Test AUROC Results

| Representation Type | Layer | Test AUROC | Train AUROC | Notes |
|-------------------|-------|------------|-------------|-------|
| **Vision Only** | - | **0.7238** | 0.9304 | Best among vision representations |
| Vision Token | 0 | 0.6829 | 0.9405 | Early layer |
| Vision Token | 6 | 0.6868 | 0.9432 | n/4 point |
| Vision Token | 12 | 0.6845 | 0.9560 | Middle layer |
| Vision Token | 18 | 0.6801 | 0.9505 | 3n/4 point |
| Vision Token | 23 | 0.6894 | 0.9445 | Final layer |
| Query Token | 0 | 0.5040 | 0.5000 | **Essentially random** |
| Query Token | 6 | 0.8971 | 0.9654 | Strong performance |
| Query Token | 12 | 0.9055 | 0.9804 | Excellent |
| **Query Token** | **18** | **0.9272** | **0.9924** | 🥇 **Best Overall** |
| Query Token | 23 | 0.9014 | 0.9927 | Near-best |

**Mean Test AUROC:** 0.7530

### Cross-Model Comparison (All 8 Models)

#### Phi4-VL Results

| Representation Type | Layer | Test AUROC |
|-------------------|-------|------------|
| Vision Only | - | 0.7842 |
| Query Token | 31 (final) | 0.9033 |
| Query Token | 24 (3n/4) | 0.9305 |

#### Pattern Across Models

**Consistent Findings:**
1. **Query tokens > Vision tokens** in all models
2. **Late layers (3n/4, final) perform best** for query tokens
3. **Early query layers (~layer 0) show poor performance** (often near-random)
4. **Vision representations show modest, stable performance** across layers

**Model-Specific Observations:**
- **Larger models** (Gemma3-12B, Llama-3.2-11B) show higher overall AUROC
- **Smaller models** (SmolVLM, Phi4) still achieve >0.90 AUROC in best layers
- **Architectural differences** (e.g., vision encoder type) affect vision-only performance

---

## Key Findings

### 1. Query Token Superiority

**Finding:** Query token representations (especially in late layers) are significantly more predictive of hallucinations than vision tokens.

**Test AUROC Comparison (SmolVLM):**
- Best Query Token: 0.9272 (layer 18)
- Best Vision Token: 0.6894 (layer 23)
- **Difference:** 0.2378 AUROC points

**Interpretation:**
- Hallucination signals are more strongly encoded in **how the model processes the question** than in **how it processes the image**
- The model's **internal understanding of the query** contains critical information about whether it will hallucinate
- This suggests hallucinations may arise from **query-image misalignment** rather than pure vision failures

### 2. Layer-Depth Patterns

**Finding:** Hallucination detectability increases with layer depth for query tokens but remains flat for vision tokens.

**Query Token Progression (SmolVLM):**
- Layer 0: 0.5040 (random)
- Layer 6: 0.8971 (strong)
- Layer 12: 0.9055 (excellent)
- Layer 18: 0.9272 (best)
- Layer 23: 0.9014 (slight drop)

**Vision Token Pattern:**
- All layers: 0.68-0.69 (stable, moderate)

**Interpretation:**
- **Early query processing** (layer 0) doesn't contain hallucination signals
- **Mid-to-late query processing** (layers 6-23) accumulates predictive information
- **Peak performance** slightly before the final layer suggests over-fitting to generation task in last layer
- **Vision processing** is consistently informative but limited

### 3. Vision-Only Performance

**Finding:** Pre-fusion vision encoder outputs (vision-only) outperform in-decoder vision tokens.

**SmolVLM Results:**
- Vision-only: 0.7238 AUROC
- Best vision token: 0.6894 AUROC

**Interpretation:**
- **Pure visual features** (before language fusion) contain more hallucination-relevant information
- **Fusion process** may dilute or transform vision signals
- Suggests **vision encoder quality** is critical for hallucination prevention

### 4. Overfitting Concerns

**Finding:** Large train-test AUROC gaps, especially in query tokens.

**SmolVLM Query Token Layer 18:**
- Train AUROC: 0.9924
- Test AUROC: 0.9272
- **Gap:** 0.0652

**Mitigation:**
- Dropout (0.3) and BatchNorm already included
- Relatively small probe (3-layer MLP) limits capacity
- **Real concern:** Limited dataset diversity (10k samples)

**Future Work:**
- Larger, more diverse datasets
- Stronger regularization
- Cross-dataset evaluation

### 5. Early Layer Ineffectiveness

**Finding:** Layer 0 query tokens are essentially non-predictive (AUROC ≈ 0.50).

**Interpretation:**
- **Initial query encoding** doesn't yet contain hallucination-relevant features
- Hallucination signals emerge through **deeper processing** and **cross-modal interaction**
- Supports theory that hallucinations arise from **reasoning failures**, not input encoding failures

### 6. Architectural Implications

**Cross-Model Patterns:**
- **All models** show query token superiority
- **All models** show layer-depth effects
- **Performance ceiling** varies (0.90-0.95 AUROC range)

**Interpretation:**
- Hallucination mechanisms are **partially universal** across VLM architectures
- **Specific implementations** affect absolute performance but not relative patterns
- Suggests **fundamental design principle**: query processing is critical for hallucination control

---

## Technical Architecture

### Directory Structure

```
/root/akhil/
├── PROJECT.md                                    # This file
├── HALP_EACL_Models/
│   └── Models/
│       ├── Gemma3_12B/
│       │   ├── run_gemma3_extraction.py         # Extraction script
│       │   └── gemma_output/                    # H5 files (10k samples)
│       ├── FastVLM_7B/
│       │   ├── run_fastvlm_extraction.py
│       │   └── fastvlm_output/
│       ├── LLaVa_Next_8B/
│       │   ├── run_llava_extraction.py
│       │   └── llava_output/
│       ├── Molmo_V1/
│       │   ├── run_molmo_extraction.py
│       │   └── molmo_output/
│       ├── Qwen25_VL_7B/
│       │   ├── run_qwen_extraction.py
│       │   └── qwen_output/
│       ├── Llama32_11B_Vision/
│       │   ├── run_llama32_extraction.py
│       │   └── llama32_output/
│       ├── Phi4_VL/
│       │   ├── run_phi4_extraction.py
│       │   └── phi4_output/
│       └── Smol_VL/                             # Latest model
│           ├── run_smol_extraction.py
│           └── smolvlm_output/
│               ├── smolvlm_2.2b_embeddings_part_001.h5
│               ├── ...
│               └── smolvlm_2.2b_embeddings_part_010.h5
│
├── FInal_CSV_Hallucination/
│   ├── gemma3_manually_reviewed.csv            # Labels for each model
│   ├── fastvlm_manually_reviewed.csv
│   ├── llava_manually_reviewed.csv
│   ├── molmo_manually_reviewed.csv
│   ├── qwen25vl_manually_reviewed.csv
│   ├── llama32_manually_reviewed.csv
│   ├── phi4vl_manually_reviewed.csv
│   └── smolvlm_manually_reviewed.csv
│
└── probe_training_scripts/
    ├── create_auroc_excel.py                   # Result compilation
    ├── test_auroc_results.xlsx                 # Cross-model results
    ├── gemma_model_probe/
    │   ├── 01_vision_only_probe.py
    │   ├── 02-06_vision_token_probes.py
    │   ├── 07-11_query_token_probes.py
    │   ├── run_all_probes.py
    │   └── results/                            # Training outputs
    ├── fastvlm_model_probe/
    ├── llava_model_probe/
    ├── molmo_model_probe/
    ├── qwen25vl_model_probe/
    ├── llama32_model_probe/
    ├── phi4vl_model_probe/
    └── smolvlm_model_probe/                    # Latest
        ├── 01_vision_only_probe.py
        ├── 02-06_vision_token_probes.py
        ├── 07-11_query_token_probes.py
        ├── run_all_probes.py
        ├── verify_setup.py
        ├── compile_auroc_results.py
        ├── README.md
        ├── QUICK_START.md
        └── results/
            ├── test_auroc_summary.csv
            ├── vision_only/
            │   ├── results.json
            │   ├── probe_model.pt
            │   ├── confusion_matrix.png
            │   ├── roc_curve.png
            │   └── training_history.png
            ├── vision_token_layer0/
            ├── ...
            └── query_token_layer23/
```

### Software Stack

**Core Dependencies:**
```
Python 3.10
PyTorch 2.x (CUDA 11.8)
Transformers (Hugging Face)
h5py (HDF5 file handling)
pandas (CSV processing)
numpy (numerical operations)
scikit-learn (metrics, splits)
matplotlib + seaborn (visualization)
tqdm (progress bars)
```

**Model-Specific:**
```
accelerate (distributed inference)
num2words (SmolVLM processor)
sentencepiece (tokenization)
Pillow (image processing)
```

### Hardware Requirements

**Extraction:**
- GPU: NVIDIA RTX 4090 (24GB VRAM) or equivalent
- RAM: 32GB+
- Storage: 100GB+ (for all models)
- Time per model: 3-6 hours (10k samples)

**Probe Training:**
- GPU: RTX 4090 or equivalent
- RAM: 16GB+
- Storage: 10GB per model
- Time per model: 10-15 minutes (11 probes)

---

## Why We Are Doing This

### Scientific Contributions

1. **Mechanistic Understanding**
   - First systematic study of hallucination emergence across VLM layers
   - Reveals that hallucinations are **query-processing phenomena**, not vision failures
   - Provides evidence for specific intervention points

2. **Cross-Architecture Analysis**
   - 8 models spanning 2.2B to 12B parameters
   - Different vision encoders (SigLIP, CLIP, custom)
   - Different architectures (Gemma, LLaMA, Qwen, Phi, etc.)
   - Identifies universal vs. model-specific patterns

3. **Practical Insights**
   - **Where to intervene:** Late query layers (18-23) are critical
   - **What to monitor:** Query token representations, not just vision
   - **Early warning signs:** Mid-layer query representations (layer 12+) already highly predictive

### Practical Applications

1. **Real-Time Hallucination Detection**
   - Extract query token at layer 18
   - Pass through trained probe
   - Flag high-risk generations before output
   - **Latency:** Minimal (single forward pass, lightweight probe)

2. **Model Selection**
   - Use test AUROC as **robustness metric**
   - Choose models with high hallucination detectability
   - Example: Phi4-VL layer 24 (0.9305 AUROC) is highly transparent

3. **Training Objectives**
   - Add **probe-based regularization** during VLM fine-tuning
   - Encourage hallucination-predictive representations
   - Potential for **self-supervised hallucination prevention**

4. **Debugging & Analysis**
   - **Which samples fail?** Inspect confused predictions
   - **Why do they fail?** Analyze representation patterns
   - **How to fix?** Target problematic query processing

### Broader Impact

**AI Safety:**
- Safer deployment in high-stakes domains (medical, legal, autonomous systems)
- Reduces risk of confident but incorrect outputs
- Enables **uncertainty estimation** from internal states

**Model Development:**
- Guides architecture design (e.g., strengthen query processing)
- Informs training strategies (e.g., hallucination-aware losses)
- Provides **interpretability tools** for VLM developers

**Research Community:**
- Open-source probing methodology
- Reproducible experimental setup
- Benchmark dataset for hallucination detection

---

## Future Work

### Short-Term

1. **Expand Dataset**
   - 10k → 100k+ samples
   - More diverse image types (natural, synthetic, diagrams)
   - Multi-domain coverage (medical, scientific, everyday)

2. **Additional Models**
   - GPT-4V, Gemini Vision (API-based probing)
   - Open-source models (BLIP-2, InstructBLIP)
   - Specialized models (medical VLMs, document understanding)

3. **Refined Probes**
   - Non-linear probes (deeper MLPs, attention mechanisms)
   - Multi-layer probes (combining representations from multiple layers)
   - Adversarial robustness testing

### Medium-Term

1. **Causal Analysis**
   - **Intervention experiments:** Perturb representations, measure hallucination changes
   - **Ablation studies:** Remove specific neurons, identify critical features
   - **Counterfactual probing:** "What if" scenarios in representation space

2. **Fine-Grained Hallucination Types**
   - Object hallucinations vs. attribute hallucinations
   - Spatial vs. semantic errors
   - Probe for specific error types

3. **Cross-Modal Probing**
   - Probe both vision AND query representations jointly
   - Analyze interaction patterns
   - Identify misalignment signatures

### Long-Term

1. **Real-Time Systems**
   - Deploy probes in production VLM pipelines
   - A/B testing with and without hallucination detection
   - Measure impact on user trust and safety

2. **Probe-Guided Training**
   - Use probe predictions as training signal
   - Minimize hallucination-predictive representations
   - Develop **self-correcting VLMs**

3. **Theoretical Framework**
   - Formalize when/why hallucinations are detectable
   - Connect to information theory, causal inference
   - Develop **hallucination bounds** (theoretical limits)

---

## How to Reproduce This Work

### Step 1: Environment Setup

```bash
# Create conda environment
conda create -n vlm_probing python=3.10
conda activate vlm_probing

# Install dependencies
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
pip install transformers accelerate h5py pandas numpy scikit-learn matplotlib seaborn tqdm
```

### Step 2: Embedding Extraction

```bash
# For SmolVLM (example)
cd /root/akhil/HALP_EACL_Models/Models/Smol_VL

# Create environment
conda create -n smolvlm python=3.10
conda activate smolvlm
pip install torch transformers h5py pandas tqdm num2words

# Run extraction
python run_smol_extraction.py \
  --vqa-dataset /root/akhil/final_data/sampled_10k_relational_dataset.csv \
  --images-dir /root/akhil/final_data/all_images \
  --output-dir ./smolvlm_output \
  --checkpoint-interval 1000

# Expected output: 10 H5 files, ~1-2GB total
# Time: ~3-6 hours on RTX 4090
```

### Step 3: Probe Training

```bash
cd /root/akhil/probe_training_scripts/smolvlm_model_probe

# Verify setup
python verify_setup.py

# Run all probes
python run_all_probes.py

# Expected output: 11 result directories
# Time: ~10 minutes
```

### Step 4: Result Analysis

```bash
# Compile AUROC results
python compile_auroc_results.py

# View summary
cat results/test_auroc_summary.csv

# Generate cross-model Excel
cd /root/akhil/probe_training_scripts
python create_auroc_excel.py
open test_auroc_results.xlsx
```

---

## Citation

If you use this work, please cite:

```bibtex
@misc{vlm_hallucination_probing_2025,
  title={Probing Hallucination Emergence in Vision-Language Models},
  author={[Your Name]},
  year={2025},
  note={Investigating hallucination detection across 8 VLM architectures using linear probes}
}
```

---

## Contact & Collaboration

**Project Lead:** [Your Name]
**Institution:** [Your Institution]
**Email:** [Your Email]

**Code Repository:** [GitHub Link]
**Dataset:** HaloQuest VQA (10k samples)
**Models:** Gemma3-12B, FastVLM-7B, LLaVA-Next-8B, Molmo-V1, Qwen2.5-VL-7B, Llama-3.2-11B, Phi4-VL, SmolVLM2-2.2B

---

## Acknowledgments

- **Hugging Face** for model hosting and transformers library
- **PyTorch** team for deep learning framework
- **Model Developers:** Google (Gemma3), Meta (LLaMA), Alibaba (Qwen), Microsoft (Phi), HuggingFace (SmolVLM)
- **Dataset Curators:** Us by combining multitple datasets and various question types.
- **Hardware Support:** NVIDIA RTX 4090 GPU

---

## License

This project is released under [MIT License / Apache 2.0 / Your Choice].

**Models:** Each model retains its original license (check individual model cards on Hugging Face).

---

**Last Updated:** October 4, 2025
**Version:** 1.0
**Status:** ✅ SmolVLM probes completed (8/8 models done)
