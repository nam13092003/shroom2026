# Detailed Hallucination Type Analysis

**Probe:** Gemma3-12B/query_token_layer_n_2
**Analysis Date:** 2025-10-05 20:14:24

---

## Overall Performance

**Test AUROC:** 0.9247

---

## Performance by Basic Hallucination Type

| Basic Hallucination Type | AUROC | Samples | Hallucination | No Hallucination |
|----------------------------------------|-------|---------|---------------|------------------|
| Object-Related | 0.9516 | 691 | 81 | 610 |
| Other | 0.9153 | 632 | 71 | 561 |
| Relationship | 0.9093 | 336 | 20 | 316 |
| Attribute-Related | 0.8953 | 341 | 40 | 301 |

---

## Performance by Domain Type

| Domain Type | AUROC | Samples | Hallucination | No Hallucination |
|----------------------------------------|-------|---------|---------------|------------------|
| Text & OCR | 0.9580 | 105 | 5 | 100 |
| Attribute Recognition | 0.9458 | 623 | 46 | 577 |
| Visual Understanding | 0.9374 | 598 | 83 | 515 |
| Spatial Reasoning | 0.9090 | 348 | 20 | 328 |
| Knowledge & Identity | 0.8675 | 119 | 24 | 95 |
| Math & Calculation | 0.8616 | 118 | 12 | 106 |
| General QA | 0.8204 | 54 | 5 | 49 |
| Temporal & Video | 0.4804 | 35 | 17 | 18 |

---

## Performance by Answer Type

| Answer Type | AUROC | Samples | Hallucination | No Hallucination |
|----------------------------------------|-------|---------|---------------|------------------|
| Yes/No | 0.8917 | 1317 | 212 | 1105 |
| Number | N/A | 132 | 0 | 132 |
| Open-Ended | N/A | 402 | 0 | 402 |
| Selection | N/A | 11 | 0 | 11 |
| Unanswerable | N/A | 138 | 0 | 138 |

---

