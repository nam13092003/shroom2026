# Detailed Hallucination Type Analysis

**Probe:** SmolVLM2-2.2B/vision_token_layer18
**Analysis Date:** 2025-10-05 20:18:51

---

## Overall Performance

**Test AUROC:** 0.6801

---

## Performance by Basic Hallucination Type

| Basic Hallucination Type | AUROC | Samples | Hallucination | No Hallucination |
|----------------------------------------|-------|---------|---------------|------------------|
| Other | 0.7905 | 621 | 63 | 558 |
| Object-Related | 0.6703 | 708 | 62 | 646 |
| Relationship | 0.5587 | 317 | 4 | 313 |
| Attribute-Related | 0.5350 | 354 | 69 | 285 |

---

## Performance by Domain Type

| Domain Type | AUROC | Samples | Hallucination | No Hallucination |
|----------------------------------------|-------|---------|---------------|------------------|
| General QA | 0.9167 | 50 | 2 | 48 |
| Math & Calculation | 0.8013 | 116 | 25 | 91 |
| Text & OCR | 0.7068 | 110 | 9 | 101 |
| Visual Understanding | 0.6592 | 611 | 69 | 542 |
| Attribute Recognition | 0.6511 | 628 | 71 | 557 |
| Spatial Reasoning | 0.5593 | 331 | 4 | 327 |
| Knowledge & Identity | 0.4958 | 124 | 4 | 120 |
| Temporal & Video | 0.1786 | 30 | 14 | 16 |

---

## Performance by Answer Type

| Answer Type | AUROC | Samples | Hallucination | No Hallucination |
|----------------------------------------|-------|---------|---------------|------------------|
| Yes/No | 0.6101 | 1314 | 198 | 1116 |
| Number | N/A | 127 | 0 | 127 |
| Open-Ended | N/A | 410 | 0 | 410 |
| Selection | N/A | 11 | 0 | 11 |
| Unanswerable | N/A | 138 | 0 | 138 |

---

