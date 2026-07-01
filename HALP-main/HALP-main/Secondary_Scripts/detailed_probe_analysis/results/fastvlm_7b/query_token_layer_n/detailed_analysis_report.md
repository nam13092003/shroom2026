# Detailed Hallucination Type Analysis

**Probe:** FastVLM-7B/query_token_layer_n
**Analysis Date:** 2025-10-05 20:15:09

---

## Overall Performance

**Test AUROC:** 0.6136

---

## Performance by Basic Hallucination Type

| Basic Hallucination Type | AUROC | Samples | Hallucination | No Hallucination |
|----------------------------------------|-------|---------|---------------|------------------|
| Object-Related | 0.6631 | 690 | 38 | 652 |
| Other | 0.6253 | 645 | 84 | 561 |
| Attribute-Related | 0.5487 | 324 | 30 | 294 |
| Relationship | 0.4947 | 341 | 22 | 319 |

---

## Performance by Domain Type

| Domain Type | AUROC | Samples | Hallucination | No Hallucination |
|----------------------------------------|-------|---------|---------------|------------------|
| Math & Calculation | 0.7147 | 129 | 20 | 109 |
| Text & OCR | 0.6725 | 106 | 6 | 100 |
| Visual Understanding | 0.6438 | 581 | 44 | 537 |
| Attribute Recognition | 0.6290 | 606 | 32 | 574 |
| General QA | 0.5069 | 54 | 6 | 48 |
| Spatial Reasoning | 0.4945 | 346 | 22 | 324 |
| Knowledge & Identity | 0.4508 | 143 | 34 | 109 |
| Temporal & Video | 0.3780 | 35 | 10 | 25 |

---

## Performance by Answer Type

| Answer Type | AUROC | Samples | Hallucination | No Hallucination |
|----------------------------------------|-------|---------|---------------|------------------|
| Yes/No | 0.5450 | 1292 | 174 | 1118 |
| Number | N/A | 146 | 0 | 146 |
| Open-Ended | N/A | 387 | 0 | 387 |
| Selection | N/A | 6 | 0 | 6 |
| Unanswerable | N/A | 169 | 0 | 169 |

---

