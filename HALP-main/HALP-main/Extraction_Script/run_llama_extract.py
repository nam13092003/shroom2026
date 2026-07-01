#!/usr/bin/env python3
"""
Llama 3.2 Vision (11B) VQA Embedding Extractor
Extracts embeddings for HALP-style probing from a multimodal LLM:

1) Vision-only representation (from MllamaVision encoder, pooled)
2) Vision token representation (hidden state at <|image|> placeholder)
3) Query token representation (hidden state at end-of-prompt)
4) Generated answer

Layer sampling matches Gemma-3 script by percentage:
[0, n/4, n/2, 3n/4, n-1]
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
from transformers import AutoProcessor, MllamaForConditionalGeneration
from tqdm import tqdm
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class Llama32VisionExtractorGPU:
    """Llama 3.2 Vision extractor optimized for GPU with bfloat16"""

    def __init__(self, model_path: str = "meta-llama/Llama-3.2-11B-Vision-Instruct", cache_dir: str = "./model_cache"):
        self.model_path = model_path
        self.cache_dir = cache_dir

        if not torch.cuda.is_available():
            raise RuntimeError("CUDA is not available. This script requires a CUDA-capable GPU.")

        logger.info(f"CUDA Device: {torch.cuda.get_device_name(0)}")
        logger.info(f"CUDA Memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.2f} GB")

        self._load_model()

    def _load_model(self):
        """Load Llama 3.2 Vision model + processor"""
        logger.info(f"Loading Llama 3.2 Vision model: {self.model_path}")

        self.processor = AutoProcessor.from_pretrained(
            self.model_path,
            cache_dir=self.cache_dir
        )

        # Use SDPA attention, bfloat16 on GPU
        self.model = MllamaForConditionalGeneration.from_pretrained(
            self.model_path,
            cache_dir=self.cache_dir,
            torch_dtype=torch.bfloat16,
            device_map="cuda",
            attn_implementation="sdpa"
        )
        self.model.eval()

        # Detect # of text (decoder) layers
        self.num_layers = None
        try:
            # Preferred: read from config
            if hasattr(self.model.config, "text_config") and hasattr(self.model.config.text_config, "num_hidden_layers"):
                self.num_layers = int(self.model.config.text_config.num_hidden_layers)
        except Exception:
            pass

        if self.num_layers is None:
            # Fallback: do a tiny forward with output_hidden_states to infer it
            dummy = self.processor(text="<|image|>Test", images=Image.new("RGB", (4, 4)), return_tensors="pt").to(self.model.device)
            with torch.no_grad():
                out = self.model(**dummy, output_hidden_states=True, return_dict=True)
            # hidden_states = [embeddings] + [L layers]
            self.num_layers = len(out.hidden_states) - 1

        logger.info(f"Detected {self.num_layers} language model layers")

        # Cache image token id
        self.image_token_id = getattr(self.model.config, "image_token_index", None)
        if self.image_token_id is None:
            try:
                self.image_token_id = self.processor.tokenizer.convert_tokens_to_ids("<|image|>")
            except Exception:
                self.image_token_id = 128256  # documented default; best-effort fallback

        # Try to find a vision submodule for vision-only embedding
        self._vision_submodule = getattr(self.model, "vision_model", None)
        if self._vision_submodule is None:
            logger.warning("Did not find `vision_model` submodule; vision-only representation may be skipped.")

    def _target_layers(self) -> List[int]:
        # 0, n/4, n/2, 3n/4, n-1
        nl = self.num_layers
        return sorted(set([
            0,
            nl // 4,
            nl // 2,
            (3 * nl) // 4,
            nl - 1
        ]))

    def extract_embeddings(self, image: Image.Image, question: str) -> Dict:
        """Extract embeddings for a VQA pair."""

        # Build chat text, then feed images via processor (robust across versions)
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "image"},
                    {"type": "text", "text": question}
                ]
            }
        ]
        chat_text = self.processor.apply_chat_template(messages, add_generation_prompt=True)

        inputs = self.processor(
            text=chat_text,
            images=[image],
            return_tensors="pt"
        ).to(self.model.device)

        # 1) Generate answer
        generated_text = self._generate_answer(inputs)

        # 2) Vision-only representation (pooled vision encoder features)
        vision_only_rep = self._extract_vision_representation(image)

        # 3) Decoder embeddings at image/query boundaries from selected layers
        vision_token_reps, query_token_reps = self._extract_decoder_embeddings(inputs, self._target_layers())

        return {
            "vision_only_representation": vision_only_rep,
            "vision_token_representation": vision_token_reps,
            "query_token_representation": query_token_reps,
            "answer": generated_text
        }

    def _generate_answer(self, inputs: Dict) -> str:
        try:
            with torch.autocast(device_type="cuda", dtype=torch.bfloat16):
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=200,
                    do_sample=False
                )
            # Skip the prompt tokens
            gen_tokens = outputs[0, inputs["input_ids"].size(1):]
            text = self.processor.decode(gen_tokens, skip_special_tokens=True).strip()
            return text
        except Exception as e:
            logger.error(f"Generation failed: {e}")
            return f"[Generation failed: {str(e)}]"

    def _extract_vision_representation(self, image: Image.Image) -> Optional[np.ndarray]:
        """Vision encoder pooled vector BEFORE projector. Averages across tiles/sequence to a single vector."""
        try:
            if self._vision_submodule is None:
                return None

            vis_inputs = self.processor(images=[image], return_tensors="pt")
            vis_inputs = {k: v.to(self.model.device) for k, v in vis_inputs.items()}

            with torch.no_grad():
                vis_out = self._vision_submodule(**vis_inputs)

                # MllamaVisionModel returns last_hidden_state with shape:
                # [batch, num_images, num_tiles, seq_len, hidden_dim]
                if not hasattr(vis_out, 'last_hidden_state') or vis_out.last_hidden_state is None:
                    logger.warning("Vision model did not return last_hidden_state")
                    return None

                feats = vis_out.last_hidden_state
                # Pool across all dimensions except hidden_dim to get single vector
                # Average over: batch, num_images, num_tiles, seq_len -> [hidden_dim]
                while feats.dim() > 1:
                    feats = feats.mean(dim=0)

                # Convert to numpy
                rep = feats.to(torch.float32).cpu().numpy()
                return rep
        except Exception as e:
            logger.warning(f"Vision-only extraction failed: {e}")
            return None

    def _extract_decoder_embeddings(self, inputs: Dict, target_layers: List[int]) -> Tuple[Dict, Dict]:
        """Use a single forward pass with output_hidden_states to grab layer-wise states."""
        with torch.no_grad():
            outputs = self.model(**inputs, output_hidden_states=True, return_dict=True)

        hidden_states = outputs.hidden_states  # tuple: [embeddings] + [layer_0 ... layer_{n-1}]
        attn_mask = inputs.get("attention_mask", None)

        # Find boundaries
        input_ids = inputs["input_ids"][0]  # [seq]
        if input_ids.device.type != "cpu":
            input_ids = input_ids.cpu()

        # Position of last <|image|> token (if any). If none, we choose the first token.
        image_positions = (input_ids == self.image_token_id).nonzero(as_tuple=False).flatten()
        if image_positions.numel() > 0:
            vision_token_boundary = int(image_positions[-1].item())
        else:
            vision_token_boundary = 0

        # Last non-padded token index
        if attn_mask is not None:
            last_idx = int(attn_mask[0].sum().item()) - 1
        else:
            last_idx = int(inputs["input_ids"].shape[1] - 1)
        query_token_boundary = max(0, last_idx)

        logger.info(f"Token boundaries -> image: {vision_token_boundary}, query: {query_token_boundary}")

        # Build dicts { f'layer_{k}': vector }
        vision_token_reps, query_token_reps = {}, {}
        for k in target_layers:
            # hidden_states index offset: +1 because 0th is embeddings
            layer_h = hidden_states[k + 1][0]  # [seq, hidden]
            vt_vec = layer_h[vision_token_boundary].to(torch.float32).cpu().numpy()
            qt_vec = layer_h[query_token_boundary].to(torch.float32).cpu().numpy()
            vision_token_reps[f"layer_{k}"] = vt_vec
            query_token_reps[f"layer_{k}"] = qt_vec

        return vision_token_reps, query_token_reps

    def process_dataset(self,
                        vqa_csv_path: str,
                        images_dir: str,
                        output_dir: str,
                        checkpoint_interval: int = 1000,
                        test_mode: bool = False):
        """Process entire VQA dataset with checkpointing (same columns & HDF5 schema)."""
        logger.info(f"Loading VQA dataset: {vqa_csv_path}")
        df = pd.read_csv(vqa_csv_path)

        if test_mode:
            logger.info("TEST MODE: Processing 3 random samples")
            df = df.sample(n=3, random_state=42)

        os.makedirs(output_dir, exist_ok=True)

        # Setup file logging
        log_file = os.path.join(output_dir, 'llama_extraction.log')
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        logger.addHandler(file_handler)

        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        logger.addHandler(console_handler)

        logger.info("="*60)
        logger.info(f"Starting extraction: {len(df)} samples")
        logger.info(f"Output directory: {output_dir}")
        logger.info(f"Log file: {log_file}")
        logger.info("="*60)

        current_batch = {}
        processed_count = 0
        failed_count = 0
        start_time = datetime.now()

        for idx, row in tqdm(df.iterrows(), total=len(df), desc="Processing VQA"):
            question_id = None
            try:
                question_id = row["question_id"]
                image_id = row.get("image_id") or row.get("image_name")
                question = row["question"]
                # Handle empty gt_answer gracefully
                gt_answer = row.get("answer", "") or row.get("gt_answer", "")
                if pd.isna(gt_answer):
                    gt_answer = ""

                image_path = os.path.join(images_dir, image_id)
                if not os.path.exists(image_path):
                    logger.warning(f"❌ [{question_id}] Image not found: {image_path}")
                    failed_count += 1
                    continue

                image = Image.open(image_path).convert("RGB")
                logger.info(f"🔄 [{question_id}] Processing image: {image_id}")

                emb = self.extract_embeddings(image, question)

                current_batch[question_id] = {
                    "question": question,
                    "image_id": image_id,
                    "vision_only_representation": emb["vision_only_representation"],
                    "vision_token_representation": emb["vision_token_representation"],
                    "query_token_representation": emb["query_token_representation"],
                    "answer": emb["answer"],
                    "ground_truth_answer": gt_answer
                }

                processed_count += 1
                logger.info(f"✅ [{question_id}] Successfully extracted embeddings | Total: {processed_count}/{len(df)}")

                # Progress logging every 100 samples
                if processed_count % 100 == 0:
                    elapsed = (datetime.now() - start_time).total_seconds()
                    speed = processed_count / elapsed if elapsed > 0 else 0
                    eta_seconds = (len(df) - processed_count) / speed if speed > 0 else 0
                    eta = str(pd.Timedelta(seconds=int(eta_seconds)))
                    logger.info(f"📊 Progress: {processed_count}/{len(df)} | Speed: {speed:.2f} samples/sec | ETA: {eta} | Failed: {failed_count}")

                # GPU memory logging every 500 samples
                if processed_count % 500 == 0:
                    if torch.cuda.is_available():
                        mem_allocated = torch.cuda.memory_allocated(0) / 1e9
                        mem_reserved = torch.cuda.memory_reserved(0) / 1e9
                        logger.info(f"💾 GPU Memory: Allocated={mem_allocated:.2f}GB, Reserved={mem_reserved:.2f}GB")

                # Save checkpoint
                if processed_count % checkpoint_interval == 0:
                    self._save_checkpoint(current_batch, output_dir, processed_count // checkpoint_interval)
                    current_batch = {}
                    torch.cuda.empty_cache()
                    logger.info(f"💾 Saved checkpoint at {processed_count} samples")

            except Exception as e:
                failed_count += 1
                error_id = question_id if question_id else f"row_{idx}"
                logger.error(f"❌ [{error_id}] Failed to process: {e}")
                torch.cuda.empty_cache()
                continue

        # Save final batch
        if current_batch:
            final_part = (processed_count // checkpoint_interval) + 1
            self._save_checkpoint(current_batch, output_dir, final_part)
            logger.info(f"Saved final checkpoint with {len(current_batch)} samples")

        # Final summary
        total_time = (datetime.now() - start_time).total_seconds()
        avg_speed = processed_count / total_time if total_time > 0 else 0
        logger.info("="*60)
        logger.info(f"✅ Processing completed!")
        logger.info(f"   Total processed: {processed_count} samples")
        logger.info(f"   Failed: {failed_count} samples")
        logger.info(f"   Total time: {pd.Timedelta(seconds=int(total_time))}")
        logger.info(f"   Average speed: {avg_speed:.2f} samples/sec")
        logger.info("="*60)

    def _save_checkpoint(self, batch_data: Dict, output_dir: str, part_num: int):
        """Save batch to HDF5 with same layout as Gemma script."""
        filename = f"llama3_2_11b_vision_embeddings_part_{part_num:03d}.h5"
        filepath = os.path.join(output_dir, filename)

        with h5py.File(filepath, "w") as f:
            f.attrs["model_name"] = self.model_path
            f.attrs["model_type"] = "llama-3.2-11b-vision"
            f.attrs["device"] = "cuda"
            f.attrs["dtype"] = "bfloat16"
            f.attrs["created_at"] = datetime.now().isoformat()
            f.attrs["num_samples"] = len(batch_data)

            for qid, data in batch_data.items():
                grp = f.create_group(str(qid))

                grp.create_dataset("image_id", data=data["image_id"], dtype=h5py.string_dtype())
                grp.create_dataset("question", data=data["question"], dtype=h5py.string_dtype())
                grp.create_dataset("ground_truth_answer", data=data["ground_truth_answer"], dtype=h5py.string_dtype())

                if data["vision_only_representation"] is not None:
                    grp.create_dataset("vision_only_representation",
                                       data=data["vision_only_representation"],
                                       compression="gzip")

                if data["vision_token_representation"]:
                    rep_grp = grp.create_group("vision_token_representation")
                    for layer_name, vec in data["vision_token_representation"].items():
                        rep_grp.create_dataset(layer_name, data=vec, compression="gzip")

                if data["query_token_representation"]:
                    rep_grp = grp.create_group("query_token_representation")
                    for layer_name, vec in data["query_token_representation"].items():
                        rep_grp.create_dataset(layer_name, data=vec, compression="gzip")

                grp.create_dataset("answer", data=data["answer"], dtype=h5py.string_dtype())

        logger.info(f"Saved {len(batch_data)} samples to {filepath}")


def main():
    parser = argparse.ArgumentParser(description="Llama 3.2 Vision 11B VQA Extractor")
    parser.add_argument('--vqa-dataset', required=True, help='Path to VQA CSV dataset')
    parser.add_argument('--images-dir', required=True, help='Directory containing images')
    parser.add_argument('--output-dir', default='./output', help='Output directory for embeddings')
    parser.add_argument('--model', default='meta-llama/Llama-3.2-11B-Vision-Instruct', help='Model path')
    parser.add_argument('--cache-dir', default='./model_cache', help='Model cache directory')
    parser.add_argument('--checkpoint-interval', type=int, default=1000, help='Save every N samples')
    parser.add_argument('--test', action='store_true', help='Test mode (3 samples)')
    args = parser.parse_args()

    logger.info("🚀 Initializing Llama 3.2 Vision Extractor")
    extractor = Llama32VisionExtractorGPU(model_path=args.model, cache_dir=args.cache_dir)

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
