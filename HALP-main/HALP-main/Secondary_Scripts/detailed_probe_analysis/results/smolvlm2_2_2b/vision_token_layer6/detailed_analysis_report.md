# Detailed Hallucination Type Analysis

**Probe:** SmolVLM2-2.2B/vision_token_layer6
**Analysis Date:** 2025-10-05 20:18:59

---

## Overall Performance

**Test AUROC:** 0.6868

---

## Performance by Basic Hallucination Type

| Basic Hallucination Type | AUROC | Samples | Hallucination | No Hallucination |
|----------------------------------------|-------|---------|---------------|------------------|
| Other | 0.7785 | 621 | 63 | 558 |
| Object-Related | 0.6712 | 708 | 62 | 646 |
| Attribute-Related | 0.5530 | 354 | 69 | 285 |
| Relationship | 0.5084 | 317 | 4 | 313 |

---

## Performance by Domain Type

| Domain Type | AUROC | Samples | Hallucination | No Hallucination |
|----------------------------------------|-------|---------|---------------|------------------|
| General QA | 0.8854 | 50 | 2 | 48 |
| Math & Calculation | 0.8022 | 116 | 25 | 91 |
| Visual Understanding | 0.6727 | 611 | 69 | 542 |
| Attribute Recognition | 0.6678 | 628 | 71 | 557 |
| Text & OCR | 0.5286 | 110 | 9 | 101 |
| Knowledge & Identity | 0.5229 | 124 | 4 | 120 |
| Spatial Reasoning | 0.5172 | 331 | 4 | 327 |
| Temporal & Video | 0.2612 | 30 | 14 | 16 |

---

## Performance by Answer Type

| Answer Type | AUROC | Samples | Hallucination | No Hallucination |
|----------------------------------------|-------|---------|---------------|------------------|
| Yes/No | 0.6186 | 1314 | 198 | 1116 |
| Number | N/A | 127 | 0 | 127 |
| Open-Ended | N/A | 410 | 0 | 410 |
| Selection | N/A | 11 | 0 | 11 |
| Unanswerable | N/A | 138 | 0 | 138 |

---

