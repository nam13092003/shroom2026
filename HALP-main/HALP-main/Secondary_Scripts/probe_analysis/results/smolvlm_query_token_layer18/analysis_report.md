# Probe Performance Analysis by Category

**Model:** SmolVLM2-2.2B
**Embedding Type:** query_token_representation / layer_18
**Analysis Date:** 2025-10-05 16:16:50

---

## Overall Performance

**Test AUROC:** 0.6868

---

## Performance by Source Dataset

| Source Dataset | AUROC | Samples | Hallucination | No Hallucination |
|----------------|-------|---------|---------------|------------------|
| hallusionbench | 0.6336 | 123 | 53 | 70 |
| amber | 0.5601 | 786 | 117 | 669 |
| mme | 0.5306 | 176 | 9 | 167 |
| pope | 0.4854 | 242 | 19 | 223 |
| haloquest | N/A | 569 | 0 | 569 |
| mathvista | N/A | 104 | 0 | 104 |

---

## Performance by Category (Top 20)

| Category | AUROC | Samples | Hallucination | No Hallucination |
|----------|-------|---------|---------------|------------------|
| math | 0.8963 | 24 | 9 | 15 |
| figure | 0.7500 | 5 | 1 | 4 |
| table | 0.7381 | 13 | 6 | 7 |
| artwork | 0.7333 | 16 | 1 | 15 |
| popular | 0.7207 | 74 | 7 | 67 |
| illusion | 0.7019 | 21 | 8 | 13 |
| ocr | 0.6250 | 6 | 4 | 2 |
| commonsense_reasoning | 0.6154 | 15 | 2 | 13 |
| posters | 0.5652 | 24 | 1 | 23 |
| discriminative-attribute-number | 0.5478 | 61 | 22 | 39 |
| relation | 0.5374 | 131 | 4 | 127 |
| discriminative-attribute-state | 0.5096 | 263 | 47 | 216 |
| discriminative-hallucination | 0.4801 | 126 | 43 | 83 |
| chart | 0.4722 | 17 | 9 | 8 |
| adversarial | 0.3350 | 73 | 11 | 62 |
| map | 0.3000 | 7 | 2 | 5 |
| video | 0.2612 | 30 | 14 | 16 |
| discriminative-attribute-action | 0.1000 | 11 | 1 | 10 |
| text_translation | 0.0938 | 8 | 4 | 4 |
| random | 0.0638 | 95 | 1 | 94 |

---

## Performance by Category (Bottom 20)

| Category | AUROC | Samples | Hallucination | No Hallucination |
|----------|-------|---------|---------------|------------------|
| figure | 0.7500 | 5 | 1 | 4 |
| table | 0.7381 | 13 | 6 | 7 |
| artwork | 0.7333 | 16 | 1 | 15 |
| popular | 0.7207 | 74 | 7 | 67 |
| illusion | 0.7019 | 21 | 8 | 13 |
| ocr | 0.6250 | 6 | 4 | 2 |
| commonsense_reasoning | 0.6154 | 15 | 2 | 13 |
| posters | 0.5652 | 24 | 1 | 23 |
| discriminative-attribute-number | 0.5478 | 61 | 22 | 39 |
| relation | 0.5374 | 131 | 4 | 127 |
| discriminative-attribute-state | 0.5096 | 263 | 47 | 216 |
| discriminative-hallucination | 0.4801 | 126 | 43 | 83 |
| chart | 0.4722 | 17 | 9 | 8 |
| adversarial | 0.3350 | 73 | 11 | 62 |
| map | 0.3000 | 7 | 2 | 5 |
| video | 0.2612 | 30 | 14 | 16 |
| discriminative-attribute-action | 0.1000 | 11 | 1 | 10 |
| text_translation | 0.0938 | 8 | 4 | 4 |
| random | 0.0638 | 95 | 1 | 94 |
| landmark | 0.0000 | 11 | 1 | 10 |

---

## Categories with Single Class (No AUROC)

| Category | Samples | Note |
|----------|---------|------|
| celebrity | 75 | Single class only |
| code_reasoning | 4 | Single class only |
| color | 2 | Single class only |
| count | 3 | Single class only |
| discriminative-relation | 178 | Single class only |
| existence | 3 | Single class only |
| false premises | 196 | Single class only |
| general-vqa | 47 | Single class only |
| generative | 16 | Single class only |
| insufficient context | 68 | Single class only |
| math-targeted-vqa | 57 | Single class only |
| position | 8 | Single class only |
| scene | 7 | Single class only |
| visual challenge | 305 | Single class only |
