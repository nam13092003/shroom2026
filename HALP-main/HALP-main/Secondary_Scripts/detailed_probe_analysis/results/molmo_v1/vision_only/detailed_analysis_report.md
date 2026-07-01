# Detailed Hallucination Type Analysis

**Probe:** Molmo-V1/vision_only
**Analysis Date:** 2025-10-05 20:17:05

---

## Overall Performance

**Test AUROC:** 0.6830

---

## Performance by Basic Hallucination Type

| Basic Hallucination Type | AUROC | Samples | Hallucination | No Hallucination |
|----------------------------------------|-------|---------|---------------|------------------|
| Other | 0.7683 | 616 | 94 | 522 |
| Object-Related | 0.6861 | 732 | 77 | 655 |
| Attribute-Related | 0.5399 | 313 | 43 | 270 |
| Relationship | 0.5177 | 339 | 27 | 312 |

---

## Performance by Domain Type

| Domain Type | AUROC | Samples | Hallucination | No Hallucination |
|----------------------------------------|-------|---------|---------------|------------------|
| General QA | 0.9085 | 54 | 3 | 51 |
| Attribute Recognition | 0.7200 | 598 | 50 | 548 |
| Text & OCR | 0.7033 | 121 | 11 | 110 |
| Math & Calculation | 0.6897 | 124 | 19 | 105 |
| Visual Understanding | 0.6725 | 609 | 83 | 526 |
| Temporal & Video | 0.5510 | 35 | 21 | 14 |
| Spatial Reasoning | 0.5276 | 348 | 27 | 321 |
| Knowledge & Identity | 0.4993 | 111 | 27 | 84 |

---

## Performance by Answer Type

| Answer Type | AUROC | Samples | Hallucination | No Hallucination |
|----------------------------------------|-------|---------|---------------|------------------|
| Yes/No | 0.5661 | 1311 | 241 | 1070 |
| Number | N/A | 110 | 0 | 110 |
| Open-Ended | N/A | 424 | 0 | 424 |
| Selection | N/A | 5 | 0 | 5 |
| Unanswerable | N/A | 150 | 0 | 150 |

---

