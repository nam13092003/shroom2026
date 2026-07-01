# Gemma Hallucination Detection - 3 Examples Per Type

---
## Basic Hallucination Type: Object-Related

### Pattern 1: Vision-only ❌ AND Vision-token ❌ → Query-token ✅
_Both vision probes failed to detect hallucination, only query-token succeeded_

**Example 1**

- **Question ID:** `question_comb_3`
- **Image:** `Unknown`
- **Question:** Is there a wall in this image?
- **Ground Truth:** n, o
- **Model Answer:** Yes, there is a wall in the image. It's the light yellow wall that forms the background behind the teddy bears and the book.
- **True Label:** Hallucination ✓
- **Domain Type:** Visual Understanding

**Probe Predictions:**
- Vision-only: No Hallucination (prob: 0.001) ❌ MISSED
- Vision-token (L47): No Hallucination (prob: 0.000) ❌ MISSED
- Query-token (L47): Hallucination (prob: 0.974) ✅ DETECTED

---

**Example 2**

- **Question ID:** `question_comb_6490`
- **Image:** `Unknown`
- **Question:** Is there a sign in this image?
- **Ground Truth:** n, o
- **Model Answer:** Yes, there are signs in the image. They are the number "66" displayed on both sides of the motorcycle.
- **True Label:** Hallucination ✓
- **Domain Type:** Visual Understanding

**Probe Predictions:**
- Vision-only: No Hallucination (prob: 0.001) ❌ MISSED
- Vision-token (L47): No Hallucination (prob: 0.000) ❌ MISSED
- Query-token (L47): Hallucination (prob: 1.000) ✅ DETECTED

---

**Example 3**

- **Question ID:** `question_comb_7091`
- **Image:** `Unknown`
- **Question:** Is there a bowl in the image?
- **Ground Truth:** yes
- **Model Answer:** No, there is no bowl in the image. There is a pitcher of syrup and a glass, but no bowls.
- **True Label:** Hallucination ✓
- **Domain Type:** Visual Understanding

**Probe Predictions:**
- Vision-only: No Hallucination (prob: 0.002) ❌ MISSED
- Vision-token (L47): No Hallucination (prob: 0.000) ❌ MISSED
- Query-token (L47): Hallucination (prob: 0.889) ✅ DETECTED

---

### Pattern 2: Vision-only ❌ → Vision-token ✅ AND Query-token ✅
_Vision-only failed, but both vision-token and query-token detected the hallucination_

**Example 1**

- **Question ID:** `question_comb_2886`
- **Image:** `Unknown`
- **Question:** Is there a person in this image?
- **Ground Truth:** n, o
- **Model Answer:** Yes, there appears to be a person in the image. They are partially visible in the background, reflected in the stainless steel interior of the refrigerator. It looks like they are standing near the open door.
- **True Label:** Hallucination ✓
- **Domain Type:** Visual Understanding

**Probe Predictions:**
- Vision-only: No Hallucination (prob: 0.416) ❌ MISSED
- Vision-token (L47): Hallucination (prob: 0.992) ✅ DETECTED
- Query-token (L47): Hallucination (prob: 0.887) ✅ DETECTED

---

**Example 2**

- **Question ID:** `question_comb_3071`
- **Image:** `Unknown`
- **Question:** Is there a sports ball in the image?
- **Ground Truth:** yes
- **Model Answer:** No, there is no sports ball visible in the image. The people in the picture are playing badminton, and they have badminton rackets.
- **True Label:** Hallucination ✓
- **Domain Type:** Visual Understanding

**Probe Predictions:**
- Vision-only: No Hallucination (prob: 0.482) ❌ MISSED
- Vision-token (L47): Hallucination (prob: 0.634) ✅ DETECTED
- Query-token (L47): Hallucination (prob: 0.970) ✅ DETECTED

---

**Example 3**

- **Question ID:** `question_comb_3775`
- **Image:** `Unknown`
- **Question:** Is there a traffic light in the image?
- **Ground Truth:** yes
- **Model Answer:** No, there is not a traffic light in the image. There is a stop sign on a pole, but it is not a traffic light.
- **True Label:** Hallucination ✓
- **Domain Type:** Visual Understanding

