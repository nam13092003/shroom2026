# Detailed Hallucination Type Analysis

**Probe:** LLaVA-Next-8B/vision_token_layer_n_4
**Analysis Date:** 2025-10-05 20:16:38

---

## Overall Performance

**Test AUROC:** 0.6185

---

## Performance by Basic Hallucination Type

| Basic Hallucination Type | AUROC | Samples | Hallucination | No Hallucination |
|----------------------------------------|-------|---------|---------------|------------------|
| Object-Related | 0.7089 | 728 | 62 | 666 |
| Other | 0.6643 | 648 | 107 | 541 |
| Attribute-Related | 0.5160 | 313 | 57 | 256 |
| Relationship | 0.3371 | 311 | 46 | 265 |

---

## Performance by Domain Type

| Domain Type | AUROC | Samples | Hallucination | No Hallucination |
|----------------------------------------|-------|---------|---------------|------------------|
| Text & OCR | 0.7302 | 110 | 7 | 103 |
| Visual Understanding | 0.6902 | 615 | 66 | 549 |
| General QA | 0.6841 | 59 | 7 | 52 |
| Attribute Recognition | 0.6625 | 597 | 63 | 534 |
| Math & Calculation | 0.5870 | 119 | 29 | 90 |
| Temporal & Video | 0.5361 | 39 | 24 | 15 |
| Knowledge & Identity | 0.4928 | 134 | 30 | 104 |
| Spatial Reasoning | 0.3537 | 327 | 46 | 281 |

---

## Performance by Answer Type

| Answer Type | AUROC | Samples | Hallucination | No Hallucination |
|----------------------------------------|-------|---------|---------------|------------------|
| Yes/No | 0.5148 | 1291 | 272 | 1019 |
| Number | N/A | 133 | 0 | 133 |
| Open-Ended | N/A | 403 | 0 | 403 |
| Selection | N/A | 6 | 0 | 6 |
| Unanswerable | N/A | 167 | 0 | 167 |

---

