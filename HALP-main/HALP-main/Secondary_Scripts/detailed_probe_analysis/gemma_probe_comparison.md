# Gemma Probe Comparison Analysis
Comparing predictions across Vision-only, Vision-token (layer 47), and Query-token (layer 47) probes

---


## Basic Hallucination Type: Object-Related

### Case 1: Vision-only failed ❌ → Query-token succeeded ✅

**Example 98**

- **Question ID:** `question_comb_3910`
- **Image:** `Unknown`
- **Question:** Is there a bicycle in the image?
- **Ground Truth:** yes
- **Model Answer:** Yes, there is a bicycle in the image. It's an orange bicycle positioned to the left of a scooter.
- **True Label:** No Hallucination
- **Domain Type:** Visual Understanding

**Probe Predictions:**
- Vision-only: Hallucination (prob: 0.947) ❌
- Vision-token (L47): Hallucination (prob: 0.981) ❌
- Query-token (L47): No Hallucination (prob: 0.000) ✅

---

**Example 111**

- **Question ID:** `question_comb_4375`
- **Image:** `Unknown`
- **Question:** Is there a total of two display devices in the image? Please answer yes or no.
- **Ground Truth:** Yes
- **Model Answer:** Yes.
- **True Label:** No Hallucination
- **Domain Type:** Attribute Recognition

**Probe Predictions:**
- Vision-only: Hallucination (prob: 0.720) ❌
- Vision-token (L47): Hallucination (prob: 0.679) ❌
- Query-token (L47): No Hallucination (prob: 0.086) ✅

---

### Case 2: Vision-only ❌ AND Vision-token ❌ → Query-token succeeded ✅

**Example**

- **Question ID:** `question_comb_3910`
- **Image:** `Unknown`
- **Question:** Is there a bicycle in the image?
- **Ground Truth:** yes
- **Model Answer:** Yes, there is a bicycle in the image. It's an orange bicycle positioned to the left of a scooter.
- **True Label:** No Hallucination
- **Domain Type:** Visual Understanding

**Probe Predictions:**
- Vision-only: Hallucination (prob: 0.947) ❌
- Vision-token (L47): Hallucination (prob: 0.981) ❌
- Query-token (L47): No Hallucination (prob: 0.000) ✅

---

### Case 3: Vision-only ❌ AND Query-token ❌ → Vision-token succeeded ✅

**Example**

- **Question ID:** `question_comb_7195`
- **Image:** `Unknown`
- **Question:** Is there a truck in the image?
- **Ground Truth:** no
- **Model Answer:** Yes, there is a truck in the image. It's visible in the distance, further down the road, among the other vehicles.
- **True Label:** Hallucination
- **Domain Type:** Visual Understanding

**Probe Predictions:**
- Vision-only: No Hallucination (prob: 0.459) ❌
- Vision-token (L12): Hallucination (prob: 0.848) ✅
- Query-token (L47): No Hallucination (prob: 0.022) ❌

---


## Basic Hallucination Type: Relationship

### Case 1: Vision-only failed ❌ → Query-token succeeded ✅

**Example 170**

- **Question ID:** `question_comb_1038`
- **Image:** `Unknown`
- **Question:** Is there direct contact between the table and keyboard?
- **Ground Truth:** y, e, s
- **Model Answer:** Based on the image, it appears there is **no direct contact** between the table and the keyboard. The keyboard is resting on a thick, fluffy rug or mat.
- **True Label:** No Hallucination
- **Domain Type:** Spatial Reasoning

**Probe Predictions:**
- Vision-only: Hallucination (prob: 0.631) ❌
- Vision-token (L47): No Hallucination (prob: 0.000) ✅
- Query-token (L47): No Hallucination (prob: 0.002) ✅

---

**Example 225**

- **Question ID:** `question_comb_6647`
- **Image:** `Unknown`
- **Question:** Is the pineapple on the left of the pot in the image? Please answer yes or no.
- **Ground Truth:** Yes
- **Model Answer:** Yes.
- **True Label:** No Hallucination
- **Domain Type:** Spatial Reasoning

**Probe Predictions:**
- Vision-only: Hallucination (prob: 0.973) ❌
- Vision-token (L47): Hallucination (prob: 0.751) ❌
- Query-token (L47): No Hallucination (prob: 0.448) ✅

---

### Case 2: Vision-only ❌ AND Vision-token ❌ → Query-token succeeded ✅

**Example**

- **Question ID:** `question_comb_6647`
- **Image:** `Unknown`
- **Question:** Is the pineapple on the left of the pot in the image? Please answer yes or no.
- **Ground Truth:** Yes
- **Model Answer:** Yes.
- **True Label:** No Hallucination
- **Domain Type:** Spatial Reasoning

**Probe Predictions:**
- Vision-only: Hallucination (prob: 0.973) ❌
- Vision-token (L47): Hallucination (prob: 0.751) ❌
- Query-token (L47): No Hallucination (prob: 0.448) ✅

---


## Basic Hallucination Type: Attribute-Related

### Case 1: Vision-only failed ❌ → Query-token succeeded ✅

**Example 164**

- **Question ID:** `question_comb_9541`
- **Image:** `Unknown`
- **Question:** Are there two baseballs in this image?
- **Ground Truth:** n, o
- **Model Answer:** Yes, there are two baseballs in the image. One is in the catcher's hand, and the other is slightly blurred in the air, presumably just thrown by the pitcher.
- **True Label:** Hallucination
- **Domain Type:** Attribute Recognition

**Probe Predictions:**
- Vision-only: No Hallucination (prob: 0.001) ❌
- Vision-token (L47): No Hallucination (prob: 0.000) ❌
- Query-token (L47): Hallucination (prob: 0.983) ✅

