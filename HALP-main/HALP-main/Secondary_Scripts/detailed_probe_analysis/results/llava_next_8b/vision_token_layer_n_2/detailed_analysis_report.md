# Detailed Hallucination Type Analysis

**Probe:** LLaVA-Next-8B/vision_token_layer_n_2
**Analysis Date:** 2025-10-05 20:16:33

---

## Overall Performance

**Test AUROC:** 0.6192

---

## Performance by Basic Hallucination Type

| Basic Hallucination Type | AUROC | Samples | Hallucination | No Hallucination |
|----------------------------------------|-------|---------|---------------|------------------|
| Object-Related | 0.7492 | 728 | 62 | 666 |
| Other | 0.6444 | 648 | 107 | 541 |
| Attribute-Related | 0.5045 | 313 | 57 | 256 |
| Relationship | 0.3981 | 311 | 46 | 265 |

---

## Performance by Domain Type

| Domain Type | AUROC | Samples | Hallucination | No Hallucination |
|----------------------------------------|-------|---------|---------------|------------------|
| Visual Understanding | 0.7262 | 615 | 66 | 549 |
| General QA | 0.6841 | 59 | 7 | 52 |
| Attribute Recognition | 0.6269 | 597 | 63 | 534 |
| Math & Calculation | 0.6169 | 119 | 29 | 90 |
| Knowledge & Identity | 0.4771 | 134 | 30 | 104 |
| Text & OCR | 0.4313 | 110 | 7 | 103 |
| Spatial Reasoning | 0.4138 | 327 | 46 | 281 |
| Temporal & Video | 0.3722 | 39 | 24 | 15 |

---

## Performance by Answer Type

| Answer Type | AUROC | Samples | Hallucination | No Hallucination |
|----------------------------------------|-------|---------|---------------|------------------|
| Yes/No | 0.5244 | 1291 | 272 | 1019 |
| Number | N/A | 133 | 0 | 133 |
| Open-Ended | N/A | 403 | 0 | 403 |
| Selection | N/A | 6 | 0 | 6 |
| Unanswerable | N/A | 167 | 0 | 167 |

---

