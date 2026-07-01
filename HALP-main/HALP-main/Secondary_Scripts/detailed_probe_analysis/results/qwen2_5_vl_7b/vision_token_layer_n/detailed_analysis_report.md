# Detailed Hallucination Type Analysis

**Probe:** Qwen2.5-VL-7B/vision_token_layer_n
**Analysis Date:** 2025-10-05 20:18:07

---

## Overall Performance

**Test AUROC:** 0.6683

---

## Performance by Basic Hallucination Type

| Basic Hallucination Type | AUROC | Samples | Hallucination | No Hallucination |
|----------------------------------------|-------|---------|---------------|------------------|
| Object-Related | 0.8033 | 691 | 41 | 650 |
| Relationship | 0.7786 | 347 | 3 | 344 |
| Other | 0.5903 | 639 | 62 | 577 |
| Attribute-Related | 0.5083 | 323 | 15 | 308 |

---

## Performance by Domain Type

| Domain Type | AUROC | Samples | Hallucination | No Hallucination |
|----------------------------------------|-------|---------|---------------|------------------|
| General QA | 0.9545 | 46 | 2 | 44 |
| Spatial Reasoning | 0.7792 | 357 | 3 | 354 |
| Visual Understanding | 0.7607 | 572 | 46 | 526 |
| Math & Calculation | 0.6557 | 130 | 8 | 122 |
| Attribute Recognition | 0.5883 | 607 | 19 | 588 |
| Knowledge & Identity | 0.5494 | 139 | 29 | 110 |
| Text & OCR | 0.5245 | 106 | 4 | 102 |
| Temporal & Video | 0.3212 | 43 | 10 | 33 |

---

## Performance by Answer Type

| Answer Type | AUROC | Samples | Hallucination | No Hallucination |
|----------------------------------------|-------|---------|---------------|------------------|
| Yes/No | 0.6344 | 1330 | 121 | 1209 |
| Number | N/A | 118 | 0 | 118 |
| Open-Ended | N/A | 402 | 0 | 402 |
| Selection | N/A | 5 | 0 | 5 |
| Unanswerable | N/A | 145 | 0 | 145 |

---

