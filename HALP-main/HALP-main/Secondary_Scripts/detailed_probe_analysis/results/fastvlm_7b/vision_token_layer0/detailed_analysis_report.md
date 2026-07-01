# Detailed Hallucination Type Analysis

**Probe:** FastVLM-7B/vision_token_layer0
**Analysis Date:** 2025-10-05 20:15:27

---

## Overall Performance

**Test AUROC:** 0.6935

---

## Performance by Basic Hallucination Type

| Basic Hallucination Type | AUROC | Samples | Hallucination | No Hallucination |
|----------------------------------------|-------|---------|---------------|------------------|
| Object-Related | 0.7235 | 690 | 38 | 652 |
| Other | 0.7188 | 645 | 84 | 561 |
| Relationship | 0.5598 | 341 | 22 | 319 |
| Attribute-Related | 0.5045 | 324 | 30 | 294 |

---

## Performance by Domain Type

| Domain Type | AUROC | Samples | Hallucination | No Hallucination |
|----------------------------------------|-------|---------|---------------|------------------|
| Text & OCR | 0.8992 | 106 | 6 | 100 |
| Visual Understanding | 0.7339 | 581 | 44 | 537 |
| General QA | 0.7257 | 54 | 6 | 48 |
| Math & Calculation | 0.7227 | 129 | 20 | 109 |
| Attribute Recognition | 0.5743 | 606 | 32 | 574 |
| Spatial Reasoning | 0.5556 | 346 | 22 | 324 |
| Temporal & Video | 0.5240 | 35 | 10 | 25 |
| Knowledge & Identity | 0.5038 | 143 | 34 | 109 |

---

## Performance by Answer Type

| Answer Type | AUROC | Samples | Hallucination | No Hallucination |
|----------------------------------------|-------|---------|---------------|------------------|
| Yes/No | 0.6566 | 1292 | 174 | 1118 |
| Number | N/A | 146 | 0 | 146 |
| Open-Ended | N/A | 387 | 0 | 387 |
| Selection | N/A | 6 | 0 | 6 |
| Unanswerable | N/A | 169 | 0 | 169 |

---

