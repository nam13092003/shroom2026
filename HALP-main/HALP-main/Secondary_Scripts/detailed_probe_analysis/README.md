# Detailed Hallucination Type Analysis

## 🎯 Overview

This analysis extends the category-level probe analysis by examining performance across **three additional dimensions**:

1. **Basic Hallucination Type** (4 types)
   - Object-Related
   - Relationship
   - Attribute-Related
   - Other

2. **Domain Type** (8 types)
   - Attribute Recognition
   - Visual Understanding
   - Spatial Reasoning
   - Knowledge & Identity
   - Math & Calculation
   - Text & OCR
   - General QA
   - Temporal & Video

3. **Answer Type** (5 types)
   - Yes/No
   - Open-Ended
   - Unanswerable
   - Number
   - Selection

## ✅ Execution Summary

**Status:** COMPLETE
**Total Probes Analyzed:** 65/66 (98.5%)
**Successful:** 65
**Failed:** 1 (LLaVA vision_only - shape mismatch)

## 📊 Quick Results - SmolVLM Query Token Layer 18 (Best Probe)

### Overall: AUROC 0.9272

### By Basic Hallucination Type
| Type | AUROC | Samples |
|------|-------|---------|
| **Object-Related** | **0.9733** | 708 |
| **Relationship** | **0.9633** | 317 |
| Other | 0.9185 | 621 |
| Attribute-Related | 0.8068 | 354 |

**Finding:** Object and relationship hallucinations are easiest to detect.

### By Domain Type
| Domain | AUROC | Samples |
|--------|-------|---------|
| **Text & OCR** | **0.9626** | 110 |
| **Spatial Reasoning** | **0.9610** | 331 |
| **Visual Understanding** | **0.9607** | 611 |
| General QA | 0.9271 | 50 |
| Math & Calculation | 0.9097 | 116 |
| Attribute Recognition | 0.8949 | 628 |
| Knowledge & Identity | 0.7063 | 124 |
| **Temporal & Video** | **0.3571** | 30 ⚠️ |

**Finding:** Temporal/video analysis is the weakest domain (0.36 AUROC - worse than random!).

### By Answer Type
| Type | AUROC | Samples |
|------|-------|---------|
| **Yes/No** | **0.8911** | 1314 |
| Number | N/A (single class) | 127 |
| Open-Ended | N/A (single class) | 410 |
| Selection | N/A (single class) | 11 |
| Unanswerable | N/A (single class) | 138 |

**Finding:** Only Yes/No questions have both classes in test set. Other answer types are predominantly no-hallucination.

## 📁 Output Structure

For each probe:
```
/root/akhil/probe_analysis/detailed_probe_analysis/results/{model}/{probe}/
├── basic_hallucination_type_auroc.csv    # AUROC by hallucination type
├── domain_type_auroc.csv                  # AUROC by domain
├── answer_type_auroc.csv                  # AUROC by answer format
├── detailed_analysis_report.md            # Human-readable markdown
└── detailed_summary.json                  # JSON metadata
```

**Master Summary:**
- `/root/akhil/probe_analysis/detailed_probe_analysis/detailed_analysis_summary.csv`

## 📈 Key Findings Across All Models

### 1. Basic Hallucination Type Performance

**Easiest to Detect:**
- Object-Related hallucinations (0.95+ AUROC)
- Relationship hallucinations (0.95+ AUROC)

**Hardest to Detect:**
- Attribute-Related hallucinations (0.70-0.80 AUROC)
- "Other" category varies widely (0.75-0.92 AUROC)

### 2. Domain Type Performance

**Strong Domains (0.90+ AUROC):**
- Text & OCR
- Spatial Reasoning
- Visual Understanding
- Math & Calculation

**Weak Domains (<0.70 AUROC):**
- Knowledge & Identity (requires external knowledge)
- Temporal & Video (requires temporal reasoning)

### 3. Answer Type Limitations

**Critical Finding:** Most answer types have **single-class test sets**:
- Number questions: All no-hallucination
- Open-Ended: All no-hallucination
- Selection: All no-hallucination
- Unanswerable: All no-hallucination

Only **Yes/No questions** have sufficient class balance for AUROC calculation.

## 🔍 CSV File Formats

### `basic_hallucination_type_auroc.csv`
```csv
type,num_samples,num_hallucination,num_no_hallucination,auroc,note
Object-Related,708,62,646,0.9733,
Relationship,317,4,313,0.9633,
Other,621,63,558,0.9185,
Attribute-Related,354,69,285,0.8068,
```

### `domain_type_auroc.csv`
```csv
type,num_samples,num_hallucination,num_no_hallucination,auroc,note
Text & OCR,110,9,101,0.9626,
Spatial Reasoning,331,4,327,0.9610,
Visual Understanding,611,69,542,0.9607,
...
Temporal & Video,30,14,16,0.3571,
```

### `answer_type_auroc.csv`
```csv
type,num_samples,num_hallucination,num_no_hallucination,auroc,note
Yes/No,1314,198,1116,0.8911,
Number,127,0,127,,Single class only
Open-Ended,410,0,410,,Single class only
Selection,11,0,11,,Single class only
Unanswerable,138,0,138,,Single class only
```

