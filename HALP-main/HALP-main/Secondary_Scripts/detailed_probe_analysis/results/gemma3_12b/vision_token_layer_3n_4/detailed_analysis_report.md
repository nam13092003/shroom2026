# Detailed Hallucination Type Analysis

**Probe:** Gemma3-12B/vision_token_layer_3n_4
**Analysis Date:** 2025-10-05 20:14:41

---

## Overall Performance

**Test AUROC:** 0.5995

---

## Performance by Basic Hallucination Type

| Basic Hallucination Type | AUROC | Samples | Hallucination | No Hallucination |
|----------------------------------------|-------|---------|---------------|------------------|
| Other | 0.6626 | 632 | 71 | 561 |
| Object-Related | 0.6200 | 691 | 81 | 610 |
| Attribute-Related | 0.5027 | 341 | 40 | 301 |
| Relationship | 0.4377 | 336 | 20 | 316 |

---

## Performance by Domain Type

| Domain Type | AUROC | Samples | Hallucination | No Hallucination |
|----------------------------------------|-------|---------|---------------|------------------|
| Math & Calculation | 0.7697 | 118 | 12 | 106 |
| General QA | 0.7163 | 54 | 5 | 49 |
| Visual Understanding | 0.6138 | 598 | 83 | 515 |
| Attribute Recognition | 0.5886 | 623 | 46 | 577 |
| Knowledge & Identity | 0.5257 | 119 | 24 | 95 |
| Spatial Reasoning | 0.4360 | 348 | 20 | 328 |
| Temporal & Video | 0.3987 | 35 | 17 | 18 |
| Text & OCR | 0.3680 | 105 | 5 | 100 |

---

## Performance by Answer Type

| Answer Type | AUROC | Samples | Hallucination | No Hallucination |
|----------------------------------------|-------|---------|---------------|------------------|
| Yes/No | 0.5514 | 1317 | 212 | 1105 |
| Number | N/A | 132 | 0 | 132 |
| Open-Ended | N/A | 402 | 0 | 402 |
| Selection | N/A | 11 | 0 | 11 |
| Unanswerable | N/A | 138 | 0 | 138 |

---

