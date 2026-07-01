# Detailed Hallucination Type Analysis

**Probe:** SmolVLM2-2.2B/vision_token_layer0
**Analysis Date:** 2025-10-05 20:18:43

---

## Overall Performance

**Test AUROC:** 0.6829

---

## Performance by Basic Hallucination Type

| Basic Hallucination Type | AUROC | Samples | Hallucination | No Hallucination |
|----------------------------------------|-------|---------|---------------|------------------|
| Other | 0.7931 | 621 | 63 | 558 |
| Object-Related | 0.6619 | 708 | 62 | 646 |
| Attribute-Related | 0.5480 | 354 | 69 | 285 |
| Relationship | 0.4764 | 317 | 4 | 313 |

---

## Performance by Domain Type

| Domain Type | AUROC | Samples | Hallucination | No Hallucination |
|----------------------------------------|-------|---------|---------------|------------------|
| General QA | 0.8646 | 50 | 2 | 48 |
| Math & Calculation | 0.8000 | 116 | 25 | 91 |
| Attribute Recognition | 0.6726 | 628 | 71 | 557 |
| Visual Understanding | 0.6623 | 611 | 69 | 542 |
| Knowledge & Identity | 0.5625 | 124 | 4 | 120 |
| Text & OCR | 0.5473 | 110 | 9 | 101 |
| Spatial Reasoning | 0.4790 | 331 | 4 | 327 |
| Temporal & Video | 0.3147 | 30 | 14 | 16 |

---

## Performance by Answer Type

| Answer Type | AUROC | Samples | Hallucination | No Hallucination |
|----------------------------------------|-------|---------|---------------|------------------|
| Yes/No | 0.6164 | 1314 | 198 | 1116 |
| Number | N/A | 127 | 0 | 127 |
| Open-Ended | N/A | 410 | 0 | 410 |
| Selection | N/A | 11 | 0 | 11 |
| Unanswerable | N/A | 138 | 0 | 138 |

---

