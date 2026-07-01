# Detailed Hallucination Type Analysis

**Probe:** LLaVA-Next-8B/query_token_layer_n_2
**Analysis Date:** 2025-10-05 20:16:05

---

## Overall Performance

**Test AUROC:** 0.9049

---

## Performance by Basic Hallucination Type

| Basic Hallucination Type | AUROC | Samples | Hallucination | No Hallucination |
|----------------------------------------|-------|---------|---------------|------------------|
| Object-Related | 0.9448 | 728 | 62 | 666 |
| Attribute-Related | 0.9017 | 313 | 57 | 256 |
| Other | 0.8881 | 648 | 107 | 541 |
| Relationship | 0.8290 | 311 | 46 | 265 |

---

## Performance by Domain Type

| Domain Type | AUROC | Samples | Hallucination | No Hallucination |
|----------------------------------------|-------|---------|---------------|------------------|
| Attribute Recognition | 0.9346 | 597 | 63 | 534 |
| Visual Understanding | 0.9274 | 615 | 66 | 549 |
| Math & Calculation | 0.8977 | 119 | 29 | 90 |
| General QA | 0.8544 | 59 | 7 | 52 |
| Knowledge & Identity | 0.8513 | 134 | 30 | 104 |
| Spatial Reasoning | 0.8345 | 327 | 46 | 281 |
| Text & OCR | 0.7836 | 110 | 7 | 103 |
| Temporal & Video | 0.4556 | 39 | 24 | 15 |

---

## Performance by Answer Type

| Answer Type | AUROC | Samples | Hallucination | No Hallucination |
|----------------------------------------|-------|---------|---------------|------------------|
| Yes/No | 0.8650 | 1291 | 272 | 1019 |
| Number | N/A | 133 | 0 | 133 |
| Open-Ended | N/A | 403 | 0 | 403 |
| Selection | N/A | 6 | 0 | 6 |
| Unanswerable | N/A | 167 | 0 | 167 |

---

