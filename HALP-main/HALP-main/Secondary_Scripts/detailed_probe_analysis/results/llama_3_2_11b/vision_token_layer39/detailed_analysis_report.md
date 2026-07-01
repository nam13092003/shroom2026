# Detailed Hallucination Type Analysis

**Probe:** Llama-3.2-11B/vision_token_layer39
**Analysis Date:** 2025-10-05 23:25:26

---

## Overall Performance

**Test AUROC:** 0.7377

---

## Performance by Basic Hallucination Type

| Type | AUROC | Samples | Hallucination | No Hallucination |
|------|-------|---------|---------------|------------------|
| Attribute-Related | 0.5456 | 310 | 28 | 282 |
| Object-Related | 0.7238 | 677 | 42 | 635 |
| Other | 0.8038 | 638 | 95 | 543 |
| Relationship | 0.6341 | 329 | 21 | 308 |

---

## Performance by Domain Type

| Type | AUROC | Samples | Hallucination | No Hallucination |
|------|-------|---------|---------------|------------------|
| Attribute Recognition | 0.7169 | 582 | 32 | 550 |
| General QA | 0.7440 | 59 | 3 | 56 |
| Knowledge & Identity | 0.5759 | 129 | 27 | 102 |
| Math & Calculation | 0.8175 | 141 | 32 | 109 |
| Spatial Reasoning | 0.6447 | 343 | 21 | 322 |
| Temporal & Video | 0.4857 | 29 | 14 | 15 |
| Text & OCR | 0.8430 | 97 | 11 | 86 |
| Visual Understanding | 0.7051 | 574 | 46 | 528 |

---

## Performance by Answer Type

| Type | AUROC | Samples | Hallucination | No Hallucination |
|------|-------|---------|---------------|------------------|
| Number | N/A | 126 | 0 | 126 |
| Open-Ended | N/A | 408 | 0 | 408 |
| Selection | N/A | 6 | 0 | 6 |
| Unanswerable | N/A | 153 | 0 | 153 |
| Yes/No | 0.6482 | 1261 | 186 | 1075 |

---

