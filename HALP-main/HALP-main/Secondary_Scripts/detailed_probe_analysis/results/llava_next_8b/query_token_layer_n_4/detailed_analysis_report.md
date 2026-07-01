# Detailed Hallucination Type Analysis

**Probe:** LLaVA-Next-8B/query_token_layer_n_4
**Analysis Date:** 2025-10-05 20:16:10

---

## Overall Performance

**Test AUROC:** 0.8453

---

## Performance by Basic Hallucination Type

| Basic Hallucination Type | AUROC | Samples | Hallucination | No Hallucination |
|----------------------------------------|-------|---------|---------------|------------------|
| Object-Related | 0.8897 | 728 | 62 | 666 |
| Other | 0.8440 | 648 | 107 | 541 |
| Attribute-Related | 0.8365 | 313 | 57 | 256 |
| Relationship | 0.7506 | 311 | 46 | 265 |

---

## Performance by Domain Type

| Domain Type | AUROC | Samples | Hallucination | No Hallucination |
|----------------------------------------|-------|---------|---------------|------------------|
| Attribute Recognition | 0.9029 | 597 | 63 | 534 |
| General QA | 0.8874 | 59 | 7 | 52 |
| Text & OCR | 0.8807 | 110 | 7 | 103 |
| Math & Calculation | 0.8628 | 119 | 29 | 90 |
| Visual Understanding | 0.8539 | 615 | 66 | 549 |
| Spatial Reasoning | 0.7648 | 327 | 46 | 281 |
| Knowledge & Identity | 0.5833 | 134 | 30 | 104 |
| Temporal & Video | 0.3694 | 39 | 24 | 15 |

---

## Performance by Answer Type

| Answer Type | AUROC | Samples | Hallucination | No Hallucination |
|----------------------------------------|-------|---------|---------------|------------------|
| Yes/No | 0.7459 | 1291 | 272 | 1019 |
| Number | N/A | 133 | 0 | 133 |
| Open-Ended | N/A | 403 | 0 | 403 |
| Selection | N/A | 6 | 0 | 6 |
| Unanswerable | N/A | 167 | 0 | 167 |

---

