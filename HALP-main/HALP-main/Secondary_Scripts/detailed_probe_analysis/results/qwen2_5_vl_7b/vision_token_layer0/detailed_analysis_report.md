# Detailed Hallucination Type Analysis

**Probe:** Qwen2.5-VL-7B/vision_token_layer0
**Analysis Date:** 2025-10-05 20:17:58

---

## Overall Performance

**Test AUROC:** 0.6543

---

## Performance by Basic Hallucination Type

| Basic Hallucination Type | AUROC | Samples | Hallucination | No Hallucination |
|----------------------------------------|-------|---------|---------------|------------------|
| Object-Related | 0.8492 | 691 | 41 | 650 |
| Relationship | 0.6391 | 347 | 3 | 344 |
| Other | 0.5468 | 639 | 62 | 577 |
| Attribute-Related | 0.4966 | 323 | 15 | 308 |

---

## Performance by Domain Type

| Domain Type | AUROC | Samples | Hallucination | No Hallucination |
|----------------------------------------|-------|---------|---------------|------------------|
| General QA | 0.9659 | 46 | 2 | 44 |
| Visual Understanding | 0.8098 | 572 | 46 | 526 |
| Spatial Reasoning | 0.6332 | 357 | 3 | 354 |
| Math & Calculation | 0.6035 | 130 | 8 | 122 |
| Attribute Recognition | 0.5819 | 607 | 19 | 588 |
| Temporal & Video | 0.4848 | 43 | 10 | 33 |
| Knowledge & Identity | 0.4204 | 139 | 29 | 110 |
| Text & OCR | 0.3627 | 106 | 4 | 102 |

---

## Performance by Answer Type

| Answer Type | AUROC | Samples | Hallucination | No Hallucination |
|----------------------------------------|-------|---------|---------------|------------------|
| Yes/No | 0.6097 | 1330 | 121 | 1209 |
| Number | N/A | 118 | 0 | 118 |
| Open-Ended | N/A | 402 | 0 | 402 |
| Selection | N/A | 5 | 0 | 5 |
| Unanswerable | N/A | 145 | 0 | 145 |

---

