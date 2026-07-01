# Detailed Hallucination Type Analysis

**Probe:** LLaVA-Next-8B/query_token_layer_n
**Analysis Date:** 2025-10-05 20:16:01

---

## Overall Performance

**Test AUROC:** 0.9026

---

## Performance by Basic Hallucination Type

| Basic Hallucination Type | AUROC | Samples | Hallucination | No Hallucination |
|----------------------------------------|-------|---------|---------------|------------------|
| Object-Related | 0.9546 | 728 | 62 | 666 |
| Attribute-Related | 0.9060 | 313 | 57 | 256 |
| Relationship | 0.8767 | 311 | 46 | 265 |
| Other | 0.8750 | 648 | 107 | 541 |

---

## Performance by Domain Type

| Domain Type | AUROC | Samples | Hallucination | No Hallucination |
|----------------------------------------|-------|---------|---------------|------------------|
| Attribute Recognition | 0.9410 | 597 | 63 | 534 |
| Visual Understanding | 0.9266 | 615 | 66 | 549 |
| Text & OCR | 0.9098 | 110 | 7 | 103 |
| Math & Calculation | 0.9019 | 119 | 29 | 90 |
| Spatial Reasoning | 0.8837 | 327 | 46 | 281 |
| General QA | 0.8516 | 59 | 7 | 52 |
| Knowledge & Identity | 0.7923 | 134 | 30 | 104 |
| Temporal & Video | 0.4306 | 39 | 24 | 15 |

---

## Performance by Answer Type

| Answer Type | AUROC | Samples | Hallucination | No Hallucination |
|----------------------------------------|-------|---------|---------------|------------------|
| Yes/No | 0.8445 | 1291 | 272 | 1019 |
| Number | N/A | 133 | 0 | 133 |
| Open-Ended | N/A | 403 | 0 | 403 |
| Selection | N/A | 6 | 0 | 6 |
| Unanswerable | N/A | 167 | 0 | 167 |

---

