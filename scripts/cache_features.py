import os
import json
import argparse
import h5py
import torch
from tqdm import tqdm
from PIL import Image
from transformers import AutoProcessor, Qwen2_5_VLForConditionalGeneration, AutoTokenizer

from models.extractor import Qwen25VLExtractor

def main():
    parser = argparse.ArgumentParser(description="SHROOM-Vision 2026 Feature Cacher")
    parser.add_argument("--jsonl-path", required=True, help="Path to labeled training JSONL")
    parser.add_argument("--images-dir", required=True, help="Path to images directory")
    parser.add_argument("--output-cache-dir", required=True, help="Directory to save HDF5 features")
    parser.add_argument("--model-name", default="Qwen/Qwen2.5-VL-3B-Instruct", help="Huggingface VLM model name")
    parser.add_argument("--device", default="cuda" if torch.cuda.is_available() else "cpu", help="Device to run extraction")
    args = parser.parse_args()

    print(f"Loading processor and tokenizer for {args.model_name}...")
    processor = AutoProcessor.from_pretrained(args.model_name, trust_remote_code=True)
    tokenizer = AutoTokenizer.from_pretrained(args.model_name, trust_remote_code=True)

    print(f"Loading VLM model on {args.device} (bfloat16)...")
    if args.device == "cuda":
        model = Qwen2_5_VLForConditionalGeneration.from_pretrained(
            args.model_name,
            torch_dtype=torch.bfloat16,
            device_map="auto",
            attn_implementation="eager", # eager mode is required to extract attention weights
            trust_remote_code=True
        )
    else:
        model = Qwen2_5_VLForConditionalGeneration.from_pretrained(
            args.model_name,
            attn_implementation="eager",
            trust_remote_code=True
        )
    model.eval()

    # Instantiate extractor wrapper
    extractor = Qwen25VLExtractor(
        model=model,
        processor=processor,
        tokenizer=tokenizer,
        device=torch.device(args.device)
    )

    os.makedirs(args.output_cache_dir, exist_ok=True)

    # Load dataset lines
    print(f"Reading dataset: {args.jsonl_path}")
    samples = []
    with open(args.jsonl_path, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                samples.append(json.loads(line))

    print(f"Caching features for {len(samples)} samples...")
    for sample in tqdm(samples):
        sample_id = sample['id']
        prompt = sample['prompt']
        response = sample['response']
        image_name = sample['image_name']

        cache_file = os.path.join(args.output_cache_dir, f"{sample_id}.h5")
        if os.path.exists(cache_file):
            continue  # skip already cached items

        # Load image
        image_path = os.path.join(args.images_dir, image_name)
        if not os.path.exists(image_path):
            # Print warning and create dummy image for caching if missing
            image = Image.new('RGB', (224, 224), color='white')
        else:
            try:
                image = Image.open(image_path).convert('RGB')
            except Exception as e:
                print(f"Failed to open image {image_path}: {e}. Using dummy.")
                image = Image.new('RGB', (224, 224), color='white')

        try:
            # Extract
            features = extractor.extract_features(image, prompt, response)

            # Write HDF5 cache
            with h5py.File(cache_file, 'w') as f:
                f.create_dataset('vision_features', data=features['vision_features'].cpu().numpy())
                f.create_dataset('decoder_hidden_states', data=features['decoder_hidden_states'].cpu().numpy())
                f.create_dataset('query_hidden_states', data=features['query_hidden_states'].cpu().numpy())
                f.create_dataset('cross_attention', data=features['cross_attention'].cpu().numpy())
                
        except Exception as e:
            print(f"Error caching features for sample {sample_id}: {e}")
            
    print("Caching complete!")

if __name__ == "__main__":
    main()