**Probe Predictions:**
- Vision-only: No Hallucination (prob: 0.419) ❌ MISSED
- Vision-token (L47): Hallucination (prob: 0.999) ✅ DETECTED
- Query-token (L47): Hallucination (prob: 0.879) ✅ DETECTED

---


## Basic Hallucination Type: Relationship

### Pattern 1: Vision-only ❌ AND Vision-token ❌ → Query-token ✅
_Both vision probes failed to detect hallucination, only query-token succeeded_

**Example 1**

- **Question ID:** `question_comb_3506`
- **Image:** `Unknown`
- **Question:** Is there direct contact between the sea and forest?
- **Ground Truth:** n, o
- **Model Answer:** Based on the image, yes, there appears to be direct contact between the sea and the forest. 

Here's what I can see:

*   **Sea:** The ocean is visible in the background, with waves and a sandy beach.
*   **Forest:** A dense, green forest is also visible in the background, directly adjacent to the beach.

Therefore, the forest borders the beach, indicating direct contact between the sea and the forest.
- **True Label:** Hallucination ✓
- **Domain Type:** Spatial Reasoning

**Probe Predictions:**
- Vision-only: No Hallucination (prob: 0.013) ❌ MISSED
- Vision-token (L47): No Hallucination (prob: 0.001) ❌ MISSED
- Query-token (L47): Hallucination (prob: 0.656) ✅ DETECTED

---

**Example 2**

- **Question ID:** `question_comb_9021`
- **Image:** `Unknown`
- **Question:** Is there direct contact between the lounge and forest?
- **Ground Truth:** n, o
- **Model Answer:** Based on the image, there appears to be a clear transition zone between the sandy area (where the lounge chairs and umbrella are) and the forest. 

Here's what I can observe:

*   **Sandy Area:** The foreground is dominated by sand.
*   **Transition Zone:** There's a narrow strip of tall grass and vegetation separating the sand from the forest.
*   **Forest:** A dense line of trees forms the backdrop, indicating the edge of the forest.

So, while there isn't a direct, seamless connection, there's a defined boundary with a natural transition zone of vegetation.
- **True Label:** Hallucination ✓
- **Domain Type:** Spatial Reasoning

**Probe Predictions:**
- Vision-only: No Hallucination (prob: 0.000) ❌ MISSED
- Vision-token (L47): No Hallucination (prob: 0.000) ❌ MISSED
- Query-token (L47): Hallucination (prob: 0.511) ✅ DETECTED

---

**Example 3**

- **Question ID:** `question_comb_986`
- **Image:** `Unknown`
- **Question:** Is there direct contact between the refrigerator and microwave?
- **Ground Truth:** n, o
- **Model Answer:** Based on the image, it appears there is **direct contact** between the refrigerator and the microwave. The microwave is positioned right next to the refrigerator, and there doesn't seem to be any significant gap between them.
- **True Label:** Hallucination ✓
- **Domain Type:** Spatial Reasoning

**Probe Predictions:**
- Vision-only: No Hallucination (prob: 0.142) ❌ MISSED
- Vision-token (L47): No Hallucination (prob: 0.445) ❌ MISSED
- Query-token (L47): Hallucination (prob: 0.549) ✅ DETECTED

---

### Pattern 2: Vision-only ❌ → Vision-token ✅ AND Query-token ✅
_Vision-only failed, but both vision-token and query-token detected the hallucination_

_No examples found for this pattern_


## Basic Hallucination Type: Attribute-Related

### Pattern 1: Vision-only ❌ AND Vision-token ❌ → Query-token ✅
_Both vision probes failed to detect hallucination, only query-token succeeded_

**Example 1**

- **Question ID:** `question_comb_9541`
- **Image:** `Unknown`
- **Question:** Are there two baseballs in this image?
- **Ground Truth:** n, o
- **Model Answer:** Yes, there are two baseballs in the image. One is in the catcher's hand, and the other is slightly blurred in the air, presumably just thrown by the pitcher.
- **True Label:** Hallucination ✓
- **Domain Type:** Attribute Recognition

