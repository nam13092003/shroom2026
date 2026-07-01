# Detailed Hallucination Type Analysis

**Probe:** Llama-3.2-11B/vision_only
**Analysis Date:** 2025-10-05 23:25:05

---

## Overall Performance

**Test AUROC:** 0.7703

---

## Performance by Basic Hallucination Type

| Type | AUROC | Samples | Hallucination | No Hallucination |
|------|-------|---------|---------------|------------------|
| Attribute-Related | 0.5799 | 310 | 28 | 282 |
| Object-Related | 0.7972 | 677 | 42 | 635 |
| Other | 0.8209 | 638 | 95 | 543 |
| Relationship | 0.5884 | 329 | 21 | 308 |

---

## Performance by Domain Type

| Type | AUROC | Samples | Hallucination | No Hallucination |
|------|-------|---------|---------------|------------------|
| Attribute Recognition | 0.7662 | 582 | 32 | 550 |
| General QA | 0.6429 | 59 | 3 | 56 |
| Knowledge & Identity | 0.5784 | 129 | 27 | 102 |
| Math & Calculation | 0.8468 | 141 | 32 | 109 |
| Spatial Reasoning | 0.5867 | 343 | 21 | 322 |
| Temporal & Video | 0.4762 | 29 | 14 | 15 |
| Text & OCR | 0.8208 | 97 | 11 | 86 |
| Visual Understanding | 0.7729 | 574 | 46 | 528 |

---

## Performance by Answer Type

| Type | AUROC | Samples | Hallucination | No Hallucination |
|------|-------|---------|---------------|------------------|
| Number | N/A | 126 | 0 | 126 |
| Open-Ended | N/A | 408 | 0 | 408 |
| Selection | N/A | 6 | 0 | 6 |
| Unanswerable | N/A | 153 | 0 | 153 |
| Yes/No | 0.6730 | 1261 | 186 | 1075 |

---

