# Detailed Hallucination Type Analysis

**Probe:** Phi4-VL/query_token_layer8
**Analysis Date:** 2025-10-05 23:13:04

---

## Overall Performance

**Test AUROC:** 0.8638

---

## Performance by Basic Hallucination Type

| Type | AUROC | Samples | Hallucination | No Hallucination |
|------|-------|---------|---------------|------------------|
| Attribute-Related | 0.7977 | 325 | 30 | 295 |
| Object-Related | 0.8994 | 696 | 44 | 652 |
| Other | 0.8634 | 582 | 99 | 483 |
| Relationship | 0.7485 | 351 | 17 | 334 |

---

## Performance by Domain Type

| Type | AUROC | Samples | Hallucination | No Hallucination |
|------|-------|---------|---------------|------------------|
| Attribute Recognition | 0.8451 | 603 | 34 | 569 |
| General QA | 0.7162 | 39 | 2 | 37 |
| Knowledge & Identity | 0.7056 | 124 | 42 | 82 |
| Math & Calculation | 0.8455 | 124 | 23 | 101 |
| Spatial Reasoning | 0.7519 | 361 | 17 | 344 |
| Temporal & Video | 0.0929 | 24 | 14 | 10 |
| Text & OCR | 0.8933 | 95 | 6 | 89 |
| Visual Understanding | 0.8767 | 584 | 52 | 532 |

---

## Performance by Answer Type

| Type | AUROC | Samples | Hallucination | No Hallucination |
|------|-------|---------|---------------|------------------|
| Number | N/A | 131 | 0 | 131 |
| Open-Ended | N/A | 396 | 0 | 396 |
| Selection | N/A | 8 | 0 | 8 |
| Unanswerable | N/A | 137 | 0 | 137 |
| Yes/No | 0.7969 | 1282 | 190 | 1092 |

---

