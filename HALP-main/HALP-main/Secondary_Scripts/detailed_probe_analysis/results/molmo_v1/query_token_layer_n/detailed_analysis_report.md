# Detailed Hallucination Type Analysis

**Probe:** Molmo-V1/query_token_layer_n
**Analysis Date:** 2025-10-05 20:16:52

---

## Overall Performance

**Test AUROC:** 0.9193

---

## Performance by Basic Hallucination Type

| Basic Hallucination Type | AUROC | Samples | Hallucination | No Hallucination |
|----------------------------------------|-------|---------|---------------|------------------|
| Object-Related | 0.9724 | 732 | 77 | 655 |
| Attribute-Related | 0.9553 | 313 | 43 | 270 |
| Other | 0.8565 | 616 | 94 | 522 |
| Relationship | 0.8088 | 339 | 27 | 312 |

---

## Performance by Domain Type

| Domain Type | AUROC | Samples | Hallucination | No Hallucination |
|----------------------------------------|-------|---------|---------------|------------------|
| Attribute Recognition | 0.9707 | 598 | 50 | 548 |
| Visual Understanding | 0.9668 | 609 | 83 | 526 |
| General QA | 0.9412 | 54 | 3 | 51 |
| Math & Calculation | 0.8341 | 124 | 19 | 105 |
| Text & OCR | 0.8248 | 121 | 11 | 110 |
| Spatial Reasoning | 0.8120 | 348 | 27 | 321 |
| Knowledge & Identity | 0.7989 | 111 | 27 | 84 |
| Temporal & Video | 0.5136 | 35 | 21 | 14 |

---

## Performance by Answer Type

| Answer Type | AUROC | Samples | Hallucination | No Hallucination |
|----------------------------------------|-------|---------|---------------|------------------|
| Yes/No | 0.8860 | 1311 | 241 | 1070 |
| Number | N/A | 110 | 0 | 110 |
| Open-Ended | N/A | 424 | 0 | 424 |
| Selection | N/A | 5 | 0 | 5 |
| Unanswerable | N/A | 150 | 0 | 150 |

---

