# Detailed Hallucination Type Analysis

**Probe:** SmolVLM2-2.2B/query_token_layer18
**Analysis Date:** 2025-10-05 20:18:28

---

## Overall Performance

**Test AUROC:** 0.9272

---

## Performance by Basic Hallucination Type

| Basic Hallucination Type | AUROC | Samples | Hallucination | No Hallucination |
|----------------------------------------|-------|---------|---------------|------------------|
| Object-Related | 0.9733 | 708 | 62 | 646 |
| Relationship | 0.9633 | 317 | 4 | 313 |
| Other | 0.9185 | 621 | 63 | 558 |
| Attribute-Related | 0.8068 | 354 | 69 | 285 |

---

## Performance by Domain Type

| Domain Type | AUROC | Samples | Hallucination | No Hallucination |
|----------------------------------------|-------|---------|---------------|------------------|
| Text & OCR | 0.9626 | 110 | 9 | 101 |
| Spatial Reasoning | 0.9610 | 331 | 4 | 327 |
| Visual Understanding | 0.9607 | 611 | 69 | 542 |
| General QA | 0.9271 | 50 | 2 | 48 |
| Math & Calculation | 0.9097 | 116 | 25 | 91 |
| Attribute Recognition | 0.8949 | 628 | 71 | 557 |
| Knowledge & Identity | 0.7063 | 124 | 4 | 120 |
| Temporal & Video | 0.3571 | 30 | 14 | 16 |

---

## Performance by Answer Type

| Answer Type | AUROC | Samples | Hallucination | No Hallucination |
|----------------------------------------|-------|---------|---------------|------------------|
| Yes/No | 0.8911 | 1314 | 198 | 1116 |
| Number | N/A | 127 | 0 | 127 |
| Open-Ended | N/A | 410 | 0 | 410 |
| Selection | N/A | 11 | 0 | 11 |
| Unanswerable | N/A | 138 | 0 | 138 |

---

