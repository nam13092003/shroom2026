# Detailed Hallucination Type Analysis

**Probe:** LLaVA-Next-8B/query_token_layer0
**Analysis Date:** 2025-10-05 20:15:51

---

## Overall Performance

**Test AUROC:** 0.4996

---

## Performance by Basic Hallucination Type

| Basic Hallucination Type | AUROC | Samples | Hallucination | No Hallucination |
|----------------------------------------|-------|---------|---------------|------------------|
| Relationship | 0.5052 | 311 | 46 | 265 |
| Other | 0.5010 | 648 | 107 | 541 |
| Attribute-Related | 0.4980 | 313 | 57 | 256 |
| Object-Related | 0.4955 | 728 | 62 | 666 |

---

## Performance by Domain Type

| Domain Type | AUROC | Samples | Hallucination | No Hallucination |
|----------------------------------------|-------|---------|---------------|------------------|
| Text & OCR | 0.5666 | 110 | 7 | 103 |
| Spatial Reasoning | 0.5055 | 327 | 46 | 281 |
| General QA | 0.5000 | 59 | 7 | 52 |
| Math & Calculation | 0.5000 | 119 | 29 | 90 |
| Temporal & Video | 0.5000 | 39 | 24 | 15 |
| Attribute Recognition | 0.4963 | 597 | 63 | 534 |
| Visual Understanding | 0.4954 | 615 | 66 | 549 |
| Knowledge & Identity | 0.4952 | 134 | 30 | 104 |

---

## Performance by Answer Type

| Answer Type | AUROC | Samples | Hallucination | No Hallucination |
|----------------------------------------|-------|---------|---------------|------------------|
| Yes/No | 0.4998 | 1291 | 272 | 1019 |
| Number | N/A | 133 | 0 | 133 |
| Open-Ended | N/A | 403 | 0 | 403 |
| Selection | N/A | 6 | 0 | 6 |
| Unanswerable | N/A | 167 | 0 | 167 |

---

