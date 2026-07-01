# Detailed Hallucination Type Analysis

**Probe:** LLaVA-Next-8B/vision_token_layer0
**Analysis Date:** 2025-10-05 20:16:19

---

## Overall Performance

**Test AUROC:** 0.6037

---

## Performance by Basic Hallucination Type

| Basic Hallucination Type | AUROC | Samples | Hallucination | No Hallucination |
|----------------------------------------|-------|---------|---------------|------------------|
| Object-Related | 0.7052 | 728 | 62 | 666 |
| Other | 0.6217 | 648 | 107 | 541 |
| Attribute-Related | 0.5224 | 313 | 57 | 256 |
| Relationship | 0.3790 | 311 | 46 | 265 |

---

## Performance by Domain Type

| Domain Type | AUROC | Samples | Hallucination | No Hallucination |
|----------------------------------------|-------|---------|---------------|------------------|
| Visual Understanding | 0.6859 | 615 | 66 | 549 |
| Attribute Recognition | 0.6434 | 597 | 63 | 534 |
| Text & OCR | 0.6338 | 110 | 7 | 103 |
| Math & Calculation | 0.5908 | 119 | 29 | 90 |
| General QA | 0.5604 | 59 | 7 | 52 |
| Knowledge & Identity | 0.4566 | 134 | 30 | 104 |
| Temporal & Video | 0.4111 | 39 | 24 | 15 |
| Spatial Reasoning | 0.3939 | 327 | 46 | 281 |

---

## Performance by Answer Type

| Answer Type | AUROC | Samples | Hallucination | No Hallucination |
|----------------------------------------|-------|---------|---------------|------------------|
| Yes/No | 0.5183 | 1291 | 272 | 1019 |
| Number | N/A | 133 | 0 | 133 |
| Open-Ended | N/A | 403 | 0 | 403 |
| Selection | N/A | 6 | 0 | 6 |
| Unanswerable | N/A | 167 | 0 | 167 |

---

