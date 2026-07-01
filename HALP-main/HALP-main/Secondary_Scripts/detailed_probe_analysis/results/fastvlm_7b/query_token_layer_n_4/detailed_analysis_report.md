# Detailed Hallucination Type Analysis

**Probe:** FastVLM-7B/query_token_layer_n_4
**Analysis Date:** 2025-10-05 20:15:19

---

## Overall Performance

**Test AUROC:** 0.6623

---

## Performance by Basic Hallucination Type

| Basic Hallucination Type | AUROC | Samples | Hallucination | No Hallucination |
|----------------------------------------|-------|---------|---------------|------------------|
| Object-Related | 0.6967 | 690 | 38 | 652 |
| Other | 0.6607 | 645 | 84 | 561 |
| Relationship | 0.6114 | 341 | 22 | 319 |
| Attribute-Related | 0.5792 | 324 | 30 | 294 |

---

## Performance by Domain Type

| Domain Type | AUROC | Samples | Hallucination | No Hallucination |
|----------------------------------------|-------|---------|---------------|------------------|
| Math & Calculation | 0.7592 | 129 | 20 | 109 |
| Text & OCR | 0.6875 | 106 | 6 | 100 |
| Visual Understanding | 0.6825 | 581 | 44 | 537 |
| Attribute Recognition | 0.6700 | 606 | 32 | 574 |
| Spatial Reasoning | 0.6150 | 346 | 22 | 324 |
| General QA | 0.5312 | 54 | 6 | 48 |
| Knowledge & Identity | 0.4843 | 143 | 34 | 109 |
| Temporal & Video | 0.4180 | 35 | 10 | 25 |

---

## Performance by Answer Type

| Answer Type | AUROC | Samples | Hallucination | No Hallucination |
|----------------------------------------|-------|---------|---------------|------------------|
| Yes/No | 0.5754 | 1292 | 174 | 1118 |
| Number | N/A | 146 | 0 | 146 |
| Open-Ended | N/A | 387 | 0 | 387 |
| Selection | N/A | 6 | 0 | 6 |
| Unanswerable | N/A | 169 | 0 | 169 |

---

