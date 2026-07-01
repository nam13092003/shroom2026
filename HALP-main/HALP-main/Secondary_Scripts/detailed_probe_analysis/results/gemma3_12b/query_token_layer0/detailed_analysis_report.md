# Detailed Hallucination Type Analysis

**Probe:** Gemma3-12B/query_token_layer0
**Analysis Date:** 2025-10-05 20:14:10

---

## Overall Performance

**Test AUROC:** 0.7165

---

## Performance by Basic Hallucination Type

| Basic Hallucination Type | AUROC | Samples | Hallucination | No Hallucination |
|----------------------------------------|-------|---------|---------------|------------------|
| Other | 0.8491 | 632 | 71 | 561 |
| Object-Related | 0.7906 | 691 | 81 | 610 |
| Attribute-Related | 0.7395 | 341 | 40 | 301 |
| Relationship | 0.3646 | 336 | 20 | 316 |

---

## Performance by Domain Type

| Domain Type | AUROC | Samples | Hallucination | No Hallucination |
|----------------------------------------|-------|---------|---------------|------------------|
| Attribute Recognition | 0.8408 | 623 | 46 | 577 |
| General QA | 0.8408 | 54 | 5 | 49 |
| Math & Calculation | 0.8121 | 118 | 12 | 106 |
| Visual Understanding | 0.7388 | 598 | 83 | 515 |
| Text & OCR | 0.7060 | 105 | 5 | 100 |
| Knowledge & Identity | 0.6548 | 119 | 24 | 95 |
| Temporal & Video | 0.6503 | 35 | 17 | 18 |
| Spatial Reasoning | 0.3878 | 348 | 20 | 328 |

---

## Performance by Answer Type

| Answer Type | AUROC | Samples | Hallucination | No Hallucination |
|----------------------------------------|-------|---------|---------------|------------------|
| Yes/No | 0.5856 | 1317 | 212 | 1105 |
| Number | N/A | 132 | 0 | 132 |
| Open-Ended | N/A | 402 | 0 | 402 |
| Selection | N/A | 11 | 0 | 11 |
| Unanswerable | N/A | 138 | 0 | 138 |

---

