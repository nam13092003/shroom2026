# Detailed Hallucination Type Analysis

**Probe:** LLaVA-Next-8B/query_token_layer_3n_4
**Analysis Date:** 2025-10-05 20:15:56

---

## Overall Performance

**Test AUROC:** 0.9053

---

## Performance by Basic Hallucination Type

| Basic Hallucination Type | AUROC | Samples | Hallucination | No Hallucination |
|----------------------------------------|-------|---------|---------------|------------------|
| Object-Related | 0.9693 | 728 | 62 | 666 |
| Attribute-Related | 0.9077 | 313 | 57 | 256 |
| Other | 0.8646 | 648 | 107 | 541 |
| Relationship | 0.8568 | 311 | 46 | 265 |

---

## Performance by Domain Type

| Domain Type | AUROC | Samples | Hallucination | No Hallucination |
|----------------------------------------|-------|---------|---------------|------------------|
| Text & OCR | 0.9612 | 110 | 7 | 103 |
| Visual Understanding | 0.9423 | 615 | 66 | 549 |
| Attribute Recognition | 0.9410 | 597 | 63 | 534 |
| Math & Calculation | 0.9046 | 119 | 29 | 90 |
| Spatial Reasoning | 0.8648 | 327 | 46 | 281 |
| General QA | 0.8159 | 59 | 7 | 52 |
| Knowledge & Identity | 0.7074 | 134 | 30 | 104 |
| Temporal & Video | 0.3722 | 39 | 24 | 15 |

---

## Performance by Answer Type

| Answer Type | AUROC | Samples | Hallucination | No Hallucination |
|----------------------------------------|-------|---------|---------------|------------------|
| Yes/No | 0.8558 | 1291 | 272 | 1019 |
| Number | N/A | 133 | 0 | 133 |
| Open-Ended | N/A | 403 | 0 | 403 |
| Selection | N/A | 6 | 0 | 6 |
| Unanswerable | N/A | 167 | 0 | 167 |

---

