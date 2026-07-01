# Detailed Hallucination Type Analysis

**Probe:** Molmo-V1/vision_token_layer_3n_4
**Analysis Date:** 2025-10-05 20:17:14

---

## Overall Performance

**Test AUROC:** 0.6862

---

## Performance by Basic Hallucination Type

| Basic Hallucination Type | AUROC | Samples | Hallucination | No Hallucination |
|----------------------------------------|-------|---------|---------------|------------------|
| Other | 0.7574 | 616 | 94 | 522 |
| Object-Related | 0.7202 | 732 | 77 | 655 |
| Attribute-Related | 0.5257 | 313 | 43 | 270 |
| Relationship | 0.4863 | 339 | 27 | 312 |

---

## Performance by Domain Type

| Domain Type | AUROC | Samples | Hallucination | No Hallucination |
|----------------------------------------|-------|---------|---------------|------------------|
| General QA | 0.9020 | 54 | 3 | 51 |
| Math & Calculation | 0.7288 | 124 | 19 | 105 |
| Attribute Recognition | 0.7104 | 598 | 50 | 548 |
| Visual Understanding | 0.6951 | 609 | 83 | 526 |
| Text & OCR | 0.6926 | 121 | 11 | 110 |
| Temporal & Video | 0.5119 | 35 | 21 | 14 |
| Spatial Reasoning | 0.4949 | 348 | 27 | 321 |
| Knowledge & Identity | 0.4641 | 111 | 27 | 84 |

---

## Performance by Answer Type

| Answer Type | AUROC | Samples | Hallucination | No Hallucination |
|----------------------------------------|-------|---------|---------------|------------------|
| Yes/No | 0.5619 | 1311 | 241 | 1070 |
| Number | N/A | 110 | 0 | 110 |
| Open-Ended | N/A | 424 | 0 | 424 |
| Selection | N/A | 5 | 0 | 5 |
| Unanswerable | N/A | 150 | 0 | 150 |

---

