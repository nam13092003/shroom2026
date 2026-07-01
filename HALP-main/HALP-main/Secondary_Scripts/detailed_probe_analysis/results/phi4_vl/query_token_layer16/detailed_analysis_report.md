# Detailed Hallucination Type Analysis

**Probe:** Phi4-VL/query_token_layer16
**Analysis Date:** 2025-10-05 23:12:52

---

## Overall Performance

**Test AUROC:** 0.9072

---

## Performance by Basic Hallucination Type

| Type | AUROC | Samples | Hallucination | No Hallucination |
|------|-------|---------|---------------|------------------|
| Attribute-Related | 0.8821 | 325 | 30 | 295 |
| Object-Related | 0.9382 | 696 | 44 | 652 |
| Other | 0.8761 | 582 | 99 | 483 |
| Relationship | 0.8617 | 351 | 17 | 334 |

---

## Performance by Domain Type

| Type | AUROC | Samples | Hallucination | No Hallucination |
|------|-------|---------|---------------|------------------|
| Attribute Recognition | 0.8924 | 603 | 34 | 569 |
| General QA | 0.5270 | 39 | 2 | 37 |
| Knowledge & Identity | 0.8621 | 124 | 42 | 82 |
| Math & Calculation | 0.7912 | 124 | 23 | 101 |
| Spatial Reasoning | 0.8653 | 361 | 17 | 344 |
| Temporal & Video | 0.1929 | 24 | 14 | 10 |
| Text & OCR | 0.9419 | 95 | 6 | 89 |
| Visual Understanding | 0.9333 | 584 | 52 | 532 |

---

## Performance by Answer Type

| Type | AUROC | Samples | Hallucination | No Hallucination |
|------|-------|---------|---------------|------------------|
| Number | N/A | 131 | 0 | 131 |
| Open-Ended | N/A | 396 | 0 | 396 |
| Selection | N/A | 8 | 0 | 8 |
| Unanswerable | N/A | 137 | 0 | 137 |
| Yes/No | 0.8626 | 1282 | 190 | 1092 |

---

