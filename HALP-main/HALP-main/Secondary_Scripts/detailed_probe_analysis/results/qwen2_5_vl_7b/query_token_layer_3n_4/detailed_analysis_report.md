# Detailed Hallucination Type Analysis

**Probe:** Qwen2.5-VL-7B/query_token_layer_3n_4
**Analysis Date:** 2025-10-05 20:17:37

---

## Overall Performance

**Test AUROC:** 0.9215

---

## Performance by Basic Hallucination Type

| Basic Hallucination Type | AUROC | Samples | Hallucination | No Hallucination |
|----------------------------------------|-------|---------|---------------|------------------|
| Object-Related | 0.9726 | 691 | 41 | 650 |
| Other | 0.8934 | 639 | 62 | 577 |
| Attribute-Related | 0.8695 | 323 | 15 | 308 |
| Relationship | 0.3508 | 347 | 3 | 344 |

---

## Performance by Domain Type

| Domain Type | AUROC | Samples | Hallucination | No Hallucination |
|----------------------------------------|-------|---------|---------------|------------------|
| General QA | 0.9773 | 46 | 2 | 44 |
| Visual Understanding | 0.9646 | 572 | 46 | 526 |
| Text & OCR | 0.9534 | 106 | 4 | 102 |
| Attribute Recognition | 0.9126 | 607 | 19 | 588 |
| Knowledge & Identity | 0.8674 | 139 | 29 | 110 |
| Math & Calculation | 0.8566 | 130 | 8 | 122 |
| Temporal & Video | 0.7152 | 43 | 10 | 33 |
| Spatial Reasoning | 0.3503 | 357 | 3 | 354 |

---

## Performance by Answer Type

| Answer Type | AUROC | Samples | Hallucination | No Hallucination |
|----------------------------------------|-------|---------|---------------|------------------|
| Yes/No | 0.8977 | 1330 | 121 | 1209 |
| Number | N/A | 118 | 0 | 118 |
| Open-Ended | N/A | 402 | 0 | 402 |
| Selection | N/A | 5 | 0 | 5 |
| Unanswerable | N/A | 145 | 0 | 145 |

---

