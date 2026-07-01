# Detailed Hallucination Type Analysis

**Probe:** FastVLM-7B/query_token_layer_3n_4
**Analysis Date:** 2025-10-05 20:15:05

---

## Overall Performance

**Test AUROC:** 0.6475

---

## Performance by Basic Hallucination Type

| Basic Hallucination Type | AUROC | Samples | Hallucination | No Hallucination |
|----------------------------------------|-------|---------|---------------|------------------|
| Object-Related | 0.7112 | 690 | 38 | 652 |
| Other | 0.6573 | 645 | 84 | 561 |
| Attribute-Related | 0.6459 | 324 | 30 | 294 |
| Relationship | 0.5750 | 341 | 22 | 319 |

---

## Performance by Domain Type

| Domain Type | AUROC | Samples | Hallucination | No Hallucination |
|----------------------------------------|-------|---------|---------------|------------------|
| Math & Calculation | 0.7961 | 129 | 20 | 109 |
| Attribute Recognition | 0.7455 | 606 | 32 | 574 |
| Text & OCR | 0.7058 | 106 | 6 | 100 |
| General QA | 0.6910 | 54 | 6 | 48 |
| Visual Understanding | 0.6375 | 581 | 44 | 537 |
| Spatial Reasoning | 0.5782 | 346 | 22 | 324 |
| Knowledge & Identity | 0.5148 | 143 | 34 | 109 |
| Temporal & Video | 0.3820 | 35 | 10 | 25 |

---

## Performance by Answer Type

| Answer Type | AUROC | Samples | Hallucination | No Hallucination |
|----------------------------------------|-------|---------|---------------|------------------|
| Yes/No | 0.5503 | 1292 | 174 | 1118 |
| Number | N/A | 146 | 0 | 146 |
| Open-Ended | N/A | 387 | 0 | 387 |
| Selection | N/A | 6 | 0 | 6 |
| Unanswerable | N/A | 169 | 0 | 169 |

---

