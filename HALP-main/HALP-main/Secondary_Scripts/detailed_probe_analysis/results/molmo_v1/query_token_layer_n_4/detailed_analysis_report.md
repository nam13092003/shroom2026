# Detailed Hallucination Type Analysis

**Probe:** Molmo-V1/query_token_layer_n_4
**Analysis Date:** 2025-10-05 20:17:01

---

## Overall Performance

**Test AUROC:** 0.8588

---

## Performance by Basic Hallucination Type

| Basic Hallucination Type | AUROC | Samples | Hallucination | No Hallucination |
|----------------------------------------|-------|---------|---------------|------------------|
| Object-Related | 0.9006 | 732 | 77 | 655 |
| Other | 0.8464 | 616 | 94 | 522 |
| Attribute-Related | 0.8108 | 313 | 43 | 270 |
| Relationship | 0.7600 | 339 | 27 | 312 |

---

## Performance by Domain Type

| Domain Type | AUROC | Samples | Hallucination | No Hallucination |
|----------------------------------------|-------|---------|---------------|------------------|
| General QA | 0.9673 | 54 | 3 | 51 |
| Text & OCR | 0.9041 | 121 | 11 | 110 |
| Attribute Recognition | 0.8962 | 598 | 50 | 548 |
| Visual Understanding | 0.8740 | 609 | 83 | 526 |
| Math & Calculation | 0.7850 | 124 | 19 | 105 |
| Spatial Reasoning | 0.7658 | 348 | 27 | 321 |
| Knowledge & Identity | 0.5238 | 111 | 27 | 84 |
| Temporal & Video | 0.4626 | 35 | 21 | 14 |

---

## Performance by Answer Type

| Answer Type | AUROC | Samples | Hallucination | No Hallucination |
|----------------------------------------|-------|---------|---------------|------------------|
| Yes/No | 0.7758 | 1311 | 241 | 1070 |
| Number | N/A | 110 | 0 | 110 |
| Open-Ended | N/A | 424 | 0 | 424 |
| Selection | N/A | 5 | 0 | 5 |
| Unanswerable | N/A | 150 | 0 | 150 |

---

