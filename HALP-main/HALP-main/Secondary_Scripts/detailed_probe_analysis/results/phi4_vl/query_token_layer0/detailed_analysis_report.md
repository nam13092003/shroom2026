# Detailed Hallucination Type Analysis

**Probe:** Phi4-VL/query_token_layer0
**Analysis Date:** 2025-10-05 23:12:48

---

## Overall Performance

**Test AUROC:** 0.8629

---

## Performance by Basic Hallucination Type

| Type | AUROC | Samples | Hallucination | No Hallucination |
|------|-------|---------|---------------|------------------|
| Attribute-Related | 0.7267 | 325 | 30 | 295 |
| Object-Related | 0.8663 | 696 | 44 | 652 |
| Other | 0.8568 | 582 | 99 | 483 |
| Relationship | 0.7260 | 351 | 17 | 334 |

---

## Performance by Domain Type

| Type | AUROC | Samples | Hallucination | No Hallucination |
|------|-------|---------|---------------|------------------|
| Attribute Recognition | 0.8394 | 603 | 34 | 569 |
| General QA | 0.7432 | 39 | 2 | 37 |
| Knowledge & Identity | 0.6876 | 124 | 42 | 82 |
| Math & Calculation | 0.8377 | 124 | 23 | 101 |
| Spatial Reasoning | 0.7327 | 361 | 17 | 344 |
| Temporal & Video | 0.0714 | 24 | 14 | 10 |
| Text & OCR | 0.8652 | 95 | 6 | 89 |
| Visual Understanding | 0.8571 | 584 | 52 | 532 |

---

## Performance by Answer Type

| Type | AUROC | Samples | Hallucination | No Hallucination |
|------|-------|---------|---------------|------------------|
| Number | N/A | 131 | 0 | 131 |
| Open-Ended | N/A | 396 | 0 | 396 |
| Selection | N/A | 8 | 0 | 8 |
| Unanswerable | N/A | 137 | 0 | 137 |
| Yes/No | 0.7849 | 1282 | 190 | 1092 |

---

