# Detailed Hallucination Type Analysis

**Probe:** Molmo-V1/vision_token_layer_n_2
**Analysis Date:** 2025-10-05 20:17:24

---

## Overall Performance

**Test AUROC:** 0.6931

---

## Performance by Basic Hallucination Type

| Basic Hallucination Type | AUROC | Samples | Hallucination | No Hallucination |
|----------------------------------------|-------|---------|---------------|------------------|
| Other | 0.7740 | 616 | 94 | 522 |
| Object-Related | 0.7223 | 732 | 77 | 655 |
| Attribute-Related | 0.5418 | 313 | 43 | 270 |
| Relationship | 0.4774 | 339 | 27 | 312 |

---

## Performance by Domain Type

| Domain Type | AUROC | Samples | Hallucination | No Hallucination |
|----------------------------------------|-------|---------|---------------|------------------|
| General QA | 0.9085 | 54 | 3 | 51 |
| Math & Calculation | 0.7714 | 124 | 19 | 105 |
| Attribute Recognition | 0.7208 | 598 | 50 | 548 |
| Visual Understanding | 0.6889 | 609 | 83 | 526 |
| Text & OCR | 0.6769 | 121 | 11 | 110 |
| Temporal & Video | 0.4983 | 35 | 21 | 14 |
| Spatial Reasoning | 0.4844 | 348 | 27 | 321 |
| Knowledge & Identity | 0.4411 | 111 | 27 | 84 |

---

## Performance by Answer Type

| Answer Type | AUROC | Samples | Hallucination | No Hallucination |
|----------------------------------------|-------|---------|---------------|------------------|
| Yes/No | 0.5655 | 1311 | 241 | 1070 |
| Number | N/A | 110 | 0 | 110 |
| Open-Ended | N/A | 424 | 0 | 424 |
| Selection | N/A | 5 | 0 | 5 |
| Unanswerable | N/A | 150 | 0 | 150 |

---

