# Detailed Hallucination Type Analysis

**Probe:** Qwen2.5-VL-7B/vision_token_layer_n_4
**Analysis Date:** 2025-10-05 20:18:16

---

## Overall Performance

**Test AUROC:** 0.6593

---

## Performance by Basic Hallucination Type

| Basic Hallucination Type | AUROC | Samples | Hallucination | No Hallucination |
|----------------------------------------|-------|---------|---------------|------------------|
| Object-Related | 0.8529 | 691 | 41 | 650 |
| Other | 0.6154 | 639 | 62 | 577 |
| Attribute-Related | 0.3698 | 323 | 15 | 308 |
| Relationship | 0.2534 | 347 | 3 | 344 |

---

## Performance by Domain Type

| Domain Type | AUROC | Samples | Hallucination | No Hallucination |
|----------------------------------------|-------|---------|---------------|------------------|
| Visual Understanding | 0.8157 | 572 | 46 | 526 |
| General QA | 0.7841 | 46 | 2 | 44 |
| Math & Calculation | 0.6691 | 130 | 8 | 122 |
| Knowledge & Identity | 0.5614 | 139 | 29 | 110 |
| Attribute Recognition | 0.4794 | 607 | 19 | 588 |
| Text & OCR | 0.4559 | 106 | 4 | 102 |
| Temporal & Video | 0.4333 | 43 | 10 | 33 |
| Spatial Reasoning | 0.2509 | 357 | 3 | 354 |

---

## Performance by Answer Type

| Answer Type | AUROC | Samples | Hallucination | No Hallucination |
|----------------------------------------|-------|---------|---------------|------------------|
| Yes/No | 0.6161 | 1330 | 121 | 1209 |
| Number | N/A | 118 | 0 | 118 |
| Open-Ended | N/A | 402 | 0 | 402 |
| Selection | N/A | 5 | 0 | 5 |
| Unanswerable | N/A | 145 | 0 | 145 |

---

