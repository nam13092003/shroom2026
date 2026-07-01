import os
import json
import torch
import pytest
from datasets.alignment import char_to_token_align, reconstruct_spans
from datasets.shroom_dataset import (
    ShroomVisionsDataset,
    ShroomVisionsCollator,
    get_char_probabilities,
    get_char_categories
)

class MockTokenizer:
    def __init__(self):
        self.pad_token_id = 0
        
    def __call__(self, text, return_offsets_mapping=True, **kwargs):
        # simple word tokenization
        words = text.split()
        input_ids = []
        offset_mapping = []
        curr = 0
        for i, word in enumerate(words):
            # Find the actual start index in the original text
            start = text.find(word, curr)
            end = start + len(word)
            input_ids.append(i + 100)
            offset_mapping.append((start, end))
            curr = end
        return {
            'input_ids': input_ids,
            'offset_mapping': offset_mapping
        }

def test_char_to_token_align():
    original_text = "The quick brown fox jumps over the lazy dog"
    # Words: The, quick, brown, fox, jumps, over, the, lazy, dog
    # Character spans:
    # "quick" starts at 4, ends at 9
    # "lazy dog" starts at 35, ends at 43
    tokenizer = MockTokenizer()
    encoding = tokenizer(original_text)
    offsets = encoding['offset_mapping']
    
    char_spans = [(4, 9), (35, 43)]
    bio_tags = char_to_token_align(original_text, offsets, char_spans)
    
    # Expected tags:
    # 'The' -> 'O'
    # 'quick' -> 'B' (overlaps (4,9))
    # 'brown' -> 'O'
    # 'fox' -> 'O'
    # 'jumps' -> 'O'
    # 'over' -> 'O'
    # 'the' -> 'O'
    # 'lazy' -> 'B' (overlaps (35,43))
    # 'dog' -> 'I' (overlaps (35,43))
    
    assert bio_tags[0] == 'O'
    assert bio_tags[1] == 'B'
    assert bio_tags[2] == 'O'
    assert bio_tags[7] == 'B'
    assert bio_tags[8] == 'I'

def test_reconstruct_spans():
    tokenized_offsets = [(0, 3), (4, 9), (10, 15), (16, 19), (20, 25), (26, 30), (31, 34), (35, 39), (40, 43)]
    bio_tags = ['O', 'B', 'O', 'O', 'O', 'O', 'O', 'B', 'I']
    
    spans = reconstruct_spans(bio_tags, tokenized_offsets)
    assert len(spans) == 2
    assert spans[0] == (4, 9)
    assert spans[1] == (35, 43)

def test_dataset_and_collator(tmp_path):
    # Create a mock jsonl dataset file
    jsonl_data = [
        {
            "id": "train-1",
            "split": "train",
            "language": "en",
            "prompt": "Identify objects",
            "image_name": "image1.jpg",
            "response": "The cat sat on the mat",
            "labels": [
                {"start": 4, "end": 7, "prob": 0.66666, "label": "invention"},
                {"start": 19, "end": 22, "prob": 0.33333, "label": "mischaracterization"}
            ]
        },
        {
            "id": "train-2",
            "split": "train",
            "language": "en",
            "prompt": "Count objects",
            "image_name": "image2.jpg",
            "response": "Three birds fly",
            "labels": [
                {"start": 0, "end": 5, "prob": 1.0, "label": "miscounting"}
            ]
        }
    ]
    
    jsonl_file = tmp_path / "train_mock.jsonl"
    with open(jsonl_file, "w", encoding="utf-8") as f:
        for item in jsonl_data:
            f.write(json.dumps(item) + "\n")
            
    tokenizer = MockTokenizer()
    dataset = ShroomVisionsDataset(
        jsonl_path=str(jsonl_file),
        images_dir=str(tmp_path),
        tokenizer=tokenizer
    )
    
    assert len(dataset) == 2
    
    # Check item 0
    item = dataset[0]
    assert item['id'] == "train-1"
    # response words: "The" (0,3), "cat" (4,7), "sat" (8,11), "on" (12,14), "the" (15,18), "mat" (19,22)
    # labels: cat (4,7) -> bio B (1), prob 0.66666, cat 0
    # mat (19,22) -> bio B (1), prob 0.33333, cat 1
    assert item['bio_tags'][1].item() == 1  # 'cat' -> B
    assert item['bio_tags'][5].item() == 1  # 'mat' -> B
    assert abs(item['probabilities'][1].item() - 0.66666) < 1e-4
    assert item['categories'][1].item() == 0  # 'invention'
    assert item['categories'][5].item() == 1  # 'mischaracterization'
    
    # Check collator
    collator = ShroomVisionsCollator(pad_token_id=0)
    batch = [dataset[0], dataset[1]]
    collated = collator(batch)
    
    assert collated['input_ids'].shape[0] == 2
    assert collated['bio_tags'].shape[0] == 2
    assert collated['categories'].shape[0] == 2
    assert collated['probabilities'].shape[0] == 2
    
    # Check padding of shorter sequence
    # train-1: "The cat sat on the mat" -> 6 tokens
    # train-2: "Three birds fly" -> 3 tokens
    assert collated['input_ids'][1, 3].item() == 0  # padding token
    assert collated['bio_tags'][1, 3].item() == -100  # padding label
    assert collated['categories'][1, 3].item() == -100
    assert collated['probabilities'][1, 3].item() == -100.0