## 🚀 Usage

### Run for Single Probe
```bash
# Edit analyze_hallucination_types.py to specify probe
cd /root/akhil/probe_analysis/detailed_probe_analysis
python3 analyze_hallucination_types.py
```

### Run for All Probes
```bash
cd /root/akhil/probe_analysis/detailed_probe_analysis
python3 run_all_detailed_analysis.py
```

### View Results
```bash
# View all results summary
cat /root/akhil/probe_analysis/detailed_probe_analysis/detailed_analysis_summary.csv

# View specific probe results
cat /root/akhil/probe_analysis/detailed_probe_analysis/results/smolvlm2_2_2b/query_token_layer18/basic_hallucination_type_auroc.csv

# View detailed report
cat /root/akhil/probe_analysis/detailed_probe_analysis/results/smolvlm2_2_2b/query_token_layer18/detailed_analysis_report.md
```

## 📊 Analysis Across Models

### Best Models by Hallucination Type

**Object-Related Hallucinations:**
- SmolVLM Layer 18: 0.9733
- Molmo Layer 16: 0.9698
- Gemma3 Layer 47: 0.9656

**Relationship Hallucinations:**
- SmolVLM Layer 18: 0.9633
- Gemma3 Layer 47: 0.9612
- Molmo Layer 16: 0.9584

**Attribute-Related Hallucinations:**
- Molmo Layer 16: 0.8523
- SmolVLM Layer 18: 0.8068
- Gemma3 Layer 47: 0.7856

### Domain Performance Patterns

All models show similar patterns:
1. ✅ **Text & OCR** - Consistently strong (0.90+ AUROC)
2. ✅ **Spatial Reasoning** - Consistently strong (0.90+ AUROC)
3. ✅ **Visual Understanding** - Strong (0.85-0.96 AUROC)
4. ⚠️ **Knowledge & Identity** - Moderate (0.65-0.75 AUROC)
5. ❌ **Temporal & Video** - Weak (0.30-0.45 AUROC)

## 💡 Insights & Implications

### 1. Hallucination Type Detectability
- **Object presence/absence** is easiest to detect
- **Relationships** between objects are well-captured
- **Attributes** (color, size, state) are harder to detect
- Suggests vision encodings capture object and spatial info better than fine-grained attributes

### 2. Domain-Specific Challenges
- **Temporal reasoning** remains a fundamental weakness across ALL models
- **Knowledge retrieval** (celebrities, landmarks) is challenging
- **Visual reasoning** (spatial, OCR, math) works well

### 3. Answer Type Bias
- Test set has severe class imbalance for non-Yes/No questions
- All Number/Open-Ended/Selection/Unanswerable questions are no-hallucination
- Suggests dataset construction may have filtered out hallucinations in certain answer formats

### 4. Practical Recommendations
For deployment:
- ✅ Trust probe for: Object detection, spatial relations, text/OCR tasks
- ⚠️ Use caution for: Attribute recognition, knowledge-based questions
- ❌ Don't rely on for: Temporal/video understanding

## 🔧 Technical Details

### Configuration
- **Train/Test Split:** 80/20 (stratified, random_state=42)
- **Metadata Source:** `/root/akhil/final_data/sampled_10k_with_hallucination_types.csv`
- **Probe Architecture:** MLP [512, 256, 128] → 1
- **Metric:** AUROC (Area Under ROC Curve)

### Data Distribution
```
Basic Hallucination Type:
- Object-Related:    3,493 samples (34.9%)
- Other:             3,165 samples (31.7%)
- Relationship:      1,720 samples (17.2%)
- Attribute-Related: 1,622 samples (16.2%)

Domain Type:
- Attribute Recognition:  3,014 samples (30.1%)
- Visual Understanding:   2,984 samples (29.8%)
- Spatial Reasoning:      1,774 samples (17.7%)
- Knowledge & Identity:     646 samples (6.5%)
- Math & Calculation:       628 samples (6.3%)
- Text & OCR:               514 samples (5.1%)
- General QA:               270 samples (2.7%)
- Temporal & Video:         170 samples (1.7%)

Answer Type:
- Yes/No:        6,568 samples (65.7%)
- Open-Ended:    2,008 samples (20.1%)
- Unanswerable:    731 samples (7.3%)
- Number:          657 samples (6.6%)
- Selection:        36 samples (0.4%)
```

## 📚 Related Documentation

- **Main Category Analysis:** `/root/akhil/probe_analysis/FINAL_SUMMARY.md`
- **Original Analysis:** `/root/akhil/probe_analysis/README.md`
- **Project Overview:** `/root/akhil/PROJECT.md`

## ✅ Completion Checklist

- [x] Analyzed 65/66 probes successfully
- [x] Generated basic_hallucination_type breakdowns
- [x] Generated domain_type breakdowns
- [x] Generated answer_type breakdowns
- [x] Created comprehensive markdown reports
- [x] Saved CSV exports for further analysis
- [x] Documented key findings and insights

---

**Status:** ✅ **COMPLETE**
**Date:** 2025-10-05
**Location:** `/root/akhil/probe_analysis/detailed_probe_analysis/`
