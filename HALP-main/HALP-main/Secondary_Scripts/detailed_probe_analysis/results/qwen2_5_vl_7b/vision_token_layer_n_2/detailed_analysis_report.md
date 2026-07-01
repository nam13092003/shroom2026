# Detailed Hallucination Type Analysis

**Probe:** Qwen2.5-VL-7B/vision_token_layer_n_2
**Analysis Date:** 2025-10-05 20:18:12

---

## Overall Performance

**Test AUROC:** 0.6539

---

## Performance by Basic Hallucination Type

| Basic Hallucination Type | AUROC | Samples | Hallucination | No Hallucination |
|----------------------------------------|-------|---------|---------------|------------------|
| Object-Related | 0.8004 | 691 | 41 | 650 |
| Relationship | 0.7689 | 347 | 3 | 344 |
| Other | 0.5663 | 639 | 62 | 577 |
| Attribute-Related | 0.4964 | 323 | 15 | 308 |

---

## Performance by Domain Type

| Domain Type | AUROC | Samples | Hallucination | No Hallucination |
|----------------------------------------|-------|---------|---------------|------------------|
| General QA | 0.9318 | 46 | 2 | 44 |
| Spatial Reasoning | 0.7698 | 357 | 3 | 354 |
| Visual Understanding | 0.7564 | 572 | 46 | 526 |
| Math & Calculation | 0.6752 | 130 | 8 | 122 |
| Text & OCR | 0.6740 | 106 | 4 | 102 |
| Attribute Recognition | 0.5943 | 607 | 19 | 588 |
| Knowledge & Identity | 0.4680 | 139 | 29 | 110 |
| Temporal & Video | 0.3545 | 43 | 10 | 33 |

---

## Performance by Answer Type

| Answer Type | AUROC | Samples | Hallucination | No Hallucination |
|----------------------------------------|-------|---------|---------------|------------------|
| Yes/No | 0.6002 | 1330 | 121 | 1209 |
| Number | N/A | 118 | 0 | 118 |
| Open-Ended | N/A | 402 | 0 | 402 |
| Selection | N/A | 5 | 0 | 5 |
| Unanswerable | N/A | 145 | 0 | 145 |

---