**Probe Predictions:**
- Vision-only: No Hallucination (prob: 0.001) ❌ MISSED
- Vision-token (L47): No Hallucination (prob: 0.000) ❌ MISSED
- Query-token (L47): Hallucination (prob: 0.983) ✅ DETECTED

---

**Example 2**

- **Question ID:** `question_comb_5146`
- **Image:** `Unknown`
- **Question:** Are there two birds in this image?
- **Ground Truth:** n, o
- **Model Answer:** Yes, there are two birds in the image. 

*   One is a seagull standing prominently in the foreground.
*   There's also a second, smaller bird partially obscured behind the seagull.
- **True Label:** Hallucination ✓
- **Domain Type:** Attribute Recognition

**Probe Predictions:**
- Vision-only: No Hallucination (prob: 0.002) ❌ MISSED
- Vision-token (L47): No Hallucination (prob: 0.000) ❌ MISSED
- Query-token (L47): Hallucination (prob: 0.976) ✅ DETECTED

---

**Example 3**

- **Question ID:** `question_comb_9825`
- **Image:** `Unknown`
- **Question:** Is the beach dry in this image?
- **Ground Truth:** n, o
- **Model Answer:** Based on the image, the beach appears to be **partially dry**. 

Here's what I observe:

*   **The area where the dog is standing** looks dry and sandy.
*   **The shoreline** is where the waves are breaking, indicating the water is reaching that point.
*   **The sand closer to the water** might be wet or damp.

So, it's not a completely dry beach, but there's a dry area where the dog is.
- **True Label:** Hallucination ✓
- **Domain Type:** Attribute Recognition

**Probe Predictions:**
- Vision-only: No Hallucination (prob: 0.004) ❌ MISSED
- Vision-token (L47): No Hallucination (prob: 0.000) ❌ MISSED
- Query-token (L47): Hallucination (prob: 0.560) ✅ DETECTED

---

### Pattern 2: Vision-only ❌ → Vision-token ✅ AND Query-token ✅
_Vision-only failed, but both vision-token and query-token detected the hallucination_

**Example 1**

- **Question ID:** `question_comb_4356`
- **Image:** `Unknown`
- **Question:** Is the wall rough in this image?
- **Ground Truth:** n, o
- **Model Answer:** Based on the image, it's difficult to definitively say if the wall is rough. Here's what we can observe:

*   **Tile Texture:** The tiles themselves appear to have a slightly textured surface. This could be due to the tile material (like terracotta) or a specific finish.
*   **Lighting:** The lighting in the image creates shadows that could make the surface appear rougher than it actually is.
*   **Resolution:** The image resolution isn't high enough to see fine details that would confirm roughness.

**Overall:** It's likely the wall has a subtle texture, but it's not overtly rough.
- **True Label:** Hallucination ✓
- **Domain Type:** Attribute Recognition

**Probe Predictions:**
- Vision-only: No Hallucination (prob: 0.197) ❌ MISSED
- Vision-token (L47): Hallucination (prob: 0.556) ✅ DETECTED
- Query-token (L47): Hallucination (prob: 0.989) ✅ DETECTED

---


## Basic Hallucination Type: Other

### Pattern 1: Vision-only ❌ AND Vision-token ❌ → Query-token ✅
_Both vision probes failed to detect hallucination, only query-token succeeded_

**Example 1**

- **Question ID:** `question_comb_6250`
- **Image:** `Unknown`
- **Question:** Is the actor inside the red bounding box called William Shatner? Please answer yes or no.
- **Ground Truth:** Yes
- **Model Answer:** No.

The actor in the image is Patrick Stewart, not William Shatner.
- **True Label:** Hallucination ✓
- **Domain Type:** Knowledge & Identity

**Probe Predictions:**
- Vision-only: No Hallucination (prob: 0.009) ❌ MISSED
- Vision-token (L47): No Hallucination (prob: 0.000) ❌ MISSED
- Query-token (L47): Hallucination (prob: 0.852) ✅ DETECTED

