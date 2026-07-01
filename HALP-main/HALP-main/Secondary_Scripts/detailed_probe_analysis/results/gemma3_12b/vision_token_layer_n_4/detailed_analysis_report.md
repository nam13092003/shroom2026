# Detailed Hallucination Type Analysis

**Probe:** Gemma3-12B/vision_token_layer_n_4
**Analysis Date:** 2025-10-05 20:14:55

---

## Overall Performance

**Test AUROC:** 0.6698

---

## Performance by Basic Hallucination Type

| Basic Hallucination Type | AUROC | Samples | Hallucination | No Hallucination |
|----------------------------------------|-------|---------|---------------|------------------|
| Other | 0.7541 | 632 | 71 | 561 |
| Object-Related | 0.6718 | 691 | 81 | 610 |
| Relationship | 0.6217 | 336 | 20 | 316 |
| Attribute-Related | 0.5261 | 341 | 40 | 301 |

---

## Performance by Domain Type

| Domain Type | AUROC | Samples | Hallucination | No Hallucination |
|----------------------------------------|-------|---------|---------------|------------------|
| Math & Calculation | 0.7535 | 118 | 12 | 106 |
| Attribute Recognition | 0.6588 | 623 | 46 | 577 |
| Visual Understanding | 0.6513 | 598 | 83 | 515 |
| General QA | 0.6388 | 54 | 5 | 49 |
| Spatial Reasoning | 0.6308 | 348 | 20 | 328 |
| Knowledge & Identity | 0.6068 | 119 | 24 | 95 |
| Text & OCR | 0.5240 | 105 | 5 | 100 |
| Temporal & Video | 0.5098 | 35 | 17 | 18 |

---

## Performance by Answer Type

| Answer Type | AUROC | Samples | Hallucination | No Hallucination |
|----------------------------------------|-------|---------|---------------|------------------|
| Yes/No | 0.5914 | 1317 | 212 | 1105 |
| Number | N/A | 132 | 0 | 132 |
| Open-Ended | N/A | 402 | 0 | 402 |
| Selection | N/A | 11 | 0 | 11 |
| Unanswerable | N/A | 138 | 0 | 138 |

---

