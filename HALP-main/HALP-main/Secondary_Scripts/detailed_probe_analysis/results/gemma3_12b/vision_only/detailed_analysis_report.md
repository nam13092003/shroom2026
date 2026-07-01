# Detailed Hallucination Type Analysis

**Probe:** Gemma3-12B/vision_only
**Analysis Date:** 2025-10-05 20:14:32

---

## Overall Performance

**Test AUROC:** 0.6736

---

## Performance by Basic Hallucination Type

| Basic Hallucination Type | AUROC | Samples | Hallucination | No Hallucination |
|----------------------------------------|-------|---------|---------------|------------------|
| Other | 0.7983 | 632 | 71 | 561 |
| Object-Related | 0.6758 | 691 | 81 | 610 |
| Relationship | 0.5339 | 336 | 20 | 316 |
| Attribute-Related | 0.4905 | 341 | 40 | 301 |

---

## Performance by Domain Type

| Domain Type | AUROC | Samples | Hallucination | No Hallucination |
|----------------------------------------|-------|---------|---------------|------------------|
| General QA | 0.7612 | 54 | 5 | 49 |
| Math & Calculation | 0.7402 | 118 | 12 | 106 |
| Text & OCR | 0.7340 | 105 | 5 | 100 |
| Attribute Recognition | 0.6548 | 623 | 46 | 577 |
| Visual Understanding | 0.6519 | 598 | 83 | 515 |
| Knowledge & Identity | 0.5846 | 119 | 24 | 95 |
| Spatial Reasoning | 0.5401 | 348 | 20 | 328 |
| Temporal & Video | 0.4510 | 35 | 17 | 18 |

---

## Performance by Answer Type

| Answer Type | AUROC | Samples | Hallucination | No Hallucination |
|----------------------------------------|-------|---------|---------------|------------------|
| Yes/No | 0.5677 | 1317 | 212 | 1105 |
| Number | N/A | 132 | 0 | 132 |
| Open-Ended | N/A | 402 | 0 | 402 |
| Selection | N/A | 11 | 0 | 11 |
| Unanswerable | N/A | 138 | 0 | 138 |

---

