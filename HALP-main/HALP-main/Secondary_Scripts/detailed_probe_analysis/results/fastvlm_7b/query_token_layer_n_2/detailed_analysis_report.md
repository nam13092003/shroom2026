# Detailed Hallucination Type Analysis

**Probe:** FastVLM-7B/query_token_layer_n_2
**Analysis Date:** 2025-10-05 20:15:14

---

## Overall Performance

**Test AUROC:** 0.6139

---

## Performance by Basic Hallucination Type

| Basic Hallucination Type | AUROC | Samples | Hallucination | No Hallucination |
|----------------------------------------|-------|---------|---------------|------------------|
| Object-Related | 0.6778 | 690 | 38 | 652 |
| Attribute-Related | 0.6440 | 324 | 30 | 294 |
| Other | 0.5980 | 645 | 84 | 561 |
| Relationship | 0.5502 | 341 | 22 | 319 |

---

## Performance by Domain Type

| Domain Type | AUROC | Samples | Hallucination | No Hallucination |
|----------------------------------------|-------|---------|---------------|------------------|
| Math & Calculation | 0.7654 | 129 | 20 | 109 |
| Attribute Recognition | 0.7287 | 606 | 32 | 574 |
| Visual Understanding | 0.6665 | 581 | 44 | 537 |
| Spatial Reasoning | 0.5534 | 346 | 22 | 324 |
| Text & OCR | 0.4508 | 106 | 6 | 100 |
| Temporal & Video | 0.4420 | 35 | 10 | 25 |
| Knowledge & Identity | 0.4328 | 143 | 34 | 109 |
| General QA | 0.3194 | 54 | 6 | 48 |

---

## Performance by Answer Type

| Answer Type | AUROC | Samples | Hallucination | No Hallucination |
|----------------------------------------|-------|---------|---------------|------------------|
| Yes/No | 0.5220 | 1292 | 174 | 1118 |
| Number | N/A | 146 | 0 | 146 |
| Open-Ended | N/A | 387 | 0 | 387 |
| Selection | N/A | 6 | 0 | 6 |
| Unanswerable | N/A | 169 | 0 | 169 |

---

