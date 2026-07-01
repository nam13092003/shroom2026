# Detailed Hallucination Type Analysis

**Probe:** Gemma3-12B/query_token_layer_n_4
**Analysis Date:** 2025-10-05 20:14:29

---

## Overall Performance

**Test AUROC:** 0.8119

---

## Performance by Basic Hallucination Type

| Basic Hallucination Type | AUROC | Samples | Hallucination | No Hallucination |
|----------------------------------------|-------|---------|---------------|------------------|
| Other | 0.8575 | 632 | 71 | 561 |
| Object-Related | 0.8464 | 691 | 81 | 610 |
| Attribute-Related | 0.8281 | 341 | 40 | 301 |
| Relationship | 0.7267 | 336 | 20 | 316 |

---

## Performance by Domain Type

| Domain Type | AUROC | Samples | Hallucination | No Hallucination |
|----------------------------------------|-------|---------|---------------|------------------|
| General QA | 0.9143 | 54 | 5 | 49 |
| Attribute Recognition | 0.8935 | 623 | 46 | 577 |
| Math & Calculation | 0.8758 | 118 | 12 | 106 |
| Visual Understanding | 0.8164 | 598 | 83 | 515 |
| Text & OCR | 0.7960 | 105 | 5 | 100 |
| Spatial Reasoning | 0.7367 | 348 | 20 | 328 |
| Temporal & Video | 0.5915 | 35 | 17 | 18 |
| Knowledge & Identity | 0.5447 | 119 | 24 | 95 |

---

## Performance by Answer Type

| Answer Type | AUROC | Samples | Hallucination | No Hallucination |
|----------------------------------------|-------|---------|---------------|------------------|
| Yes/No | 0.7111 | 1317 | 212 | 1105 |
| Number | N/A | 132 | 0 | 132 |
| Open-Ended | N/A | 402 | 0 | 402 |
| Selection | N/A | 11 | 0 | 11 |
| Unanswerable | N/A | 138 | 0 | 138 |

---

