# Detailed Hallucination Type Analysis

**Probe:** SmolVLM2-2.2B/vision_token_layer23
**Analysis Date:** 2025-10-05 20:18:55

---

## Overall Performance

**Test AUROC:** 0.6894

---

## Performance by Basic Hallucination Type

| Basic Hallucination Type | AUROC | Samples | Hallucination | No Hallucination |
|----------------------------------------|-------|---------|---------------|------------------|
| Other | 0.7826 | 621 | 63 | 558 |
| Object-Related | 0.6865 | 708 | 62 | 646 |
| Attribute-Related | 0.5553 | 354 | 69 | 285 |
| Relationship | 0.4141 | 317 | 4 | 313 |

---

## Performance by Domain Type

| Domain Type | AUROC | Samples | Hallucination | No Hallucination |
|----------------------------------------|-------|---------|---------------|------------------|
| General QA | 0.9688 | 50 | 2 | 48 |
| Math & Calculation | 0.8413 | 116 | 25 | 91 |
| Visual Understanding | 0.6931 | 611 | 69 | 542 |
| Attribute Recognition | 0.6601 | 628 | 71 | 557 |
| Text & OCR | 0.5319 | 110 | 9 | 101 |
| Spatial Reasoning | 0.4247 | 331 | 4 | 327 |
| Knowledge & Identity | 0.3562 | 124 | 4 | 120 |
| Temporal & Video | 0.2991 | 30 | 14 | 16 |

---

## Performance by Answer Type

| Answer Type | AUROC | Samples | Hallucination | No Hallucination |
|----------------------------------------|-------|---------|---------------|------------------|
| Yes/No | 0.6226 | 1314 | 198 | 1116 |
| Number | N/A | 127 | 0 | 127 |
| Open-Ended | N/A | 410 | 0 | 410 |
| Selection | N/A | 11 | 0 | 11 |
| Unanswerable | N/A | 138 | 0 | 138 |

---

