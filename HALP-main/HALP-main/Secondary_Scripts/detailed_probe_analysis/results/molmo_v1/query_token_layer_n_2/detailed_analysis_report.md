# Detailed Hallucination Type Analysis

**Probe:** Molmo-V1/query_token_layer_n_2
**Analysis Date:** 2025-10-05 20:16:56

---

## Overall Performance

**Test AUROC:** 0.9365

---

## Performance by Basic Hallucination Type

| Basic Hallucination Type | AUROC | Samples | Hallucination | No Hallucination |
|----------------------------------------|-------|---------|---------------|------------------|
| Object-Related | 0.9807 | 732 | 77 | 655 |
| Attribute-Related | 0.9534 | 313 | 43 | 270 |
| Other | 0.8943 | 616 | 94 | 522 |
| Relationship | 0.8305 | 339 | 27 | 312 |

---

## Performance by Domain Type

| Domain Type | AUROC | Samples | Hallucination | No Hallucination |
|----------------------------------------|-------|---------|---------------|------------------|
| Visual Understanding | 0.9732 | 609 | 83 | 526 |
| Attribute Recognition | 0.9687 | 598 | 50 | 548 |
| General QA | 0.9542 | 54 | 3 | 51 |
| Text & OCR | 0.9231 | 121 | 11 | 110 |
| Knowledge & Identity | 0.8642 | 111 | 27 | 84 |
| Spatial Reasoning | 0.8328 | 348 | 27 | 321 |
| Math & Calculation | 0.8070 | 124 | 19 | 105 |
| Temporal & Video | 0.5136 | 35 | 21 | 14 |

---

## Performance by Answer Type

| Answer Type | AUROC | Samples | Hallucination | No Hallucination |
|----------------------------------------|-------|---------|---------------|------------------|
| Yes/No | 0.9055 | 1311 | 241 | 1070 |
| Number | N/A | 110 | 0 | 110 |
| Open-Ended | N/A | 424 | 0 | 424 |
| Selection | N/A | 5 | 0 | 5 |
| Unanswerable | N/A | 150 | 0 | 150 |

---

