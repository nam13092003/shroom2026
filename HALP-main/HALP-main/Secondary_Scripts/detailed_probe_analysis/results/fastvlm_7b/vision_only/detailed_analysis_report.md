# Detailed Hallucination Type Analysis

**Probe:** FastVLM-7B/vision_only
**Analysis Date:** 2025-10-05 20:15:23

---

## Overall Performance

**Test AUROC:** 0.6830

---

## Performance by Basic Hallucination Type

| Basic Hallucination Type | AUROC | Samples | Hallucination | No Hallucination |
|----------------------------------------|-------|---------|---------------|------------------|
| Object-Related | 0.7263 | 690 | 38 | 652 |
| Other | 0.7167 | 645 | 84 | 561 |
| Attribute-Related | 0.5553 | 324 | 30 | 294 |
| Relationship | 0.4078 | 341 | 22 | 319 |

---

## Performance by Domain Type

| Domain Type | AUROC | Samples | Hallucination | No Hallucination |
|----------------------------------------|-------|---------|---------------|------------------|
| Math & Calculation | 0.8603 | 129 | 20 | 109 |
| Text & OCR | 0.8158 | 106 | 6 | 100 |
| Visual Understanding | 0.7254 | 581 | 44 | 537 |
| Attribute Recognition | 0.6689 | 606 | 32 | 574 |
| General QA | 0.5833 | 54 | 6 | 48 |
| Knowledge & Identity | 0.4628 | 143 | 34 | 109 |
| Spatial Reasoning | 0.4104 | 346 | 22 | 324 |
| Temporal & Video | 0.4080 | 35 | 10 | 25 |

---

## Performance by Answer Type

| Answer Type | AUROC | Samples | Hallucination | No Hallucination |
|----------------------------------------|-------|---------|---------------|------------------|
| Yes/No | 0.6120 | 1292 | 174 | 1118 |
| Number | N/A | 146 | 0 | 146 |
| Open-Ended | N/A | 387 | 0 | 387 |
| Selection | N/A | 6 | 0 | 6 |
| Unanswerable | N/A | 169 | 0 | 169 |

---

