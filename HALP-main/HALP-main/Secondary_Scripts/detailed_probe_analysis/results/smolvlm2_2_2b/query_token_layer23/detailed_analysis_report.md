# Detailed Hallucination Type Analysis

**Probe:** SmolVLM2-2.2B/query_token_layer23
**Analysis Date:** 2025-10-05 20:18:32

---

## Overall Performance

**Test AUROC:** 0.9014

---

## Performance by Basic Hallucination Type

| Basic Hallucination Type | AUROC | Samples | Hallucination | No Hallucination |
|----------------------------------------|-------|---------|---------------|------------------|
| Object-Related | 0.9527 | 708 | 62 | 646 |
| Other | 0.8975 | 621 | 63 | 558 |
| Relationship | 0.8922 | 317 | 4 | 313 |
| Attribute-Related | 0.8332 | 354 | 69 | 285 |

---

## Performance by Domain Type

| Domain Type | AUROC | Samples | Hallucination | No Hallucination |
|----------------------------------------|-------|---------|---------------|------------------|
| Text & OCR | 0.9450 | 110 | 9 | 101 |
| Visual Understanding | 0.9407 | 611 | 69 | 542 |
| Spatial Reasoning | 0.8960 | 331 | 4 | 327 |
| Attribute Recognition | 0.8906 | 628 | 71 | 557 |
| General QA | 0.8750 | 50 | 2 | 48 |
| Math & Calculation | 0.8565 | 116 | 25 | 91 |
| Knowledge & Identity | 0.7854 | 124 | 4 | 120 |
| Temporal & Video | 0.3571 | 30 | 14 | 16 |

---

## Performance by Answer Type

| Answer Type | AUROC | Samples | Hallucination | No Hallucination |
|----------------------------------------|-------|---------|---------------|------------------|
| Yes/No | 0.8646 | 1314 | 198 | 1116 |
| Number | N/A | 127 | 0 | 127 |
| Open-Ended | N/A | 410 | 0 | 410 |
| Selection | N/A | 11 | 0 | 11 |
| Unanswerable | N/A | 138 | 0 | 138 |

---

