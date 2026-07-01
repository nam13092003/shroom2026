# Detailed Hallucination Type Analysis

**Probe:** Molmo-V1/vision_token_layer_n_4
**Analysis Date:** 2025-10-05 20:17:28

---

## Overall Performance

**Test AUROC:** 0.6982

---

## Performance by Basic Hallucination Type

| Basic Hallucination Type | AUROC | Samples | Hallucination | No Hallucination |
|----------------------------------------|-------|---------|---------------|------------------|
| Other | 0.7633 | 616 | 94 | 522 |
| Object-Related | 0.7347 | 732 | 77 | 655 |
| Attribute-Related | 0.5389 | 313 | 43 | 270 |
| Relationship | 0.5105 | 339 | 27 | 312 |

---

## Performance by Domain Type

| Domain Type | AUROC | Samples | Hallucination | No Hallucination |
|----------------------------------------|-------|---------|---------------|------------------|
| General QA | 0.8627 | 54 | 3 | 51 |
| Math & Calculation | 0.7529 | 124 | 19 | 105 |
| Attribute Recognition | 0.7253 | 598 | 50 | 548 |
| Visual Understanding | 0.6990 | 609 | 83 | 526 |
| Text & OCR | 0.6562 | 121 | 11 | 110 |
| Spatial Reasoning | 0.5187 | 348 | 27 | 321 |
| Temporal & Video | 0.4949 | 35 | 21 | 14 |
| Knowledge & Identity | 0.4085 | 111 | 27 | 84 |

---

## Performance by Answer Type

| Answer Type | AUROC | Samples | Hallucination | No Hallucination |
|----------------------------------------|-------|---------|---------------|------------------|
| Yes/No | 0.5698 | 1311 | 241 | 1070 |
| Number | N/A | 110 | 0 | 110 |
| Open-Ended | N/A | 424 | 0 | 424 |
| Selection | N/A | 5 | 0 | 5 |
| Unanswerable | N/A | 150 | 0 | 150 |

---

