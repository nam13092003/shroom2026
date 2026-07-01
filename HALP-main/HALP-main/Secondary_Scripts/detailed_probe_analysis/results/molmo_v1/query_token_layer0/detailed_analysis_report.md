# Detailed Hallucination Type Analysis

**Probe:** Molmo-V1/query_token_layer0
**Analysis Date:** 2025-10-05 20:16:42

---

## Overall Performance

**Test AUROC:** 0.7675

---

## Performance by Basic Hallucination Type

| Basic Hallucination Type | AUROC | Samples | Hallucination | No Hallucination |
|----------------------------------------|-------|---------|---------------|------------------|
| Other | 0.8431 | 616 | 94 | 522 |
| Object-Related | 0.7991 | 732 | 77 | 655 |
| Relationship | 0.5655 | 339 | 27 | 312 |
| Attribute-Related | 0.5427 | 313 | 43 | 270 |

---

## Performance by Domain Type

| Domain Type | AUROC | Samples | Hallucination | No Hallucination |
|----------------------------------------|-------|---------|---------------|------------------|
| General QA | 0.9477 | 54 | 3 | 51 |
| Text & OCR | 0.9190 | 121 | 11 | 110 |
| Math & Calculation | 0.8316 | 124 | 19 | 105 |
| Visual Understanding | 0.7556 | 609 | 83 | 526 |
| Attribute Recognition | 0.7442 | 598 | 50 | 548 |
| Spatial Reasoning | 0.5729 | 348 | 27 | 321 |
| Knowledge & Identity | 0.4268 | 111 | 27 | 84 |
| Temporal & Video | 0.4252 | 35 | 21 | 14 |

---

## Performance by Answer Type

| Answer Type | AUROC | Samples | Hallucination | No Hallucination |
|----------------------------------------|-------|---------|---------------|------------------|
| Yes/No | 0.6459 | 1311 | 241 | 1070 |
| Number | N/A | 110 | 0 | 110 |
| Open-Ended | N/A | 424 | 0 | 424 |
| Selection | N/A | 5 | 0 | 5 |
| Unanswerable | N/A | 150 | 0 | 150 |

---

