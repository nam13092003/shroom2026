# Detailed Hallucination Type Analysis

**Probe:** Gemma3-12B/vision_token_layer0
**Analysis Date:** 2025-10-05 20:14:37

---

## Overall Performance

**Test AUROC:** 0.6538

---

## Performance by Basic Hallucination Type

| Basic Hallucination Type | AUROC | Samples | Hallucination | No Hallucination |
|----------------------------------------|-------|---------|---------------|------------------|
| Other | 0.7213 | 632 | 71 | 561 |
| Object-Related | 0.6731 | 691 | 81 | 610 |
| Relationship | 0.5290 | 336 | 20 | 316 |
| Attribute-Related | 0.5269 | 341 | 40 | 301 |

---

## Performance by Domain Type

| Domain Type | AUROC | Samples | Hallucination | No Hallucination |
|----------------------------------------|-------|---------|---------------|------------------|
| Math & Calculation | 0.6938 | 118 | 12 | 106 |
| Visual Understanding | 0.6591 | 598 | 83 | 515 |
| Attribute Recognition | 0.6584 | 623 | 46 | 577 |
| Temporal & Video | 0.5915 | 35 | 17 | 18 |
| Knowledge & Identity | 0.5901 | 119 | 24 | 95 |
| Spatial Reasoning | 0.5373 | 348 | 20 | 328 |
| General QA | 0.5143 | 54 | 5 | 49 |
| Text & OCR | 0.4540 | 105 | 5 | 100 |

---

## Performance by Answer Type

| Answer Type | AUROC | Samples | Hallucination | No Hallucination |
|----------------------------------------|-------|---------|---------------|------------------|
| Yes/No | 0.5735 | 1317 | 212 | 1105 |
| Number | N/A | 132 | 0 | 132 |
| Open-Ended | N/A | 402 | 0 | 402 |
| Selection | N/A | 11 | 0 | 11 |
| Unanswerable | N/A | 138 | 0 | 138 |

---

