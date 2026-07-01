# Detailed Hallucination Type Analysis

**Probe:** Gemma3-12B/query_token_layer_n
**Analysis Date:** 2025-10-05 20:14:19

---

## Overall Performance

**Test AUROC:** 0.9349

---

## Performance by Basic Hallucination Type

| Basic Hallucination Type | AUROC | Samples | Hallucination | No Hallucination |
|----------------------------------------|-------|---------|---------------|------------------|
| Object-Related | 0.9673 | 691 | 81 | 610 |
| Other | 0.9144 | 632 | 71 | 561 |
| Attribute-Related | 0.9140 | 341 | 40 | 301 |
| Relationship | 0.8847 | 336 | 20 | 316 |

---

## Performance by Domain Type

| Domain Type | AUROC | Samples | Hallucination | No Hallucination |
|----------------------------------------|-------|---------|---------------|------------------|
| Text & OCR | 0.9840 | 105 | 5 | 100 |
| Visual Understanding | 0.9532 | 598 | 83 | 515 |
| Attribute Recognition | 0.9481 | 623 | 46 | 577 |
| Knowledge & Identity | 0.8943 | 119 | 24 | 95 |
| Spatial Reasoning | 0.8877 | 348 | 20 | 328 |
| Math & Calculation | 0.8797 | 118 | 12 | 106 |
| General QA | 0.7796 | 54 | 5 | 49 |
| Temporal & Video | 0.5196 | 35 | 17 | 18 |

---

## Performance by Answer Type

| Answer Type | AUROC | Samples | Hallucination | No Hallucination |
|----------------------------------------|-------|---------|---------------|------------------|
| Yes/No | 0.9030 | 1317 | 212 | 1105 |
| Number | N/A | 132 | 0 | 132 |
| Open-Ended | N/A | 402 | 0 | 402 |
| Selection | N/A | 11 | 0 | 11 |
| Unanswerable | N/A | 138 | 0 | 138 |

---

