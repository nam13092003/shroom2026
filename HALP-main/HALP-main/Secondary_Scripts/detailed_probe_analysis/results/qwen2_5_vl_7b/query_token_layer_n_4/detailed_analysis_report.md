# Detailed Hallucination Type Analysis

**Probe:** Qwen2.5-VL-7B/query_token_layer_n_4
**Analysis Date:** 2025-10-05 20:17:51

---

## Overall Performance

**Test AUROC:** 0.8863

---

## Performance by Basic Hallucination Type

| Basic Hallucination Type | AUROC | Samples | Hallucination | No Hallucination |
|----------------------------------------|-------|---------|---------------|------------------|
| Object-Related | 0.9224 | 691 | 41 | 650 |
| Attribute-Related | 0.8848 | 323 | 15 | 308 |
| Other | 0.8234 | 639 | 62 | 577 |
| Relationship | 0.4215 | 347 | 3 | 344 |

---

## Performance by Domain Type

| Domain Type | AUROC | Samples | Hallucination | No Hallucination |
|----------------------------------------|-------|---------|---------------|------------------|
| General QA | 1.0000 | 46 | 2 | 44 |
| Attribute Recognition | 0.9381 | 607 | 19 | 588 |
| Text & OCR | 0.9314 | 106 | 4 | 102 |
| Visual Understanding | 0.9028 | 572 | 46 | 526 |
| Math & Calculation | 0.7531 | 130 | 8 | 122 |
| Temporal & Video | 0.6242 | 43 | 10 | 33 |
| Knowledge & Identity | 0.5771 | 139 | 29 | 110 |
| Spatial Reasoning | 0.4237 | 357 | 3 | 354 |

---

## Performance by Answer Type

| Answer Type | AUROC | Samples | Hallucination | No Hallucination |
|----------------------------------------|-------|---------|---------------|------------------|
| Yes/No | 0.8328 | 1330 | 121 | 1209 |
| Number | N/A | 118 | 0 | 118 |
| Open-Ended | N/A | 402 | 0 | 402 |
| Selection | N/A | 5 | 0 | 5 |
| Unanswerable | N/A | 145 | 0 | 145 |

---

