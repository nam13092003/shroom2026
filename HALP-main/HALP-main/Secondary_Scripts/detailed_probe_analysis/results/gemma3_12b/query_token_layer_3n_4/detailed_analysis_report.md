# Detailed Hallucination Type Analysis

**Probe:** Gemma3-12B/query_token_layer_3n_4
**Analysis Date:** 2025-10-05 20:14:15

---

## Overall Performance

**Test AUROC:** 0.9315

---

## Performance by Basic Hallucination Type

| Basic Hallucination Type | AUROC | Samples | Hallucination | No Hallucination |
|----------------------------------------|-------|---------|---------------|------------------|
| Object-Related | 0.9698 | 691 | 81 | 610 |
| Relationship | 0.9369 | 336 | 20 | 316 |
| Attribute-Related | 0.9211 | 341 | 40 | 301 |
| Other | 0.8868 | 632 | 71 | 561 |

---

## Performance by Domain Type

| Domain Type | AUROC | Samples | Hallucination | No Hallucination |
|----------------------------------------|-------|---------|---------------|------------------|
| Text & OCR | 0.9840 | 105 | 5 | 100 |
| Visual Understanding | 0.9593 | 598 | 83 | 515 |
| Attribute Recognition | 0.9549 | 623 | 46 | 577 |
| Spatial Reasoning | 0.9392 | 348 | 20 | 328 |
| Knowledge & Identity | 0.9127 | 119 | 24 | 95 |
| Math & Calculation | 0.8078 | 118 | 12 | 106 |
| General QA | 0.8000 | 54 | 5 | 49 |
| Temporal & Video | 0.4412 | 35 | 17 | 18 |

---

## Performance by Answer Type

| Answer Type | AUROC | Samples | Hallucination | No Hallucination |
|----------------------------------------|-------|---------|---------------|------------------|
| Yes/No | 0.9019 | 1317 | 212 | 1105 |
| Number | N/A | 132 | 0 | 132 |
| Open-Ended | N/A | 402 | 0 | 402 |
| Selection | N/A | 11 | 0 | 11 |
| Unanswerable | N/A | 138 | 0 | 138 |

---

