# Detailed Hallucination Type Analysis

**Probe:** FastVLM-7B/vision_token_layer_n_2
**Analysis Date:** 2025-10-05 20:15:42

---

## Overall Performance

**Test AUROC:** 0.7093

---

## Performance by Basic Hallucination Type

| Basic Hallucination Type | AUROC | Samples | Hallucination | No Hallucination |
|----------------------------------------|-------|---------|---------------|------------------|
| Object-Related | 0.8102 | 690 | 38 | 652 |
| Other | 0.6911 | 645 | 84 | 561 |
| Relationship | 0.5503 | 341 | 22 | 319 |
| Attribute-Related | 0.5196 | 324 | 30 | 294 |

---

## Performance by Domain Type

| Domain Type | AUROC | Samples | Hallucination | No Hallucination |
|----------------------------------------|-------|---------|---------------|------------------|
| Text & OCR | 0.9342 | 106 | 6 | 100 |
| Visual Understanding | 0.7894 | 581 | 44 | 537 |
| General QA | 0.7535 | 54 | 6 | 48 |
| Attribute Recognition | 0.6618 | 606 | 32 | 574 |
| Math & Calculation | 0.5952 | 129 | 20 | 109 |
| Spatial Reasoning | 0.5516 | 346 | 22 | 324 |
| Knowledge & Identity | 0.5030 | 143 | 34 | 109 |
| Temporal & Video | 0.4000 | 35 | 10 | 25 |

---

## Performance by Answer Type

| Answer Type | AUROC | Samples | Hallucination | No Hallucination |
|----------------------------------------|-------|---------|---------------|------------------|
| Yes/No | 0.6440 | 1292 | 174 | 1118 |
| Number | N/A | 146 | 0 | 146 |
| Open-Ended | N/A | 387 | 0 | 387 |
| Selection | N/A | 6 | 0 | 6 |
| Unanswerable | N/A | 169 | 0 | 169 |

---

