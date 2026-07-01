# Detailed Hallucination Type Analysis

**Probe:** FastVLM-7B/query_token_layer0
**Analysis Date:** 2025-10-05 20:15:00

---

## Overall Performance

**Test AUROC:** 0.6715

---

## Performance by Basic Hallucination Type

| Basic Hallucination Type | AUROC | Samples | Hallucination | No Hallucination |
|----------------------------------------|-------|---------|---------------|------------------|
| Other | 0.6704 | 645 | 84 | 561 |
| Attribute-Related | 0.6596 | 324 | 30 | 294 |
| Object-Related | 0.6588 | 690 | 38 | 652 |
| Relationship | 0.5762 | 341 | 22 | 319 |

---

## Performance by Domain Type

| Domain Type | AUROC | Samples | Hallucination | No Hallucination |
|----------------------------------------|-------|---------|---------------|------------------|
| Attribute Recognition | 0.7467 | 606 | 32 | 574 |
| Math & Calculation | 0.7374 | 129 | 20 | 109 |
| Text & OCR | 0.7192 | 106 | 6 | 100 |
| Visual Understanding | 0.6618 | 581 | 44 | 537 |
| Spatial Reasoning | 0.5796 | 346 | 22 | 324 |
| Knowledge & Identity | 0.5308 | 143 | 34 | 109 |
| General QA | 0.4514 | 54 | 6 | 48 |
| Temporal & Video | 0.4420 | 35 | 10 | 25 |

---

## Performance by Answer Type

| Answer Type | AUROC | Samples | Hallucination | No Hallucination |
|----------------------------------------|-------|---------|---------------|------------------|
| Yes/No | 0.5988 | 1292 | 174 | 1118 |
| Number | N/A | 146 | 0 | 146 |
| Open-Ended | N/A | 387 | 0 | 387 |
| Selection | N/A | 6 | 0 | 6 |
| Unanswerable | N/A | 169 | 0 | 169 |

---

