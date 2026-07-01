# Detailed Hallucination Type Analysis

**Probe:** Gemma3-12B/vision_token_layer_n
**Analysis Date:** 2025-10-05 20:14:46

---

## Overall Performance

**Test AUROC:** 0.5956

---

## Performance by Basic Hallucination Type

| Basic Hallucination Type | AUROC | Samples | Hallucination | No Hallucination |
|----------------------------------------|-------|---------|---------------|------------------|
| Object-Related | 0.6418 | 691 | 81 | 610 |
| Other | 0.6380 | 632 | 71 | 561 |
| Attribute-Related | 0.4811 | 341 | 40 | 301 |
| Relationship | 0.4636 | 336 | 20 | 316 |

---

## Performance by Domain Type

| Domain Type | AUROC | Samples | Hallucination | No Hallucination |
|----------------------------------------|-------|---------|---------------|------------------|
| Visual Understanding | 0.6431 | 598 | 83 | 515 |
| Knowledge & Identity | 0.6366 | 119 | 24 | 95 |
| Math & Calculation | 0.6018 | 118 | 12 | 106 |
| Attribute Recognition | 0.5246 | 623 | 46 | 577 |
| Spatial Reasoning | 0.4655 | 348 | 20 | 328 |
| General QA | 0.4061 | 54 | 5 | 49 |
| Temporal & Video | 0.3954 | 35 | 17 | 18 |
| Text & OCR | 0.3900 | 105 | 5 | 100 |

---

## Performance by Answer Type

| Answer Type | AUROC | Samples | Hallucination | No Hallucination |
|----------------------------------------|-------|---------|---------------|------------------|
| Yes/No | 0.5584 | 1317 | 212 | 1105 |
| Number | N/A | 132 | 0 | 132 |
| Open-Ended | N/A | 402 | 0 | 402 |
| Selection | N/A | 11 | 0 | 11 |
| Unanswerable | N/A | 138 | 0 | 138 |

---