---

**Example 217**

- **Question ID:** `question_comb_5146`
- **Image:** `Unknown`
- **Question:** Are there two birds in this image?
- **Ground Truth:** n, o
- **Model Answer:** Yes, there are two birds in the image. 

*   One is a seagull standing prominently in the foreground.
*   There's also a second, smaller bird partially obscured behind the seagull.
- **True Label:** Hallucination
- **Domain Type:** Attribute Recognition

**Probe Predictions:**
- Vision-only: No Hallucination (prob: 0.002) ❌
- Vision-token (L47): No Hallucination (prob: 0.000) ❌
- Query-token (L47): Hallucination (prob: 0.976) ✅

---

### Case 2: Vision-only ❌ AND Vision-token ❌ → Query-token succeeded ✅

**Example**

- **Question ID:** `question_comb_9541`
- **Image:** `Unknown`
- **Question:** Are there two baseballs in this image?
- **Ground Truth:** n, o
- **Model Answer:** Yes, there are two baseballs in the image. One is in the catcher's hand, and the other is slightly blurred in the air, presumably just thrown by the pitcher.
- **True Label:** Hallucination
- **Domain Type:** Attribute Recognition

**Probe Predictions:**
- Vision-only: No Hallucination (prob: 0.001) ❌
- Vision-token (L47): No Hallucination (prob: 0.000) ❌
- Query-token (L47): Hallucination (prob: 0.983) ✅

---

### Case 3: Vision-only ❌ AND Query-token ❌ → Vision-token succeeded ✅

**Example**

- **Question ID:** `question_comb_8119`
- **Image:** `Unknown`
- **Question:** Is the mountain tall in this image?
- **Ground Truth:** n, o
- **Model Answer:** Based on the image, the mountain in the background appears to be relatively tall, but it's difficult to say definitively without a reference point for scale. Here's what we can observe:

*   **Distance:** The mountain is far in the background, which makes judging its height challenging.
*   **Relative Size:** Compared to the giraffes, which are quite tall animals, the mountain still appears to be significantly larger.
*   **Horizon Line:** The mountain extends a considerable distance above the horizon line.

Overall, it seems likely that the mountain is a substantial height, though it's hard to give an exact measurement.
- **True Label:** Hallucination
- **Domain Type:** Attribute Recognition

**Probe Predictions:**
- Vision-only: No Hallucination (prob: 0.241) ❌
- Vision-token (L12): Hallucination (prob: 0.981) ✅
- Query-token (L47): No Hallucination (prob: 0.434) ❌

---


## Basic Hallucination Type: Other

### Case 1: Vision-only failed ❌ → Query-token succeeded ✅

**Example 10**

- **Question ID:** `question_comb_6250`
- **Image:** `Unknown`
- **Question:** Is the actor inside the red bounding box called William Shatner? Please answer yes or no.
- **Ground Truth:** Yes
- **Model Answer:** No.

The actor in the image is Patrick Stewart, not William Shatner.
- **True Label:** Hallucination
- **Domain Type:** Knowledge & Identity

**Probe Predictions:**
- Vision-only: No Hallucination (prob: 0.009) ❌
- Vision-token (L47): No Hallucination (prob: 0.000) ❌
- Query-token (L47): Hallucination (prob: 0.852) ✅

---

**Example 19**

- **Question ID:** `question_comb_6022`
- **Image:** `Unknown`
- **Question:** According to the table, does the SABMiller India have the second highest portion of the market share for beer across India in 2020?
- **Ground Truth:** yes
- **Model Answer:** No, according to the table, Carlsberg India has the second highest portion of the market share for beer across India in 2020.

Here's the breakdown:

*   **UB Group:** 54%
*   **Carlsberg India:** 15.4%
*   **SABMiller India:** 17.1%

Carlsberg India (15.4%) has a smaller market share than SABMiller India (17.1%).
- **True Label:** Hallucination
- **Domain Type:** Math & Calculation

**Probe Predictions:**
- Vision-only: No Hallucination (prob: 0.200) ❌
- Vision-token (L47): No Hallucination (prob: 0.001) ❌
- Query-token (L47): Hallucination (prob: 0.541) ✅

---

### Case 2: Vision-only ❌ AND Vision-token ❌ → Query-token succeeded ✅

**Example**

- **Question ID:** `question_comb_6250`
- **Image:** `Unknown`
- **Question:** Is the actor inside the red bounding box called William Shatner? Please answer yes or no.
- **Ground Truth:** Yes
- **Model Answer:** No.

The actor in the image is Patrick Stewart, not William Shatner.
- **True Label:** Hallucination
- **Domain Type:** Knowledge & Identity

**Probe Predictions:**
- Vision-only: No Hallucination (prob: 0.009) ❌
- Vision-token (L47): No Hallucination (prob: 0.000) ❌
- Query-token (L47): Hallucination (prob: 0.852) ✅

---

### Case 3: Vision-only ❌ AND Query-token ❌ → Vision-token succeeded ✅

**Example**

- **Question ID:** `question_comb_5323`
- **Image:** `Unknown`
- **Question:** This woman is jumping out from a toilet. According to the positive sequence of the images, are they in the correct order? Answer in one word.
- **Ground Truth:** yes
- **Model Answer:** Yes.
- **True Label:** No Hallucination
- **Domain Type:** Temporal & Video

**Probe Predictions:**
- Vision-only: Hallucination (prob: 0.639) ❌
- Vision-token (L12): No Hallucination (prob: 0.499) ✅
- Query-token (L47): Hallucination (prob: 0.722) ❌

---

