#!/usr/bin/env python3
"""
SmolVLM2 2.2B VQA Embedding Extractor
Multimodal vision-language model

Extracts embeddings for HALP (Hallucination Prediction via Probing):
1. Vision representation (from vision encoder)
2. Vision token representation (at image token boundary in decoder layers)
3. Query token representation (at query token boundary in decoder layers)
"""

import os
import argparse
import h5py
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
from PIL import Image
from datetime import datetime

import torch
from transformers import AutoProcessor, AutoModelForImageTextToText
from tqdm import tqdm
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class SmolVLMExtractorGPU:
    """SmolVLM2 2.2B multimodal extractor optimized for GPU"""

    def __init__(self, model_path: str = "HuggingFaceTB/SmolVLM2-2.2B-Instruct", cache_dir: str = "./model_cache"):
        """Initialize SmolVLM2 2.2B extractor"""
        self.model_path = model_path
        self.cache_dir = cache_dir

        # Verify CUDA is available
        if not torch.cuda.is_available():
            raise RuntimeError("CUDA is not available. This script requires GPU with CUDA.")

        logger.info(f"CUDA Device: {torch.cuda.get_device_name(0)}")
        logger.info(f"CUDA Memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.2f} GB")

        self._load_model()

    def _load_model(self):
        """Load SmolVLM2 2.2B model and processor"""
        logger.info(f"Loading SmolVLM2 2.2B model: {self.model_path}")

        # Load processor
        self.processor = AutoProcessor.from_pretrained(
            self.model_path,
            cache_dir=self.cache_dir,
            trust_remote_code=True
        )

        # Load model with float32 for compatibility
        self.model = AutoModelForImageTextToText.from_pretrained(
            self.model_path,
            cache_dir=self.cache_dir,
            trust_remote_code=True,
            torch_dtype=torch.float32,
            device_map='cuda'
        )
        self.model.eval()

        # Detect model architecture
        self._detect_architecture()

    def _detect_architecture(self):
        """Detect SmolVLM architecture components"""
        # Get text (language) model info
        if hasattr(self.model.config, 'text_config'):
            text_config = self.model.config.text_config
            self.num_layers = getattr(text_config, 'num_hidden_layers', None)
            self.text_hidden_size = getattr(text_config, 'hidden_size', None)
            logger.info(f"Detected {self.num_layers} text layers, hidden size: {self.text_hidden_size}")
        else:
            logger.warning("Text config not found")
            self.num_layers = 0

        # Get vision model info
        if hasattr(self.model.config, 'vision_config'):
            vision_config = self.model.config.vision_config
            self.vision_layers = getattr(vision_config, 'num_hidden_layers', None)
            self.vision_hidden_size = getattr(vision_config, 'hidden_size', None)
            logger.info(f"Detected {self.vision_layers} vision layers, hidden size: {self.vision_hidden_size}")
        else:
            logger.warning("Vision config not found")

    def _get_target_layers(self) -> List[int]:
        """Get target layer indices: 0, n/4, n/2, 3n/4, n-1"""
        if self.num_layers < 5:
            return list(range(self.num_layers))

        indices = [
            0,
            self.num_layers // 4,
            self.num_layers // 2,
            (3 * self.num_layers) // 4,
            self.num_layers - 1
        ]

        # Remove duplicates and sort
        return sorted(list(set(indices)))

    def _safe_tensor_to_numpy(self, tensor, name="tensor"):
        """Safely convert tensor to numpy array, handling BFloat16 and other dtypes."""
        try:
            if tensor.dtype == torch.bfloat16:
                tensor = tensor.float()
            return tensor.detach().cpu().numpy()
        except Exception as e:
            logger.warning(f"Could not convert {name} to numpy: {e}")
            return None

    def _estimate_vision_token_count(self, sequence_length: int) -> int:
        """Estimate the number of vision tokens in the sequence."""
        # For SmolVLM, vision tokens are typically at the beginning
        # Conservative estimate: vision tokens are roughly 10-30% of sequence
        # but usually between 200-800 tokens
        estimated_vision_tokens = min(
            max(200, sequence_length // 4),
            800
        )
        return estimated_vision_tokens

    def _find_token_boundaries(self, input_ids: torch.Tensor) -> Tuple[int, int]:
        """Find image and query token boundaries

        Returns:
            vision_token_boundary: Index of last image token (before query tokens start)
            query_token_boundary: Index of last query token (end of sequence)
        """
        try:
            sequence_length = input_ids.shape[1] if input_ids.dim() > 1 else input_ids.shape[0]
            vision_token_count = self._estimate_vision_token_count(sequence_length)

            # Image tokens are at the beginning, so image_end_pos is after vision tokens
            vision_token_boundary = min(vision_token_count, sequence_length - 10)
            vision_token_boundary = max(1, min(vision_token_boundary, sequence_length - 2))

            # Query end is the last token before generation
            query_token_boundary = sequence_length - 1
            query_token_boundary = max(vision_token_boundary + 1, min(query_token_boundary, sequence_length - 1))

            logger.info(f"Token boundaries - Vision (last img token): {vision_token_boundary}, Query (last token): {query_token_boundary}")
            return vision_token_boundary, query_token_boundary

        except Exception as e:
            logger.warning(f"Boundary detection failed: {e}, using fallback")
            sequence_length = input_ids.shape[1] if input_ids.dim() > 1 else input_ids.shape[0]
            return min(255, sequence_length // 3), sequence_length - 1

    def extract_embeddings(self, image: Image.Image, question: str) -> Dict:
        """Extract all embeddings for a VQA pair

        Returns dictionary with:
            - vision_only_representation: From vision encoder
            - vision_token_representation: At last image token in decoder layers
            - query_token_representation: At last query token in decoder layers
            - answer: Generated answer
        """

        target_layers = self._get_target_layers()
        logger.info(f"Target layers: {target_layers}")

        # Step 1: Extract vision-only representation
        vision_only_rep = self._extract_vision_representation(image)

        # Step 2: Format input with chat template
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "image", "image": image},
                    {"type": "text", "text": question}
                ]
            }
        ]

        inputs = self.processor.apply_chat_template(
            messages,
            add_generation_prompt=True,
            tokenize=True,
            return_dict=True,
            return_tensors="pt"
        )
        inputs = {k: v.to('cuda') for k, v in inputs.items()}

        # Step 3: Generate answer
        generated_text = self._generate_answer(inputs)

        # Step 4: Extract decoder embeddings at token boundaries
        vision_token_reps, query_token_reps = self._extract_decoder_embeddings(
            inputs, target_layers
        )

        return {
            'vision_only_representation': vision_only_rep,
            'vision_token_representation': vision_token_reps,
            'query_token_representation': query_token_reps,
            'answer': generated_text
        }

    def _generate_answer(self, inputs: Dict) -> str:
        """Generate answer using SmolVLM"""
        try:
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=100,
                    do_sample=False
                )

            generated_text = self.processor.batch_decode(outputs, skip_special_tokens=True)[0]
            return generated_text

        except Exception as e:
            logger.error(f"Generation failed: {e}")
            return f"[Generation failed: {str(e)}]"

    def _extract_vision_representation(self, image: Image.Image) -> Optional[np.ndarray]:
        """Extract vision encoder representation (pooled)"""
        try:
            # Process image through vision encoder
            image_inputs = self.processor.image_processor(image, return_tensors="pt").to('cuda')
            pixel_values = image_inputs['pixel_values'].view(-1, 3, 384, 384)
            pixel_values = pixel_values.to(dtype=torch.float32)

            with torch.no_grad():
                vision_outputs = self.model.model.vision_model(
                    pixel_values=pixel_values,
                    output_hidden_states=True,
                    return_dict=True
                )

            vision_hidden_states = vision_outputs.hidden_states

            # Get final layer hidden states
            # Expected shape: [batch_size * num_images, num_patches, hidden_size]
            final_hidden = vision_hidden_states[-1]

            # Average across all dimensions except the last (hidden_size)
            # This handles variable batch/patch dimensions properly
            pooled_vision = final_hidden.mean(dim=tuple(range(final_hidden.dim() - 1)))

            # Should now be [hidden_size]
            return self._safe_tensor_to_numpy(pooled_vision, "pooled_vision")

        except Exception as e:
            logger.error(f"Vision extraction failed: {e}")
            return None

    def _extract_decoder_embeddings(self, inputs: Dict, target_layers: List[int]) -> Tuple:
        """Extract embeddings from decoder layers at token boundaries

        Returns:
            vision_token_reps: Representations at last image token
            query_token_reps: Representations at last query token
        """

        # Forward pass to get hidden states
        try:
            with torch.no_grad():
                outputs = self.model(**inputs, output_hidden_states=True, return_dict=True)

            hidden_states = outputs.hidden_states

            # Find token boundaries
            vision_token_boundary, query_token_boundary = self._find_token_boundaries(inputs['input_ids'])

            # Extract embeddings at boundaries
            vision_token_reps = {}
            query_token_reps = {}

            for layer_idx in target_layers:
                if layer_idx < len(hidden_states):
                    layer_hidden = hidden_states[layer_idx]  # [batch, seq_len, hidden_dim]

                    # Vision token representation (at last image token)
                    if vision_token_boundary < layer_hidden.shape[1]:
                        vision_emb = layer_hidden[0, vision_token_boundary, :]
                        vision_token_reps[f'layer_{layer_idx}'] = self._safe_tensor_to_numpy(
                            vision_emb, f"layer_{layer_idx}_vision"
                        )

                    # Query token representation (at last query token)
                    if query_token_boundary < layer_hidden.shape[1]:
                        query_emb = layer_hidden[0, query_token_boundary, :]
                        query_token_reps[f'layer_{layer_idx}'] = self._safe_tensor_to_numpy(
                            query_emb, f"layer_{layer_idx}_query"
                        )

            return vision_token_reps, query_token_reps

        except Exception as e:
            logger.error(f"Decoder embedding extraction failed: {e}")
            return {}, {}

    def process_dataset(self,
                       vqa_csv_path: str,
                       images_dir: str,
                       output_dir: str,
                       checkpoint_interval: int = 1000,
                       test_mode: bool = False):
        """Process entire VQA dataset with checkpointing"""

        # Load dataset
        logger.info(f"Loading VQA dataset: {vqa_csv_path}")
        df = pd.read_csv(vqa_csv_path)

        if test_mode:
            logger.info("TEST MODE: Processing 3 random samples")
            df = df.sample(n=3, random_state=42)

        os.makedirs(output_dir, exist_ok=True)

        # Process samples
        current_batch = {}
        processed_count = 0

        failed_count = 0
        for idx, row in tqdm(df.iterrows(), total=len(df), desc="Processing VQA"):
            question_id = None
            try:
                question_id = row['question_id']
                # Support both 'image_id' and 'image_name' columns
                image_id = row.get('image_id') or row.get('image_name')
                question = str(row['question']) if pd.notna(row['question']) else ""
                # Support both 'answer' and 'gt_answer' columns - handle NaN/empty
                gt_answer = row.get('answer') or row.get('gt_answer') or row.get('ground_truth_answer')
                gt_answer = str(gt_answer) if pd.notna(gt_answer) and str(gt_answer).strip() else "N/A"

                # Load image
                image_path = os.path.join(images_dir, image_id)
                if not os.path.exists(image_path):
                    logger.warning(f"❌ FAIL [{question_id}]: Image not found: {image_path}")
                    failed_count += 1
                    continue

                image = Image.open(image_path).convert('RGB')

                # Extract embeddings
                embeddings = self.extract_embeddings(image, question)

                # Store in batch
                current_batch[question_id] = {
                    'question': question,
                    'image_id': str(image_id),
                    'vision_only_representation': embeddings['vision_only_representation'],
                    'vision_token_representation': embeddings['vision_token_representation'],
                    'query_token_representation': embeddings['query_token_representation'],
                    'answer': str(embeddings['answer']),
                    'ground_truth_answer': gt_answer
                }

                processed_count += 1
                logger.info(f"✅ PASS [{question_id}]: Processed successfully ({processed_count}/{len(df)})")

                # Clear CUDA cache to prevent OOM errors
                torch.cuda.empty_cache()

                # Save checkpoint
                if processed_count % checkpoint_interval == 0:
                    self._save_checkpoint(current_batch, output_dir, processed_count // checkpoint_interval)
                    current_batch = {}
                    torch.cuda.empty_cache()
                    logger.info(f"💾 Checkpoint saved at {processed_count} samples")

            except Exception as e:
                failed_count += 1
                logger.error(f"❌ FAIL [{question_id}]: {e}")
                torch.cuda.empty_cache()
                continue

        # Save final batch
        if current_batch:
            final_part = (processed_count // checkpoint_interval) + 1
            self._save_checkpoint(current_batch, output_dir, final_part)
            logger.info(f"💾 Saved final checkpoint with {len(current_batch)} samples")

        logger.info(f"✅ Processing completed!")
        logger.info(f"   Total processed: {processed_count} samples")
        logger.info(f"   Total failed: {failed_count} samples")
        logger.info(f"   Success rate: {100 * processed_count / (processed_count + failed_count):.2f}%")

    def _save_checkpoint(self, batch_data: Dict, output_dir: str, part_num: int):
        """Save batch to HDF5 file

        Output structure per sample:
            question_id/
                image_id: str
                question: str
                ground_truth_answer: str
                vision_only_representation: [D]
                vision_token_representation/
                    layer_0: [D]
                    layer_n/4: [D]
                    layer_n/2: [D]
                    layer_3n/4: [D]
                    layer_n-1: [D]
                query_token_representation/
                    layer_0: [D]
                    layer_n/4: [D]
                    layer_n/2: [D]
                    layer_3n/4: [D]
                    layer_n-1: [D]
                answer: str
        """
        filename = f"smolvlm_2.2b_embeddings_part_{part_num:03d}.h5"
        filepath = os.path.join(output_dir, filename)

        with h5py.File(filepath, 'w') as f:
            # Metadata
            f.attrs['model_name'] = self.model_path
            f.attrs['model_type'] = 'smolvlm2-2.2b-multimodal'
            f.attrs['device'] = 'cuda'
            f.attrs['dtype'] = 'float32'
            f.attrs['created_at'] = datetime.now().isoformat()
            f.attrs['num_samples'] = len(batch_data)

            for question_id, data in batch_data.items():
                grp = f.create_group(str(question_id))

                # Store metadata strings
                grp.create_dataset('image_id', data=data['image_id'], dtype=h5py.string_dtype())
                grp.create_dataset('question', data=data['question'], dtype=h5py.string_dtype())
                grp.create_dataset('ground_truth_answer', data=data['ground_truth_answer'], dtype=h5py.string_dtype())

                # Store vision-only representation
                if data['vision_only_representation'] is not None:
                    grp.create_dataset('vision_only_representation',
                                     data=data['vision_only_representation'],
                                     compression='gzip')

                # Store vision token representations
                if data['vision_token_representation']:
                    rep_grp = grp.create_group('vision_token_representation')
                    for layer_name, embedding in data['vision_token_representation'].items():
                        if embedding is not None:
                            rep_grp.create_dataset(layer_name, data=embedding, compression='gzip')

                # Store query token representations
                if data['query_token_representation']:
                    rep_grp = grp.create_group('query_token_representation')
                    for layer_name, embedding in data['query_token_representation'].items():
                        if embedding is not None:
                            rep_grp.create_dataset(layer_name, data=embedding, compression='gzip')

                # Store generated answer
                grp.create_dataset('answer', data=data['answer'], dtype=h5py.string_dtype())

        logger.info(f"Saved {len(batch_data)} samples to {filepath}")


def main():
    parser = argparse.ArgumentParser(description="SmolVLM2 2.2B VQA Extractor")
    parser.add_argument('--vqa-dataset', required=True, help='Path to VQA CSV dataset')
    parser.add_argument('--images-dir', required=True, help='Directory containing images')
    parser.add_argument('--output-dir', default='./smolvlm_output', help='Output directory for embeddings')
    parser.add_argument('--model', default='HuggingFaceTB/SmolVLM2-2.2B-Instruct', help='Model path')
    parser.add_argument('--cache-dir', default='./model_cache', help='Model cache directory')
    parser.add_argument('--checkpoint-interval', type=int, default=1000, help='Save every N samples')
    parser.add_argument('--test', action='store_true', help='Test mode (3 samples)')

    args = parser.parse_args()

    # Initialize extractor
    logger.info("🚀 Initializing SmolVLM2 2.2B Extractor")
    extractor = SmolVLMExtractorGPU(model_path=args.model, cache_dir=args.cache_dir)

    # Process dataset
    logger.info(f"📊 Dataset: {args.vqa_dataset}")
    logger.info(f"🖼️  Images: {args.images_dir}")
    logger.info(f"💾 Output: {args.output_dir}")

    extractor.process_dataset(
        vqa_csv_path=args.vqa_dataset,
        images_dir=args.images_dir,
        output_dir=args.output_dir,
        checkpoint_interval=args.checkpoint_interval,
        test_mode=args.test
    )

    logger.info("✅ All done!")


if __name__ == "__main__":
    main()

