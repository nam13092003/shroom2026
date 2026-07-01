import os
import json
import h5py
import torch
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
from torch.utils.data import Dataset
from PIL import Image

from datasets.alignment import char_to_token_align

# Category mapping
CATEGORY_MAP = {
    "invention": 0,
    "mischaracterization": 1,
    "ocr problem": 2,
    "ocr_problem": 2,
    "miscounting": 3,
    "other": 4
}
INV_CATEGORY_MAP = {v: k for k, v in CATEGORY_MAP.items()}

def get_char_probabilities(response_len: int, labels: List[Dict[str, Any]]) -> List[float]:
    """Calculate empirical hallucination probability for every character in the response."""
    probs = [0.0] * response_len
    for label in labels:
        start = label['start']
        end = label['end']
        prob = float(label.get('prob', 1.0))
        for i in range(start, min(end, response_len)):
            probs[i] = max(probs[i], prob)
    return probs

def get_char_categories(response_len: int, labels: List[Dict[str, Any]]) -> List[int]:
    """Map every character in the response to its hallucination category index (-1 if none)."""
    categories = [-1] * response_len
    for label in labels:
        start = label['start']
        end = label['end']
        cat_str = label.get('label', 'other').lower()
        cat_idx = CATEGORY_MAP.get(cat_str, 4)
        for i in range(start, min(end, response_len)):
            categories[i] = cat_idx
    return categories

