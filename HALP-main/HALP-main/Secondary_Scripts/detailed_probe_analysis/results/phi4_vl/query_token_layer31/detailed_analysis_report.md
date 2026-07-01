# Detailed Hallucination Type Analysis

**Probe:** Phi4-VL/query_token_layer31
**Analysis Date:** 2025-10-05 23:13:00

---

## Overall Performance

**Test AUROC:** 0.9033

---

## Performance by Basic Hallucination Type

| Type | AUROC | Samples | Hallucination | No Hallucination |
|------|-------|---------|---------------|------------------|
| Attribute-Related | 0.8974 | 325 | 30 | 295 |
| Object-Related | 0.9461 | 696 | 44 | 652 |
| Other | 0.8565 | 582 | 99 | 483 |
| Relationship | 0.8866 | 351 | 17 | 334 |

---

## Performance by Domain Type

| Type | AUROC | Samples | Hallucination | No Hallucination |
|------|-------|---------|---------------|------------------|
| Attribute Recognition | 0.9295 | 603 | 34 | 569 |
| General QA | 0.4730 | 39 | 2 | 37 |
| Knowledge & Identity | 0.7953 | 124 | 42 | 82 |
| Math & Calculation | 0.7861 | 124 | 23 | 101 |
| Spatial Reasoning | 0.8895 | 361 | 17 | 344 |
| Temporal & Video | 0.0500 | 24 | 14 | 10 |
| Text & OCR | 0.9382 | 95 | 6 | 89 |
| Visual Understanding | 0.9322 | 584 | 52 | 532 |

---

## Performance by Answer Type

| Type | AUROC | Samples | Hallucination | No Hallucination |
|------|-------|---------|---------------|------------------|
| Number | N/A | 131 | 0 | 131 |
| Open-Ended | N/A | 396 | 0 | 396 |
| Selection | N/A | 8 | 0 | 8 |
| Unanswerable | N/A | 137 | 0 | 137 |
| Yes/No | 0.8549 | 1282 | 190 | 1092 |

---

