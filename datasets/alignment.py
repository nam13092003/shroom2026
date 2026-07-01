from typing import List, Tuple

def char_to_token_align(
    original_text: str,
    tokenized_offsets: List[Tuple[int, int]],
    char_spans: List[Tuple[int, int]]
) -> List[str]:
    """
    Align character-level hallucination spans to token-level BIO tags.
    
    Args:
        original_text: The original generated response text.
        tokenized_offsets: List of (start_char_idx, end_char_idx) for each token.
        char_spans: List of ground truth hallucination character spans (start_idx, end_idx).
                    Note: end_idx is exclusive (python slice style).
                    
    Returns:
        List of BIO tags ('B', 'I', 'O') matching the length of tokenized_offsets.
    """
    bio_tags = ['O'] * len(tokenized_offsets)
    
    # Sort spans to ensure chronological processing
    sorted_spans = sorted(char_spans, key=lambda x: x[0])
    
    for span_start, span_end in sorted_spans:
        # Keep track of whether we've started this span in the token sequence
        span_started = False
        
        for idx, (start_idx, end_idx) in enumerate(tokenized_offsets):
            # Skip special tokens (often represented by (0, 0) offset)
            if start_idx == 0 and end_idx == 0:
                continue
                
            # Check overlap
            overlap = max(start_idx, span_start) < min(end_idx, span_end)
            if overlap:
                if not span_started:
                    bio_tags[idx] = 'B'
                    span_started = True
                else:
                    bio_tags[idx] = 'I'
                    
    return bio_tags

def reconstruct_spans(
    token_bio_tags: List[str],
    tokenized_offsets: List[Tuple[int, int]]
) -> List[Tuple[int, int]]:
    """
    Reconstruct character-level spans from token-level BIO tags using offset mapping.
    
    Args:
        token_bio_tags: List of BIO tags ('B', 'I', 'O').
        tokenized_offsets: List of (start_char_idx, end_char_idx) for each token.
        
    Returns:
        List of character spans (start_idx, end_idx) where end_idx is exclusive.
    """
    spans = []
    active_span_start = None
    active_span_end = None
    
    for idx, tag in enumerate(token_bio_tags):
        start_idx, end_idx = tokenized_offsets[idx]
        
        # Skip special/padding tokens with zero offsets
        if start_idx == 0 and end_idx == 0:
            # If there was an active span, close it before skipping
            if active_span_start is not None:
                spans.append((active_span_start, active_span_end))
                active_span_start, active_span_end = None, None
            continue
            
        if tag == 'B':
            # Close existing active span if any
            if active_span_start is not None:
                spans.append((active_span_start, active_span_end))
            # Start new span
            active_span_start = start_idx
            active_span_end = end_idx
        elif tag == 'I':
            if active_span_start is not None:
                # Extend current span
                active_span_end = end_idx
            else:
                # Handle malformed 'I' without 'B': treat it as starting a span
                active_span_start = start_idx
                active_span_end = end_idx
        elif tag == 'O':
            # Close existing active span if any
            if active_span_start is not None:
                spans.append((active_span_start, active_span_end))
                active_span_start, active_span_end = None, None
                
    # Close final active span if it reached the end
    if active_span_start is not None:
        spans.append((active_span_start, active_span_end))
        
    # Merge overlapping or adjacent spans if necessary, and filter empty spans
    refined_spans = []
    for s_start, s_end in spans:
        if s_start >= s_end:
            continue
        if refined_spans and s_start <= refined_spans[-1][1]:
            # Overlap or contiguous, merge them
            prev_start, prev_end = refined_spans.pop()
            refined_spans.append((prev_start, max(prev_end, s_end)))
        else:
            refined_spans.append((s_start, s_end))
            
    return refined_spans
