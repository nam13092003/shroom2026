# Detailed Hallucination Type Analysis

**Probe:** Gemma3-12B/vision_token_layer_n_2
**Analysis Date:** 2025-10-05 20:14:50

---

## Overall Performance

**Test AUROC:** 0.6146

---

## Performance by Basic Hallucination Type

| Basic Hallucination Type | AUROC | Samples | Hallucination | No Hallucination |
|----------------------------------------|-------|---------|---------------|------------------|
| Object-Related | 0.6666 | 691 | 81 | 610 |
| Other | 0.6390 | 632 | 71 | 561 |
| Attribute-Related | 0.5363 | 341 | 40 | 301 |
| Relationship | 0.5060 | 336 | 20 | 316 |

---

## Performance by Domain Type

| Domain Type | AUROC | Samples | Hallucination | No Hallucination |
|----------------------------------------|-------|---------|---------------|------------------|
| General QA | 0.8306 | 54 | 5 | 49 |
| Visual Understanding | 0.6491 | 598 | 83 | 515 |
| Attribute Recognition | 0.6199 | 623 | 46 | 577 |
| Math & Calculation | 0.6097 | 118 | 12 | 106 |
| Spatial Reasoning | 0.5070 | 348 | 20 | 328 |
| Text & OCR | 0.4740 | 105 | 5 | 100 |
| Knowledge & Identity | 0.4436 | 119 | 24 | 95 |
| Temporal & Video | 0.4248 | 35 | 17 | 18 |

---

## Performance by Answer Type

| Answer Type | AUROC | Samples | Hallucination | No Hallucination |
|----------------------------------------|-------|---------|---------------|------------------|
| Yes/No | 0.5600 | 1317 | 212 | 1105 |
| Number | N/A | 132 | 0 | 132 |
| Open-Ended | N/A | 402 | 0 | 402 |
| Selection | N/A | 11 | 0 | 11 |
| Unanswerable | N/A | 138 | 0 | 138 |

---

