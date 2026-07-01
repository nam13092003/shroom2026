# Detailed Hallucination Type Analysis

**Probe:** Qwen2.5-VL-7B/query_token_layer0
**Analysis Date:** 2025-10-05 20:17:33

---

## Overall Performance

**Test AUROC:** 0.8614

---

## Performance by Basic Hallucination Type

| Basic Hallucination Type | AUROC | Samples | Hallucination | No Hallucination |
|----------------------------------------|-------|---------|---------------|------------------|
| Object-Related | 0.9161 | 691 | 41 | 650 |
| Other | 0.7995 | 639 | 62 | 577 |
| Attribute-Related | 0.7556 | 323 | 15 | 308 |
| Relationship | 0.5465 | 347 | 3 | 344 |

---

## Performance by Domain Type

| Domain Type | AUROC | Samples | Hallucination | No Hallucination |
|----------------------------------------|-------|---------|---------------|------------------|
| General QA | 1.0000 | 46 | 2 | 44 |
| Visual Understanding | 0.8978 | 572 | 46 | 526 |
| Text & OCR | 0.8848 | 106 | 4 | 102 |
| Attribute Recognition | 0.8488 | 607 | 19 | 588 |
| Math & Calculation | 0.8094 | 130 | 8 | 122 |
| Temporal & Video | 0.6212 | 43 | 10 | 33 |
| Spatial Reasoning | 0.5480 | 357 | 3 | 354 |
| Knowledge & Identity | 0.4596 | 139 | 29 | 110 |

---

## Performance by Answer Type

| Answer Type | AUROC | Samples | Hallucination | No Hallucination |
|----------------------------------------|-------|---------|---------------|------------------|
| Yes/No | 0.8037 | 1330 | 121 | 1209 |
| Number | N/A | 118 | 0 | 118 |
| Open-Ended | N/A | 402 | 0 | 402 |
| Selection | N/A | 5 | 0 | 5 |
| Unanswerable | N/A | 145 | 0 | 145 |

---

