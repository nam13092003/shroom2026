# Detailed Hallucination Type Analysis

**Probe:** SmolVLM2-2.2B/vision_only
**Analysis Date:** 2025-10-05 20:18:39

---

## Overall Performance

**Test AUROC:** 0.7238

---

## Performance by Basic Hallucination Type

| Basic Hallucination Type | AUROC | Samples | Hallucination | No Hallucination |
|----------------------------------------|-------|---------|---------------|------------------|
| Other | 0.8221 | 621 | 63 | 558 |
| Object-Related | 0.7364 | 708 | 62 | 646 |
| Relationship | 0.6721 | 317 | 4 | 313 |
| Attribute-Related | 0.5621 | 354 | 69 | 285 |

---

## Performance by Domain Type

| Domain Type | AUROC | Samples | Hallucination | No Hallucination |
|----------------------------------------|-------|---------|---------------|------------------|
| General QA | 0.9271 | 50 | 2 | 48 |
| Math & Calculation | 0.8303 | 116 | 25 | 91 |
| Attribute Recognition | 0.7381 | 628 | 71 | 557 |
| Visual Understanding | 0.7071 | 611 | 69 | 542 |
| Spatial Reasoning | 0.6831 | 331 | 4 | 327 |
| Text & OCR | 0.6155 | 110 | 9 | 101 |
| Knowledge & Identity | 0.5354 | 124 | 4 | 120 |
| Temporal & Video | 0.2344 | 30 | 14 | 16 |

---

## Performance by Answer Type

| Answer Type | AUROC | Samples | Hallucination | No Hallucination |
|----------------------------------------|-------|---------|---------------|------------------|
| Yes/No | 0.6137 | 1314 | 198 | 1116 |
| Number | N/A | 127 | 0 | 127 |
| Open-Ended | N/A | 410 | 0 | 410 |
| Selection | N/A | 11 | 0 | 11 |
| Unanswerable | N/A | 138 | 0 | 138 |

---

