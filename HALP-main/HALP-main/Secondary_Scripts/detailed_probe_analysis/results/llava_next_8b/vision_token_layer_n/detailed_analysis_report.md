# Detailed Hallucination Type Analysis

**Probe:** LLaVA-Next-8B/vision_token_layer_n
**Analysis Date:** 2025-10-05 20:16:28

---

## Overall Performance

**Test AUROC:** 0.6270

---

## Performance by Basic Hallucination Type

| Basic Hallucination Type | AUROC | Samples | Hallucination | No Hallucination |
|----------------------------------------|-------|---------|---------------|------------------|
| Object-Related | 0.7670 | 728 | 62 | 666 |
| Other | 0.6537 | 648 | 107 | 541 |
| Attribute-Related | 0.5068 | 313 | 57 | 256 |
| Relationship | 0.4045 | 311 | 46 | 265 |

---

## Performance by Domain Type

| Domain Type | AUROC | Samples | Hallucination | No Hallucination |
|----------------------------------------|-------|---------|---------------|------------------|
| General QA | 0.7830 | 59 | 7 | 52 |
| Visual Understanding | 0.7465 | 615 | 66 | 549 |
| Attribute Recognition | 0.6239 | 597 | 63 | 534 |
| Math & Calculation | 0.6157 | 119 | 29 | 90 |
| Text & OCR | 0.5763 | 110 | 7 | 103 |
| Knowledge & Identity | 0.4579 | 134 | 30 | 104 |
| Spatial Reasoning | 0.4139 | 327 | 46 | 281 |
| Temporal & Video | 0.4000 | 39 | 24 | 15 |

---

## Performance by Answer Type

| Answer Type | AUROC | Samples | Hallucination | No Hallucination |
|----------------------------------------|-------|---------|---------------|------------------|
| Yes/No | 0.5354 | 1291 | 272 | 1019 |
| Number | N/A | 133 | 0 | 133 |
| Open-Ended | N/A | 403 | 0 | 403 |
| Selection | N/A | 6 | 0 | 6 |
| Unanswerable | N/A | 167 | 0 | 167 |

---