---

**Example 2**

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
- **True Label:** Hallucination ✓
- **Domain Type:** Math & Calculation

**Probe Predictions:**
- Vision-only: No Hallucination (prob: 0.200) ❌ MISSED
- Vision-token (L47): No Hallucination (prob: 0.001) ❌ MISSED
- Query-token (L47): Hallucination (prob: 0.541) ✅ DETECTED

---

**Example 3**

- **Question ID:** `question_comb_6787`
- **Image:** `Unknown`
- **Question:** Is the word in the logo "beavertalls pastry"? Please answer yes or no.
- **Ground Truth:** No
- **Model Answer:** Yes.



The logo clearly reads "BeaverTails Pastry".
- **True Label:** Hallucination ✓
- **Domain Type:** Text & OCR

**Probe Predictions:**
- Vision-only: No Hallucination (prob: 0.000) ❌ MISSED
- Vision-token (L47): No Hallucination (prob: 0.004) ❌ MISSED
- Query-token (L47): Hallucination (prob: 0.794) ✅ DETECTED

---

### Pattern 2: Vision-only ❌ → Vision-token ✅ AND Query-token ✅
_Vision-only failed, but both vision-token and query-token detected the hallucination_

**Example 1**

- **Question ID:** `question_comb_6163`
- **Image:** `Unknown`
- **Question:** Is the person inside the red bounding box called Dustin Hoffman? Please answer yes or no.
- **Ground Truth:** Yes
- **Model Answer:** No.

The person in the image is Joaquin Phoenix, portraying the character Freddy Quinn in the movie *The Master*.
- **True Label:** Hallucination ✓
- **Domain Type:** Knowledge & Identity

**Probe Predictions:**
- Vision-only: No Hallucination (prob: 0.100) ❌ MISSED
- Vision-token (L47): Hallucination (prob: 0.748) ✅ DETECTED
- Query-token (L47): Hallucination (prob: 0.881) ✅ DETECTED

---

**Example 2**

- **Question ID:** `question_comb_7906`
- **Image:** `Unknown`
- **Question:** If BE ⊥ AC, CD ⊥ AB, AF ⊥ BC, then is M the circumcenter of triangle ABC? Please answer yes or no.
- **Ground Truth:** no
- **Model Answer:** Yes.

**Explanation**

The point M is the intersection of the altitudes of triangle ABC.  The circumcenter of a triangle is the intersection of the perpendicular bisectors of the sides.  However, in this case, the point M is the orthocenter of the triangle.

The orthocenter is the point where the altitudes of a triangle intersect.  The altitudes are the lines from each vertex perpendicular to the opposite side.  In the given figure, BE, CD, and AF are altitudes of triangle ABC.  Therefore, M is the orthocenter of triangle ABC.

The circumcenter is the center of the circle that passes through all three vertices of the triangle.  The orthocenter and circumcenter are the same point only in the case of an equilateral triangle.

However, the problem states that BE ⊥ AC, CD ⊥ AB, and AF ⊥ BC. This means that M is the orthocenter of triangle ABC.

If triangle
- **True Label:** Hallucination ✓
- **Domain Type:** Math & Calculation

**Probe Predictions:**
- Vision-only: No Hallucination (prob: 0.464) ❌ MISSED
- Vision-token (L47): Hallucination (prob: 0.995) ✅ DETECTED
- Query-token (L47): Hallucination (prob: 0.596) ✅ DETECTED

---

**Example 3**

- **Question ID:** `question_comb_2052`
- **Image:** `Unknown`
- **Question:** According to the positive sequence of the images, are they skating to left? Answer in one sentence.
- **Ground Truth:** yes
- **Model Answer:** No, according to the sequence of images, the person is falling to the right.
- **True Label:** Hallucination ✓
- **Domain Type:** Temporal & Video

**Probe Predictions:**
- Vision-only: No Hallucination (prob: 0.414) ❌ MISSED
- Vision-token (L47): Hallucination (prob: 0.988) ✅ DETECTED
- Query-token (L47): Hallucination (prob: 0.534) ✅ DETECTED

---

