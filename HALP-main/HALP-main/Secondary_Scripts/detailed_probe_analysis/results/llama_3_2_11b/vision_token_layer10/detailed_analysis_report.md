# Detailed Hallucination Type Analysis

**Probe:** Llama-3.2-11B/vision_token_layer10
**Analysis Date:** 2025-10-05 23:25:13

---

## Overall Performance

**Test AUROC:** 0.7463

---

## Performance by Basic Hallucination Type

| Type | AUROC | Samples | Hallucination | No Hallucination |
|------|-------|---------|---------------|------------------|
| Attribute-Related | 0.5774 | 310 | 28 | 282 |
| Object-Related | 0.7840 | 677 | 42 | 635 |
| Other | 0.7894 | 638 | 95 | 543 |
| Relationship | 0.5848 | 329 | 21 | 308 |

---

## Performance by Domain Type

| Type | AUROC | Samples | Hallucination | No Hallucination |
|------|-------|---------|---------------|------------------|
| Attribute Recognition | 0.7504 | 582 | 32 | 550 |
| General QA | 0.7738 | 59 | 3 | 56 |
| Knowledge & Identity | 0.4789 | 129 | 27 | 102 |
| Math & Calculation | 0.8370 | 141 | 32 | 109 |
| Spatial Reasoning | 0.5900 | 343 | 21 | 322 |
| Temporal & Video | 0.4667 | 29 | 14 | 15 |
| Text & OCR | 0.8314 | 97 | 11 | 86 |
| Visual Understanding | 0.7595 | 574 | 46 | 528 |

---

## Performance by Answer Type

| Type | AUROC | Samples | Hallucination | No Hallucination |
|------|-------|---------|---------------|------------------|
| Number | N/A | 126 | 0 | 126 |
| Open-Ended | N/A | 408 | 0 | 408 |
| Selection | N/A | 6 | 0 | 6 |
| Unanswerable | N/A | 153 | 0 | 153 |
| Yes/No | 0.6426 | 1261 | 186 | 1075 |

---

