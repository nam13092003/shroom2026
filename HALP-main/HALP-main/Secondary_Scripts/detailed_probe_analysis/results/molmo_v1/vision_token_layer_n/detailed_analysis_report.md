# Detailed Hallucination Type Analysis

**Probe:** Molmo-V1/vision_token_layer_n
**Analysis Date:** 2025-10-05 20:17:19

---

## Overall Performance

**Test AUROC:** 0.6867

---

## Performance by Basic Hallucination Type

| Basic Hallucination Type | AUROC | Samples | Hallucination | No Hallucination |
|----------------------------------------|-------|---------|---------------|------------------|
| Other | 0.7463 | 616 | 94 | 522 |
| Object-Related | 0.7274 | 732 | 77 | 655 |
| Attribute-Related | 0.5686 | 313 | 43 | 270 |
| Relationship | 0.4767 | 339 | 27 | 312 |

---

## Performance by Domain Type

| Domain Type | AUROC | Samples | Hallucination | No Hallucination |
|----------------------------------------|-------|---------|---------------|------------------|
| General QA | 0.9477 | 54 | 3 | 51 |
| Attribute Recognition | 0.7210 | 598 | 50 | 548 |
| Visual Understanding | 0.7019 | 609 | 83 | 526 |
| Math & Calculation | 0.6942 | 124 | 19 | 105 |
| Text & OCR | 0.6380 | 121 | 11 | 110 |
| Knowledge & Identity | 0.4861 | 111 | 27 | 84 |
| Spatial Reasoning | 0.4855 | 348 | 27 | 321 |
| Temporal & Video | 0.4813 | 35 | 21 | 14 |

---

## Performance by Answer Type

| Answer Type | AUROC | Samples | Hallucination | No Hallucination |
|----------------------------------------|-------|---------|---------------|------------------|
| Yes/No | 0.5733 | 1311 | 241 | 1070 |
| Number | N/A | 110 | 0 | 110 |
| Open-Ended | N/A | 424 | 0 | 424 |
| Selection | N/A | 5 | 0 | 5 |
| Unanswerable | N/A | 150 | 0 | 150 |

---

