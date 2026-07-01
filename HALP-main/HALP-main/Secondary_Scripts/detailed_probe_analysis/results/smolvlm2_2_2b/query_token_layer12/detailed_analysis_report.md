# Detailed Hallucination Type Analysis

**Probe:** SmolVLM2-2.2B/query_token_layer12
**Analysis Date:** 2025-10-05 20:18:24

---

## Overall Performance

**Test AUROC:** 0.9055

---

## Performance by Basic Hallucination Type

| Basic Hallucination Type | AUROC | Samples | Hallucination | No Hallucination |
|----------------------------------------|-------|---------|---------------|------------------|
| Relationship | 0.9473 | 317 | 4 | 313 |
| Object-Related | 0.9430 | 708 | 62 | 646 |
| Other | 0.8927 | 621 | 63 | 558 |
| Attribute-Related | 0.7854 | 354 | 69 | 285 |

---

## Performance by Domain Type

| Domain Type | AUROC | Samples | Hallucination | No Hallucination |
|----------------------------------------|-------|---------|---------------|------------------|
| Knowledge & Identity | 0.9667 | 124 | 4 | 120 |
| Spatial Reasoning | 0.9465 | 331 | 4 | 327 |
| Text & OCR | 0.9450 | 110 | 9 | 101 |
| Visual Understanding | 0.9046 | 611 | 69 | 542 |
| Math & Calculation | 0.8815 | 116 | 25 | 91 |
| Attribute Recognition | 0.8768 | 628 | 71 | 557 |
| General QA | 0.8750 | 50 | 2 | 48 |
| Temporal & Video | 0.4018 | 30 | 14 | 16 |

---

## Performance by Answer Type

| Answer Type | AUROC | Samples | Hallucination | No Hallucination |
|----------------------------------------|-------|---------|---------------|------------------|
| Yes/No | 0.8621 | 1314 | 198 | 1116 |
| Number | N/A | 127 | 0 | 127 |
| Open-Ended | N/A | 410 | 0 | 410 |
| Selection | N/A | 11 | 0 | 11 |
| Unanswerable | N/A | 138 | 0 | 138 |

---