class ShroomVisionsDataset(Dataset):
    """
    SHROOM-Vision 2026 Multitask Dataset.
    Supports on-the-fly extraction using Qwen2.5-VL or loading cached features from HDF5.
    """
    def __init__(
        self,
        jsonl_path: str,
        images_dir: str,
        tokenizer: Any,
        processor: Optional[Any] = None,
        cache_dir: Optional[str] = None,
        max_length: int = 1024,
        is_training: bool = True
    ):
        self.jsonl_path = jsonl_path
        self.images_dir = images_dir
        self.tokenizer = tokenizer
        self.processor = processor
        self.cache_dir = cache_dir
        self.max_length = max_length
        self.is_training = is_training
        
        # Load samples
        self.samples = []
        with open(jsonl_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    self.samples.append(json.loads(line))
                    
        # Verify cache directory
        if self.cache_dir:
            os.makedirs(self.cache_dir, exist_ok=True)

    def __len__(self) -> int:
        return len(self.samples)

    def _get_cached_features(self, sample_id: str) -> Optional[Dict[str, Any]]:
        """Attempt to load features from cached HDF5 file."""
        if not self.cache_dir:
            return None
        cache_path = os.path.join(self.cache_dir, f"{sample_id}.h5")
        if not os.path.exists(cache_path):
            return None
            
        try:
            features = {}
            with h5py.File(cache_path, 'r') as f:
                features['vision_features'] = torch.tensor(f['vision_features'][:])
                features['decoder_hidden_states'] = torch.tensor(f['decoder_hidden_states'][:])
                features['query_hidden_states'] = torch.tensor(f['query_hidden_states'][:])
                features['cross_attention'] = torch.tensor(f['cross_attention'][:])
                if 'grounding_features' in f:
                    features['grounding_features'] = torch.tensor(f['grounding_features'][:])
            return features
        except Exception as e:
            print(f"Error reading cache for {sample_id}: {e}")
            return None

    def _write_cached_features(self, sample_id: str, features: Dict[str, Any]):
        """Save extracted features to HDF5 cache."""
        if not self.cache_dir:
            return
        cache_path = os.path.join(self.cache_dir, f"{sample_id}.h5")
        try:
            with h5py.File(cache_path, 'w') as f:
                f.create_dataset('vision_features', data=features['vision_features'].cpu().numpy())
                f.create_dataset('decoder_hidden_states', data=features['decoder_hidden_states'].cpu().numpy())
                f.create_dataset('query_hidden_states', data=features['query_hidden_states'].cpu().numpy())
                f.create_dataset('cross_attention', data=features['cross_attention'].cpu().numpy())
                if 'grounding_features' in features:
                    f.create_dataset('grounding_features', data=features['grounding_features'].cpu().numpy())
        except Exception as e:
            print(f"Error writing cache for {sample_id}: {e}")

    def __getitem__(self, idx: int) -> Dict[str, Any]:
        sample = self.samples[idx]
        sample_id = sample['id']
        prompt = sample['prompt']
        response = sample['response']
        image_name = sample['image_name']
        labels = sample.get('labels', [])
        
        # 1. Look for cached features
        features = self._get_cached_features(sample_id)
        
        # 2. Tokenize response and get offset mappings
        # We need the response offsets to perform character-to-token alignment
        encoding = self.tokenizer(
            response,
            return_offsets_mapping=True,
            add_special_tokens=False,
            max_length=self.max_length,
            truncation=True
        )
        
        input_ids = encoding['input_ids']
        offsets = encoding['offset_mapping']
        
        # 3. Create target labels
        response_len = len(response)
        char_probs = get_char_probabilities(response_len, labels)
        char_cats = get_char_categories(response_len, labels)
        
        # Convert character spans to list of (start, end) tuples
        char_spans = [(label['start'], label['end']) for label in labels]
        
        # BIO Alignment
        bio_tag_strs = char_to_token_align(response, offsets, char_spans)
        
        # Map BIO tags to indices (O=0, B=1, I=2)
        tag_map = {'O': 0, 'B': 1, 'I': 2}
        bio_tags = [tag_map[t] for t in bio_tag_strs]
        
        # Assign token-level categories and probabilities
        token_categories = []
        token_probs = []
        
        for start_idx, end_idx in offsets:
            if start_idx == 0 and end_idx == 0:
                token_categories.append(-100)
                token_probs.append(0.0)
                continue
                
            # Token probability is max character probability inside the token boundary
            tok_prob = max(char_probs[start_idx:end_idx]) if start_idx < end_idx else 0.0
            token_probs.append(tok_prob)
            
            # Token category is the dominant category inside the token boundary
            # If the token is O, it has no category (-100)
            sub_cats = [c for c in char_cats[start_idx:end_idx] if c != -1]
            if sub_cats:
                # Assign the most common non-empty category
                from collections import Counter
                tok_cat = Counter(sub_cats).most_common(1)[0][0]
            else:
                tok_cat = -100
                
            token_categories.append(tok_cat)
            
        # Is the sequence hallucinated overall? (Sequence-level risk target)
        seq_label = 1 if len(char_spans) > 0 else 0
        
        item = {
            'id': sample_id,
            'prompt': prompt,
            'response': response,
            'image_name': image_name,
            'input_ids': torch.tensor(input_ids, dtype=torch.long),
            'offsets': offsets,
            'bio_tags': torch.tensor(bio_tags, dtype=torch.long),
            'categories': torch.tensor(token_categories, dtype=torch.long),
            'probabilities': torch.tensor(token_probs, dtype=torch.float),
            'seq_label': torch.tensor(seq_label, dtype=torch.float)
        }
        
        if features is not None:
            item.update(features)
            
        return item

class ShroomVisionsCollator:
    """Collates and pads dynamic sequence elements for multitask modeling."""
    def __init__(self, pad_token_id: int):
        self.pad_token_id = pad_token_id

    def __call__(self, batch: List[Dict[str, Any]]) -> Dict[str, Any]:
        ids = [item['id'] for item in batch]
        prompts = [item['prompt'] for item in batch]
        responses = [item['response'] for item in batch]
        image_names = [item['image_name'] for item in batch]
        offsets = [item['offsets'] for item in batch]
        
        # Pad token ids, bio tags, categories, probabilities
        input_ids = [item['input_ids'] for item in batch]
        bio_tags = [item['bio_tags'] for item in batch]
        categories = [item['categories'] for item in batch]
        probabilities = [item['probabilities'] for item in batch]
        seq_labels = torch.stack([item['seq_label'] for item in batch])
        
        # Compute lengths
        lengths = [len(x) for x in input_ids]
        max_len = max(lengths)
        
        # Perform padding
        padded_input_ids = torch.full((len(batch), max_len), self.pad_token_id, dtype=torch.long)
        padded_bio_tags = torch.full((len(batch), max_len), -100, dtype=torch.long)
        padded_categories = torch.full((len(batch), max_len), -100, dtype=torch.long)
        padded_probabilities = torch.full((len(batch), max_len), -100.0, dtype=torch.float)
        attention_mask = torch.zeros((len(batch), max_len), dtype=torch.long)
        
        for i, length in enumerate(lengths):
            padded_input_ids[i, :length] = input_ids[i]
            padded_bio_tags[i, :length] = bio_tags[i]
            padded_categories[i, :length] = categories[i]
            padded_probabilities[i, :length] = probabilities[i]
            attention_mask[i, :length] = 1
            
        collated = {
            'ids': ids,
            'prompts': prompts,
            'responses': responses,
            'image_names': image_names,
            'offsets': offsets,
            'input_ids': padded_input_ids,
            'bio_tags': padded_bio_tags,
            'categories': padded_categories,
            'probabilities': padded_probabilities,
            'attention_mask': attention_mask,
            'seq_labels': seq_labels
        }
        
        # Process cached VLM features if present in the first item of the batch
        if 'vision_features' in batch[0]:
            # Vision features are sequence of patches [num_patches, d_vision]
            # Since patches count can vary slightly per image resolution, pad them if necessary
            v_feats = [item['vision_features'] for item in batch]
            v_lens = [x.size(0) for x in v_feats]
            max_v_len = max(v_lens)
            d_vision = v_feats[0].size(1)
            
            padded_v_feats = torch.zeros((len(batch), max_v_len, d_vision), dtype=v_feats[0].dtype)
            v_mask = torch.zeros((len(batch), max_v_len), dtype=torch.long)
            for i, length in enumerate(v_lens):
                padded_v_feats[i, :length] = v_feats[i]
                v_mask[i, :length] = 1
                
            collated['vision_features'] = padded_v_feats
            collated['vision_mask'] = v_mask
            
        if 'decoder_hidden_states' in batch[0]:
            # Decoder hidden states are sequence-level representations [seq_len, d_hidden]
            dec_states = [item['decoder_hidden_states'] for item in batch]
            d_hidden = dec_states[0].size(1)
            padded_dec_states = torch.zeros((len(batch), max_len, d_hidden), dtype=dec_states[0].dtype)
            for i, length in enumerate(lengths):
                # Ensure we match lengths (in case cached hidden states are longer/shorter)
                curr_len = min(length, dec_states[i].size(0))
                padded_dec_states[i, :curr_len] = dec_states[i][:curr_len]
            collated['decoder_hidden_states'] = padded_dec_states
            
        if 'query_hidden_states' in batch[0]:
            # Query hidden states are global sequence embeddings [d_hidden]
            collated['query_hidden_states'] = torch.stack([item['query_hidden_states'] for item in batch])
            
        if 'cross_attention' in batch[0]:
            # Cross attention maps [max_len, max_v_len]
            attns = [item['cross_attention'] for item in batch]
            max_v_len = collated['vision_features'].size(1) if 'vision_features' in collated else attns[0].size(1)
            padded_attns = torch.zeros((len(batch), max_len, max_v_len), dtype=attns[0].dtype)
            for i, length in enumerate(lengths):
                curr_len = min(length, attns[i].size(0))
                curr_v_len = min(max_v_len, attns[i].size(1))
                padded_attns[i, :curr_len, :curr_v_len] = attns[i][:curr_len, :curr_v_len]
            collated['cross_attention'] = padded_attns
            
        if 'grounding_features' in batch[0]:
            gr_feats = [item['grounding_features'] for item in batch]
            d_gr = gr_feats[0].size(1)
            padded_gr = torch.zeros((len(batch), max_len, d_gr), dtype=gr_feats[0].dtype)
            for i, length in enumerate(lengths):
                curr_len = min(length, gr_feats[i].size(0))
                padded_gr[i, :curr_len] = gr_feats[i][:curr_len]
            collated['grounding_features'] = padded_gr
            
        return collated
