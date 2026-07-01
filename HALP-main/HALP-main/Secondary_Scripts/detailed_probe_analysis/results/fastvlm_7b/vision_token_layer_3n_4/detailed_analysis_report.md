# Detailed Hallucination Type Analysis

**Probe:** FastVLM-7B/vision_token_layer_3n_4
**Analysis Date:** 2025-10-05 20:15:32

---

## Overall Performance

**Test AUROC:** 0.6879

---

## Performance by Basic Hallucination Type

| Basic Hallucination Type | AUROC | Samples | Hallucination | No Hallucination |
|----------------------------------------|-------|---------|---------------|------------------|
| Object-Related | 0.7861 | 690 | 38 | 652 |
| Other | 0.6846 | 645 | 84 | 561 |
| Attribute-Related | 0.5463 | 324 | 30 | 294 |
| Relationship | 0.5234 | 341 | 22 | 319 |

---

## Performance by Domain Type

| Domain Type | AUROC | Samples | Hallucination | No Hallucination |
|----------------------------------------|-------|---------|---------------|------------------|
| Text & OCR | 0.9442 | 106 | 6 | 100 |
| General QA | 0.7639 | 54 | 6 | 48 |
| Visual Understanding | 0.7605 | 581 | 44 | 537 |
| Math & Calculation | 0.7021 | 129 | 20 | 109 |
| Attribute Recognition | 0.6831 | 606 | 32 | 574 |
| Spatial Reasoning | 0.5262 | 346 | 22 | 324 |
| Temporal & Video | 0.5000 | 35 | 10 | 25 |
| Knowledge & Identity | 0.4870 | 143 | 34 | 109 |

---

## Performance by Answer Type

| Answer Type | AUROC | Samples | Hallucination | No Hallucination |
|----------------------------------------|-------|---------|---------------|------------------|
| Yes/No | 0.6167 | 1292 | 174 | 1118 |
| Number | N/A | 146 | 0 | 146 |
| Open-Ended | N/A | 387 | 0 | 387 |
| Selection | N/A | 6 | 0 | 6 |
| Unanswerable | N/A | 169 | 0 | 169 |

---

