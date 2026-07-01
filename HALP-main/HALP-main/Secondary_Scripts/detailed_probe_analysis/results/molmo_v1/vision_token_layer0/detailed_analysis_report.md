# Detailed Hallucination Type Analysis

**Probe:** Molmo-V1/vision_token_layer0
**Analysis Date:** 2025-10-05 20:17:10

---

## Overall Performance

**Test AUROC:** 0.6936

---

## Performance by Basic Hallucination Type

| Basic Hallucination Type | AUROC | Samples | Hallucination | No Hallucination |
|----------------------------------------|-------|---------|---------------|------------------|
| Other | 0.7832 | 616 | 94 | 522 |
| Object-Related | 0.7183 | 732 | 77 | 655 |
| Attribute-Related | 0.5451 | 313 | 43 | 270 |
| Relationship | 0.5226 | 339 | 27 | 312 |

---

## Performance by Domain Type

| Domain Type | AUROC | Samples | Hallucination | No Hallucination |
|----------------------------------------|-------|---------|---------------|------------------|
| General QA | 0.9020 | 54 | 3 | 51 |
| Text & OCR | 0.8083 | 121 | 11 | 110 |
| Math & Calculation | 0.7629 | 124 | 19 | 105 |
| Attribute Recognition | 0.7181 | 598 | 50 | 548 |
| Visual Understanding | 0.6900 | 609 | 83 | 526 |
| Spatial Reasoning | 0.5336 | 348 | 27 | 321 |
| Temporal & Video | 0.4983 | 35 | 21 | 14 |
| Knowledge & Identity | 0.4438 | 111 | 27 | 84 |

---

## Performance by Answer Type

| Answer Type | AUROC | Samples | Hallucination | No Hallucination |
|----------------------------------------|-------|---------|---------------|------------------|
| Yes/No | 0.5652 | 1311 | 241 | 1070 |
| Number | N/A | 110 | 0 | 110 |
| Open-Ended | N/A | 424 | 0 | 424 |
| Selection | N/A | 5 | 0 | 5 |
| Unanswerable | N/A | 150 | 0 | 150 |

---

