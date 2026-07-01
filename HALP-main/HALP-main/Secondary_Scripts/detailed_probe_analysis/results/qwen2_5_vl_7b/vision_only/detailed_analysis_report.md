# Detailed Hallucination Type Analysis

**Probe:** Qwen2.5-VL-7B/vision_only
**Analysis Date:** 2025-10-05 20:17:54

---

## Overall Performance

**Test AUROC:** 0.7873

---

## Performance by Basic Hallucination Type

| Basic Hallucination Type | AUROC | Samples | Hallucination | No Hallucination |
|----------------------------------------|-------|---------|---------------|------------------|
| Object-Related | 0.8329 | 691 | 41 | 650 |
| Other | 0.7676 | 639 | 62 | 577 |
| Relationship | 0.6478 | 347 | 3 | 344 |
| Attribute-Related | 0.6358 | 323 | 15 | 308 |

---

## Performance by Domain Type

| Domain Type | AUROC | Samples | Hallucination | No Hallucination |
|----------------------------------------|-------|---------|---------------|------------------|
| General QA | 1.0000 | 46 | 2 | 44 |
| Visual Understanding | 0.8248 | 572 | 46 | 526 |
| Math & Calculation | 0.7797 | 130 | 8 | 122 |
| Attribute Recognition | 0.7702 | 607 | 19 | 588 |
| Text & OCR | 0.7549 | 106 | 4 | 102 |
| Spatial Reasoning | 0.6474 | 357 | 3 | 354 |
| Knowledge & Identity | 0.5251 | 139 | 29 | 110 |
| Temporal & Video | 0.5121 | 43 | 10 | 33 |

---

## Performance by Answer Type

| Answer Type | AUROC | Samples | Hallucination | No Hallucination |
|----------------------------------------|-------|---------|---------------|------------------|
| Yes/No | 0.7131 | 1330 | 121 | 1209 |
| Number | N/A | 118 | 0 | 118 |
| Open-Ended | N/A | 402 | 0 | 402 |
| Selection | N/A | 5 | 0 | 5 |
| Unanswerable | N/A | 145 | 0 | 145 |

---

