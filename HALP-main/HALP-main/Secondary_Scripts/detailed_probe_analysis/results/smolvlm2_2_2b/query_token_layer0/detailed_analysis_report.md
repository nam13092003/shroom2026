# Detailed Hallucination Type Analysis

**Probe:** SmolVLM2-2.2B/query_token_layer0
**Analysis Date:** 2025-10-05 20:18:20

---

## Overall Performance

**Test AUROC:** 0.5040

---

## Performance by Basic Hallucination Type

| Basic Hallucination Type | AUROC | Samples | Hallucination | No Hallucination |
|----------------------------------------|-------|---------|---------------|------------------|
| Attribute-Related | 0.5075 | 354 | 69 | 285 |
| Other | 0.5052 | 621 | 63 | 558 |
| Object-Related | 0.4992 | 708 | 62 | 646 |
| Relationship | 0.4920 | 317 | 4 | 313 |

---

## Performance by Domain Type

| Domain Type | AUROC | Samples | Hallucination | No Hallucination |
|----------------------------------------|-------|---------|---------------|------------------|
| Text & OCR | 0.5556 | 110 | 9 | 101 |
| Attribute Recognition | 0.5096 | 628 | 71 | 557 |
| Temporal & Video | 0.5000 | 30 | 14 | 16 |
| Knowledge & Identity | 0.5000 | 124 | 4 | 120 |
| Visual Understanding | 0.4991 | 611 | 69 | 542 |
| Math & Calculation | 0.4945 | 116 | 25 | 91 |
| Spatial Reasoning | 0.4924 | 331 | 4 | 327 |
| General QA | 0.4896 | 50 | 2 | 48 |

---

## Performance by Answer Type

| Answer Type | AUROC | Samples | Hallucination | No Hallucination |
|----------------------------------------|-------|---------|---------------|------------------|
| Yes/No | 0.5026 | 1314 | 198 | 1116 |
| Number | N/A | 127 | 0 | 127 |
| Open-Ended | N/A | 410 | 0 | 410 |
| Selection | N/A | 11 | 0 | 11 |
| Unanswerable | N/A | 138 | 0 | 138 |

---

