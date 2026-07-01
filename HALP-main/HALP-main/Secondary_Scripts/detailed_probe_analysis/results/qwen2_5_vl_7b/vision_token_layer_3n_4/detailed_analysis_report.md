# Detailed Hallucination Type Analysis

**Probe:** Qwen2.5-VL-7B/vision_token_layer_3n_4
**Analysis Date:** 2025-10-05 20:18:03

---

## Overall Performance

**Test AUROC:** 0.6625

---

## Performance by Basic Hallucination Type

| Basic Hallucination Type | AUROC | Samples | Hallucination | No Hallucination |
|----------------------------------------|-------|---------|---------------|------------------|
| Object-Related | 0.8084 | 691 | 41 | 650 |
| Attribute-Related | 0.6205 | 323 | 15 | 308 |
| Relationship | 0.5877 | 347 | 3 | 344 |
| Other | 0.5745 | 639 | 62 | 577 |

---

## Performance by Domain Type

| Domain Type | AUROC | Samples | Hallucination | No Hallucination |
|----------------------------------------|-------|---------|---------------|------------------|
| Visual Understanding | 0.7733 | 572 | 46 | 526 |
| Attribute Recognition | 0.7270 | 607 | 19 | 588 |
| Spatial Reasoning | 0.5880 | 357 | 3 | 354 |
| Math & Calculation | 0.5645 | 130 | 8 | 122 |
| General QA | 0.5568 | 46 | 2 | 44 |
| Knowledge & Identity | 0.5129 | 139 | 29 | 110 |
| Text & OCR | 0.4142 | 106 | 4 | 102 |
| Temporal & Video | 0.3818 | 43 | 10 | 33 |

---

## Performance by Answer Type

| Answer Type | AUROC | Samples | Hallucination | No Hallucination |
|----------------------------------------|-------|---------|---------------|------------------|
| Yes/No | 0.5999 | 1330 | 121 | 1209 |
| Number | N/A | 118 | 0 | 118 |
| Open-Ended | N/A | 402 | 0 | 402 |
| Selection | N/A | 5 | 0 | 5 |
| Unanswerable | N/A | 145 | 0 | 145 |

---

