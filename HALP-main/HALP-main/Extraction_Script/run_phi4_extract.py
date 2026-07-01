#!/usr/bin/env python3
"""
Phi-4 Multimodal (5.6B) VQA Embedding Extractor
Extracts embeddings for HALP-style probing from a multimodal LLM:

1) Vision-only representation (from SigLIP vision encoder, pooled)
2) Vision token representation (hidden state at <|image_1|> placeholder)
3) Query token representation (hidden state at end-of-prompt)
4) Generated answer

Layer sampling matches Llama-3.2 script by percentage:
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
from transformers import AutoProcessor, AutoModelForCausalLM
from tqdm import tqdm
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class Phi4MultimodalExtractorGPU:
    """Phi-4 Multimodal extractor optimized for GPU with float16"""

    def __init__(self, model_path: str = "microsoft/Phi-4-multimodal-instruct", cache_dir: str = "./model_cache"):
        self.model_path = model_path
        self.cache_dir = cache_dir

        if not torch.cuda.is_available():
            raise RuntimeError("CUDA is not available. This script requires a CUDA-capable GPU.")

        logger.info(f"CUDA Device: {torch.cuda.get_device_name(0)}")
        logger.info(f"CUDA Memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.2f} GB")

        self._load_model()

    def _load_model(self):
        """Load Phi-4 Multimodal model + processor"""
        logger.info(f"Loading Phi-4 Multimodal model: {self.model_path}")

        self.processor = AutoProcessor.from_pretrained(
            self.model_path,
            cache_dir=self.cache_dir,
            trust_remote_code=True
        )

        # Use Flash Attention 2 if available, auto dtype
        # Note: Phi-4 automatically loads vision LoRA adapter during initialization
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_path,
            cache_dir=self.cache_dir,
            torch_dtype="auto",
            device_map="cuda",
            trust_remote_code=True,
            attn_implementation="flash_attention_2"  # Use "eager" for older GPUs
        )

        self.model.eval()

        # Detect # of text (decoder) layers
        self.num_layers = None
        try:
            # Phi-4 has text_config in config
            if hasattr(self.model.config, "text_config") and hasattr(self.model.config.text_config, "num_hidden_layers"):
                self.num_layers = int(self.model.config.text_config.num_hidden_layers)
            elif hasattr(self.model.config, "num_hidden_layers"):
                self.num_layers = int(self.model.config.num_hidden_layers)
        except Exception:
            pass

        if self.num_layers is None:
            # Fallback: do a tiny forward with output_hidden_states to infer it
            dummy_prompt = '<|user|><|image_1|>Test<|end|><|assistant|>'
            dummy = self.processor(text=dummy_prompt, images=Image.new("RGB", (4, 4)), return_tensors="pt").to(self.model.device)
            with torch.no_grad():
                out = self.model(**dummy, output_hidden_states=True, return_dict=True)
            # hidden_states = [embeddings] + [L layers]
            self.num_layers = len(out.hidden_states) - 1

        logger.info(f"Detected {self.num_layers} language model layers")

        # Cache special token IDs
        self.image_token_id = 200010  # <|image_1|> in Phi-4
        self.audio_token_id = 200011  # <|audio_1|> in Phi-4

        # Try to find a vision submodule for vision-only embedding
        # Phi-4 uses: model.model.embed_tokens_extend.image_embed.img_processor (SigLIP)
        self._vision_submodule = None
        if hasattr(self.model, "model"):
            if hasattr(self.model.model, "embed_tokens_extend"):
                if hasattr(self.model.model.embed_tokens_extend, "image_embed"):
                    if hasattr(self.model.model.embed_tokens_extend.image_embed, "img_processor"):
                        self._vision_submodule = self.model.model.embed_tokens_extend.image_embed.img_processor
                        logger.info(f"Found Phi-4 vision encoder: {type(self._vision_submodule)}")

        if self._vision_submodule is None:
            logger.warning("Did not find vision encoder submodule; vision-only representation may be skipped.")

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

        # Build Phi-4 formatted prompt
        prompt = f'<|user|><|image_1|>{question}<|end|><|assistant|>'

        inputs = self.processor(
            text=prompt,
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
            with torch.autocast(device_type="cuda", dtype=torch.float16):
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
        """Vision encoder pooled vector. Averages across tiles/sequence to a single vector."""
        try:
            if self._vision_submodule is None:
                return None

            # For Phi-4, the processor already runs vision encoder internally
            # We need to extract from the pre-computed embeddings
            vis_inputs = self.processor.image_processor(images=[image], return_tensors="pt")

            # Phi-4 returns 'input_image_embeds' - already processed by vision encoder
            if 'input_image_embeds' in vis_inputs:
                # input_image_embeds is the output from vision encoder
                # Shape: [batch, tiles, channels, height, width] or similar
                feats = vis_inputs['input_image_embeds'].to(self.model.device)

                # Pool over all spatial/tile dimensions to get single vector
                while feats.dim() > 2:
                    feats = feats.mean(dim=1)

                # [B, hidden] -> [hidden]
                rep = feats.squeeze(0).to(torch.float32).cpu().numpy()
                return rep
            else:
                logger.warning(f"Available keys in vis_inputs: {vis_inputs.keys()}")
                return None

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

        # Position of last <|image_1|> token (if any). If none, we choose the first token.
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

        current_batch = {}
        processed_count = 0

        for idx, row in tqdm(df.iterrows(), total=len(df), desc="Processing VQA"):
            try:
                question_id = row["question_id"]
                image_id = row.get("image_id") or row.get("image_name")
                question = row["question"]
                gt_answer = row.get("answer") or row.get("gt_answer")

                image_path = os.path.join(images_dir, image_id)
                if not os.path.exists(image_path):
                    logger.warning(f"Image not found: {image_path}")
                    continue

                image = Image.open(image_path).convert("RGB")

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
                torch.cuda.empty_cache()

                if processed_count % checkpoint_interval == 0:
                    self._save_checkpoint(current_batch, output_dir, processed_count // checkpoint_interval)
                    current_batch = {}
                    torch.cuda.empty_cache()
                    logger.info(f"Saved checkpoint at {processed_count} samples")

            except Exception as e:
                logger.error(f"Failed to process {row.get('question_id', idx)}: {e}")
                torch.cuda.empty_cache()
                continue

        if current_batch:
            final_part = (processed_count // checkpoint_interval) + 1
            self._save_checkpoint(current_batch, output_dir, final_part)
            logger.info(f"Saved final checkpoint with {len(current_batch)} samples")

        logger.info(f"✅ Processing completed! Total: {processed_count} samples")

    def _save_checkpoint(self, batch_data: Dict, output_dir: str, part_num: int):
        """Save batch to HDF5 with same layout as Llama script."""
        filename = f"phi4_multimodal_embeddings_part_{part_num:03d}.h5"
        filepath = os.path.join(output_dir, filename)

        with h5py.File(filepath, "w") as f:
            f.attrs["model_name"] = self.model_path
            f.attrs["model_type"] = "phi-4-multimodal"
            f.attrs["device"] = "cuda"
            f.attrs["dtype"] = "float16"
            f.attrs["created_at"] = datetime.now().isoformat()
            f.attrs["num_samples"] = len(batch_data)

            for qid, data in batch_data.items():
                grp = f.create_group(str(qid))

                grp.create_dataset("image_id", data=data["image_id"], dtype=h5py.string_dtype())
                grp.create_dataset("question", data=data["question"], dtype=h5py.string_dtype())
                # Convert ground_truth_answer to string to handle NaN/None/numeric values
                gt_answer = str(data["ground_truth_answer"]) if data["ground_truth_answer"] is not None else ""
                grp.create_dataset("ground_truth_answer", data=gt_answer, dtype=h5py.string_dtype())

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
    parser = argparse.ArgumentParser(description="Phi-4 Multimodal VQA Extractor")
    parser.add_argument('--vqa-dataset', required=True, help='Path to VQA CSV dataset')
    parser.add_argument('--images-dir', required=True, help='Directory containing images')
    parser.add_argument('--output-dir', default='./output', help='Output directory for embeddings')
    parser.add_argument('--model', default='microsoft/Phi-4-multimodal-instruct', help='Model path')
    parser.add_argument('--cache-dir', default='./model_cache', help='Model cache directory')
    parser.add_argument('--checkpoint-interval', type=int, default=1000, help='Save every N samples')
    parser.add_argument('--test', action='store_true', help='Test mode (3 samples)')
    args = parser.parse_args()

    logger.info("🚀 Initializing Phi-4 Multimodal Extractor")
    extractor = Phi4MultimodalExtractorGPU(model_path=args.model, cache_dir=args.cache_dir)

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
