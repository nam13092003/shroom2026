# Detailed Hallucination Type Analysis

**Probe:** Phi4-VL/vision_token_layer24
**Analysis Date:** 2025-10-05 23:13:18

---

## Overall Performance

**Test AUROC:** 0.7662

---

## Performance by Basic Hallucination Type

| Type | AUROC | Samples | Hallucination | No Hallucination |
|------|-------|---------|---------------|------------------|
| Attribute-Related | 0.6281 | 325 | 30 | 295 |
| Object-Related | 0.7939 | 696 | 44 | 652 |
| Other | 0.8050 | 582 | 99 | 483 |
| Relationship | 0.4612 | 351 | 17 | 334 |

---

## Performance by Domain Type

| Type | AUROC | Samples | Hallucination | No Hallucination |
|------|-------|---------|---------------|------------------|
| Attribute Recognition | 0.7582 | 603 | 34 | 569 |
| General QA | 0.5676 | 39 | 2 | 37 |
| Knowledge & Identity | 0.5507 | 124 | 42 | 82 |
| Math & Calculation | 0.8422 | 124 | 23 | 101 |
| Spatial Reasoning | 0.4761 | 361 | 17 | 344 |
| Temporal & Video | 0.1643 | 24 | 14 | 10 |
| Text & OCR | 0.6798 | 95 | 6 | 89 |
| Visual Understanding | 0.7911 | 584 | 52 | 532 |

---

## Performance by Answer Type

| Type | AUROC | Samples | Hallucination | No Hallucination |
|------|-------|---------|---------------|------------------|
| Number | N/A | 131 | 0 | 131 |
| Open-Ended | N/A | 396 | 0 | 396 |
| Selection | N/A | 8 | 0 | 8 |
| Unanswerable | N/A | 137 | 0 | 137 |
| Yes/No | 0.6520 | 1282 | 190 | 1092 |

---

