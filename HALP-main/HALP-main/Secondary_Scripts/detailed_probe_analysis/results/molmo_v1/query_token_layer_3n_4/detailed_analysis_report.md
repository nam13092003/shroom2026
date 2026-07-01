# Detailed Hallucination Type Analysis

**Probe:** Molmo-V1/query_token_layer_3n_4
**Analysis Date:** 2025-10-05 20:16:47

---

## Overall Performance

**Test AUROC:** 0.9345

---

## Performance by Basic Hallucination Type

| Basic Hallucination Type | AUROC | Samples | Hallucination | No Hallucination |
|----------------------------------------|-------|---------|---------------|------------------|
| Object-Related | 0.9799 | 732 | 77 | 655 |
| Attribute-Related | 0.9495 | 313 | 43 | 270 |
| Relationship | 0.8858 | 339 | 27 | 312 |
| Other | 0.8759 | 616 | 94 | 522 |

---

## Performance by Domain Type

| Domain Type | AUROC | Samples | Hallucination | No Hallucination |
|----------------------------------------|-------|---------|---------------|------------------|
| Visual Understanding | 0.9749 | 609 | 83 | 526 |
| General QA | 0.9673 | 54 | 3 | 51 |
| Attribute Recognition | 0.9666 | 598 | 50 | 548 |
| Text & OCR | 0.8950 | 121 | 11 | 110 |
| Spatial Reasoning | 0.8885 | 348 | 27 | 321 |
| Math & Calculation | 0.8617 | 124 | 19 | 105 |
| Knowledge & Identity | 0.8131 | 111 | 27 | 84 |
| Temporal & Video | 0.4388 | 35 | 21 | 14 |

---

## Performance by Answer Type

| Answer Type | AUROC | Samples | Hallucination | No Hallucination |
|----------------------------------------|-------|---------|---------------|------------------|
| Yes/No | 0.9048 | 1311 | 241 | 1070 |
| Number | N/A | 110 | 0 | 110 |
| Open-Ended | N/A | 424 | 0 | 424 |
| Selection | N/A | 5 | 0 | 5 |
| Unanswerable | N/A | 150 | 0 | 150 |

---

