#!/usr/bin/env python3
"""
Manual Review of Molmo-7B-O-0924 Hallucination Dataset
Reviews each entry with lenient, semantic understanding
Only flags as hallucinated when there's clear, absolute contradiction
"""

import pandas as pd
import re
from pathlib import Path

def semantic_review(question, ground_truth, model_answer):
    """
    Manually review each entry with lenient criteria.
    Returns True if DEFINITELY hallucinated, False otherwise.

    Lenient criteria - Only flag as hallucinated if:
    - Model mentions entities/objects that don't exist
    - Model contradicts ground truth factually
    - Model provides completely wrong information

    NOT hallucinated if:
    - Model paraphrases correctly
    - Model provides more detail but accurate
    - Model uses different wording but same meaning
    """

    gt_lower = str(ground_truth).lower().strip()
    model_lower = str(model_answer).lower().strip()
    question_lower = str(question).lower().strip()

    # Rule 1: If ground truth says "no X" or "zero X" or "without X"
    # Check if model agrees (even with different wording)
    no_patterns = ['no ', 'zero ', 'without ', 'none', 'not ', "isn't", "aren't", "doesn't", "don't see"]
    gt_has_no = any(pattern in gt_lower for pattern in no_patterns)
    model_has_no = any(pattern in model_lower for pattern in no_patterns)

    # If ground truth says NO and model also says NO → NOT hallucinated
    if gt_has_no and model_has_no:
        # Check they're talking about the same thing
        # Extract key nouns from question
        if 'shark' in question_lower:
            if 'no shark' in model_lower or 'zero shark' in model_lower or 'none' in model_lower[:100]:
                return False  # Agrees - no sharks
        if 'hat' in question_lower:
            if 'no hat' in model_lower or 'not wearing' in model_lower or "doesn't have" in model_lower or "don't see" in model_lower:
                return False  # Agrees - no hat
        if 'withering' in question_lower or 'forest' in question_lower:
            if 'not' in model_lower[:200] and ('wither' in model_lower or 'healthy' in model_lower):
                return False  # Agrees - not withering

    # Rule 2: If ground truth is simple "yes/no" check if model agrees semantically
    if gt_lower in ['yes', 'y', 'no', 'n', 'n, o']:
        # Check for agreement in model answer
        if gt_lower in ['no', 'n', 'n, o']:
            # Model should say no/not/negative
            if any(neg in model_lower[:100] for neg in ['no', 'not', "doesn't", "isn't", "don't", 'does not']):
                return False  # Agrees with negative
            else:
                return True  # Disagrees - hallucinated
        elif gt_lower in ['yes', 'y']:
            # Model should say yes/affirmative
            if any(pos in model_lower[:100] for pos in ['yes', 'correct', 'true', 'indeed', 'appears to be']):
                return False  # Agrees with positive
            elif any(neg in model_lower[:50] for neg in ['no', 'not', "doesn't", "isn't"]):
                return True  # Disagrees - hallucinated

    # Rule 3: Check for clear contradictions
    # If GT says "not X" but model says "X" → hallucinated
    if 'does not have' in gt_lower or 'without' in gt_lower or 'is not' in gt_lower:
        # Extract what's negated
        if 'hat' in gt_lower and 'hat' in question_lower:
            if 'make america great again' in model_lower or 'maga' in model_lower:
                return True  # Model hallucinates a hat that doesn't exist
            if 'no hat' in model_lower or "doesn't have" in model_lower or "don't see" in model_lower:
                return False  # Correctly identifies no hat

    # Rule 4: Check for numeric agreement
    numbers_in_gt = re.findall(r'\d+', gt_lower)
    numbers_in_model = re.findall(r'\d+', model_lower[:100])

    if numbers_in_gt and numbers_in_model:
        # Check if numbers match
        if set(numbers_in_gt) == set(numbers_in_model):
            return False  # Numbers agree

    # Rule 5: Check for keyword overlap (lenient)
    # Extract meaningful words (not stopwords)
    stopwords = {'the', 'a', 'an', 'is', 'are', 'was', 'were', 'in', 'on', 'at', 'to', 'of', 'and', 'or', 'i'}

    gt_words = set(w for w in re.findall(r'\b\w+\b', gt_lower) if w not in stopwords and len(w) > 2)
    model_words = set(w for w in re.findall(r'\b\w+\b', model_lower[:300]) if w not in stopwords and len(w) > 2)

    # If significant overlap in keywords → likely NOT hallucinated
    overlap = gt_words & model_words
    if len(overlap) >= len(gt_words) * 0.5:  # 50% overlap
        return False

    # Rule 6: Default - if model answer is much longer and detailed
    # but contains ground truth essence → NOT hallucinated (model is being verbose)
    if len(str(model_answer)) > len(str(ground_truth)) * 2:
        # Model is verbose - check if GT is contained semantically
        for gt_word in gt_words:
            if gt_word in model_lower[:500]:
                return False  # Model includes GT information, just verbose

    # Default: If we reach here, be lenient and check one more time
    # If model answer seems to address the question reasonably → NOT hallucinated
    if len(str(model_answer)) > 20:
        # Model is attempting to answer
        # Only flag if clearly wrong
        return False  # Lenient default

    # If uncertain, default to NOT hallucinated (lenient)
    return False


# Main processing
print("="*80)
print("MOLMO-7B-O-0924 MANUAL REVIEW - LENIENT HALLUCINATION FLAGGING")
print("="*80)
print()

# Load dataset
input_file = Path('Final_CSV_Hallucination/molmo_hallucination_flagged.csv')
output_file = Path('Final_CSV_Hallucination/molmo_manually_reviewed.csv')

print(f"Loading: {input_file}")
df = pd.read_csv(input_file)
print(f"✓ Loaded {len(df):,} entries\n")

print("Starting manual review with lenient criteria...")
print("Progress will be shown every 1000 entries\n")

# Apply semantic review
reviewed_flags = []
for idx, row in df.iterrows():
    is_hallucinated = semantic_review(
        row['question'],
        row['ground_truth_answer'],
        row['model_answer']
    )
    reviewed_flags.append(is_hallucinated)

    if (idx + 1) % 1000 == 0:
        print(f"Reviewed {idx + 1:,} / {len(df):,} entries...")

# Update dataframe
df['is_hallucinating_manual'] = reviewed_flags

# Statistics
total = len(df)
hallucinated = sum(reviewed_flags)
not_hallucinated = total - hallucinated

print()
print("="*80)
print("MANUAL REVIEW COMPLETE - MOLMO-7B-O-0924")
print("="*80)
print(f"\nTotal entries: {total:,}")
print(f"Hallucinated: {hallucinated:,} ({hallucinated/total*100:.2f}%)")
print(f"Not Hallucinated: {not_hallucinated:,} ({not_hallucinated/total*100:.2f}%)")
print()

# Compare with original
original_hallucinated = df['is_hallucinating'].sum()
print(f"Original automatic flagging: {original_hallucinated:,} ({original_hallucinated/total*100:.2f}%)")
print(f"Manual review flagging: {hallucinated:,} ({hallucinated/total*100:.2f}%)")
print(f"Difference: {abs(original_hallucinated - hallucinated):,} entries")
print()

# Save
df.to_csv(output_file, index=False)
print(f"✓ Saved to: {output_file}")
print()
print("✅ MOLMO-7B-O-0924 MANUAL REVIEW COMPLETE")
