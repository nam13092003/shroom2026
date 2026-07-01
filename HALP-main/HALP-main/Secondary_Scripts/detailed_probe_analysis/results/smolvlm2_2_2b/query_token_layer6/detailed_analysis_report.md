# Detailed Hallucination Type Analysis

**Probe:** SmolVLM2-2.2B/query_token_layer6
**Analysis Date:** 2025-10-05 20:18:36

---

## Overall Performance

**Test AUROC:** 0.8971

---

## Performance by Basic Hallucination Type

| Basic Hallucination Type | AUROC | Samples | Hallucination | No Hallucination |
|----------------------------------------|-------|---------|---------------|------------------|
| Other | 0.9265 | 621 | 63 | 558 |
| Object-Related | 0.8999 | 708 | 62 | 646 |
| Relationship | 0.8914 | 317 | 4 | 313 |
| Attribute-Related | 0.7513 | 354 | 69 | 285 |

---

## Performance by Domain Type

| Domain Type | AUROC | Samples | Hallucination | No Hallucination |
|----------------------------------------|-------|---------|---------------|------------------|
| Knowledge & Identity | 0.9729 | 124 | 4 | 120 |
| Text & OCR | 0.9527 | 110 | 9 | 101 |
| General QA | 0.9271 | 50 | 2 | 48 |
| Spatial Reasoning | 0.8922 | 331 | 4 | 327 |
| Math & Calculation | 0.8877 | 116 | 25 | 91 |
| Visual Understanding | 0.8651 | 611 | 69 | 542 |
| Attribute Recognition | 0.8649 | 628 | 71 | 557 |
| Temporal & Video | 0.4688 | 30 | 14 | 16 |

---

## Performance by Answer Type

| Answer Type | AUROC | Samples | Hallucination | No Hallucination |
|----------------------------------------|-------|---------|---------------|------------------|
| Yes/No | 0.8386 | 1314 | 198 | 1116 |
| Number | N/A | 127 | 0 | 127 |
| Open-Ended | N/A | 410 | 0 | 410 |
| Selection | N/A | 11 | 0 | 11 |
| Unanswerable | N/A | 138 | 0 | 138 |

---

