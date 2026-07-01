# Detailed Hallucination Type Analysis

**Probe:** Phi4-VL/vision_token_layer0
**Analysis Date:** 2025-10-05 23:13:10

---

## Overall Performance

**Test AUROC:** 0.7689

---

## Performance by Basic Hallucination Type

| Type | AUROC | Samples | Hallucination | No Hallucination |
|------|-------|---------|---------------|------------------|
| Attribute-Related | 0.5733 | 325 | 30 | 295 |
| Object-Related | 0.7815 | 696 | 44 | 652 |
| Other | 0.8225 | 582 | 99 | 483 |
| Relationship | 0.5145 | 351 | 17 | 334 |

---

## Performance by Domain Type

| Type | AUROC | Samples | Hallucination | No Hallucination |
|------|-------|---------|---------------|------------------|
| Attribute Recognition | 0.6986 | 603 | 34 | 569 |
| General QA | 0.4595 | 39 | 2 | 37 |
| Knowledge & Identity | 0.6445 | 124 | 42 | 82 |
| Math & Calculation | 0.8216 | 124 | 23 | 101 |
| Spatial Reasoning | 0.5134 | 361 | 17 | 344 |
| Temporal & Video | 0.3786 | 24 | 14 | 10 |
| Text & OCR | 0.7715 | 95 | 6 | 89 |
| Visual Understanding | 0.7831 | 584 | 52 | 532 |

---

## Performance by Answer Type

| Type | AUROC | Samples | Hallucination | No Hallucination |
|------|-------|---------|---------------|------------------|
| Number | N/A | 131 | 0 | 131 |
| Open-Ended | N/A | 396 | 0 | 396 |
| Selection | N/A | 8 | 0 | 8 |
| Unanswerable | N/A | 137 | 0 | 137 |
| Yes/No | 0.6772 | 1282 | 190 | 1092 |

---

