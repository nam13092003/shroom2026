# Detailed Hallucination Type Analysis

**Probe:** Qwen2.5-VL-7B/query_token_layer_n_2
**Analysis Date:** 2025-10-05 20:17:46

---

## Overall Performance

**Test AUROC:** 0.8794

---

## Performance by Basic Hallucination Type

| Basic Hallucination Type | AUROC | Samples | Hallucination | No Hallucination |
|----------------------------------------|-------|---------|---------------|------------------|
| Object-Related | 0.9506 | 691 | 41 | 650 |
| Attribute-Related | 0.8478 | 323 | 15 | 308 |
| Other | 0.8251 | 639 | 62 | 577 |
| Relationship | 0.3924 | 347 | 3 | 344 |

---

## Performance by Domain Type

| Domain Type | AUROC | Samples | Hallucination | No Hallucination |
|----------------------------------------|-------|---------|---------------|------------------|
| General QA | 0.9773 | 46 | 2 | 44 |
| Text & OCR | 0.9363 | 106 | 4 | 102 |
| Visual Understanding | 0.9267 | 572 | 46 | 526 |
| Attribute Recognition | 0.9112 | 607 | 19 | 588 |
| Math & Calculation | 0.7193 | 130 | 8 | 122 |
| Knowledge & Identity | 0.6320 | 139 | 29 | 110 |
| Temporal & Video | 0.5545 | 43 | 10 | 33 |
| Spatial Reasoning | 0.4030 | 357 | 3 | 354 |

---

## Performance by Answer Type

| Answer Type | AUROC | Samples | Hallucination | No Hallucination |
|----------------------------------------|-------|---------|---------------|------------------|
| Yes/No | 0.8222 | 1330 | 121 | 1209 |
| Number | N/A | 118 | 0 | 118 |
| Open-Ended | N/A | 402 | 0 | 402 |
| Selection | N/A | 5 | 0 | 5 |
| Unanswerable | N/A | 145 | 0 | 145 |

---

