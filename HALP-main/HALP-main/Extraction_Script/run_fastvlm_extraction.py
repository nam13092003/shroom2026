import os
import torch
import pandas as pd
import numpy as np
import h5py
import logging
import argparse
from transformers import AutoModelForCausalLM, AutoTokenizer
from PIL import Image
from tqdm import tqdm

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

MODEL_REPO = "apple/FastVLM-7B"
MODEL_DIR = "fastvlm_7b"

# Paths
CSV_PATH = "/root/akhil/final_data/sampled_10k_relational_dataset.csv"
IMAGES_DIR = "/root/akhil/final_data/all_images"
RESULTS_DIR = "/root/akhil/HALP_EACL_Models/Models/FastVLM_model/fastvlm_output"
os.makedirs(RESULTS_DIR, exist_ok=True)

BATCH_SIZE = 1000
IMAGE_TOKEN_INDEX = -200

def download_model(model_repo=MODEL_REPO, local_dir=MODEL_DIR):
    """Download the model if it doesn't exist."""
    if not os.path.exists(local_dir):
        logger.info(f"Downloading model to {local_dir}...")
        from huggingface_hub import snapshot_download
        model_path = snapshot_download(repo_id=model_repo, local_dir=local_dir)
        logger.info(f"Model downloaded to: {model_path}")
    else:
        logger.info(f"Model already exists at: {local_dir}")
    return local_dir

def get_layer_indices(total_layers):
    """Get layer indices: 0, n//4, n//2, 3n//4, n-1"""
    if total_layers < 5:
        return list(range(total_layers))
    
    indices = [
        0,
        total_layers // 4,
        total_layers // 2,
        (3 * total_layers) // 4,
        total_layers - 1
    ]
    
    return sorted(list(set(indices)))

def safe_tensor_to_numpy(tensor, name="tensor"):
    """Safely convert tensor to numpy array."""
    try:
        if tensor.dtype == torch.bfloat16:
            tensor = tensor.float()
        return tensor.detach().cpu().numpy()
    except Exception as e:
        logger.warning(f"Could not convert {name} to numpy: {e}")
        return None

def extract_embeddings(image_path, question, model, tokenizer, device, config):
    """Extract embeddings from FastVLM model."""
    embeddings_data = {}

    # Load image
    image = Image.open(image_path).convert('RGB')

    # Extract vision-only representation (before MLP projector)
    try:
        vision_tower = model.get_vision_tower()
        px = vision_tower.image_processor(images=image, return_tensors="pt")["pixel_values"]
        px = px.to(device, dtype=model.dtype)

        with torch.no_grad():
            # Get vision features from vision tower
            vision_outputs = vision_tower(px)

            # Get features before projection
            if hasattr(vision_outputs, 'last_hidden_state'):
                vision_features = vision_outputs.last_hidden_state
            elif isinstance(vision_outputs, tuple):
                vision_features = vision_outputs[0]
            else:
                vision_features = vision_outputs

            # Pool vision features (average over spatial dimension)
            if vision_features.dim() == 3:  # [batch, seq_len, hidden]
                pooled_vision = vision_features.mean(dim=1)
            elif vision_features.dim() == 2:  # [batch, hidden]
                pooled_vision = vision_features
            else:
                pooled_vision = vision_features.reshape(vision_features.size(0), -1).mean(dim=1, keepdim=True)

            embeddings_data['vision_only_representation'] = safe_tensor_to_numpy(pooled_vision.squeeze(0), "vision_only")

    except Exception as e:
        logger.warning(f"Could not extract vision-only representation: {e}")
        embeddings_data['vision_only_representation'] = np.zeros(1024, dtype=np.float32)

    # Prepare chat message with image
    messages = [
        {"role": "user", "content": f"<image>\n{question}"}
    ]

    # Apply chat template and split by image token
    rendered = tokenizer.apply_chat_template(messages, add_generation_prompt=True, tokenize=False)
    pre, post = rendered.split("<image>", 1)

    # Tokenize parts separately
    pre_ids = tokenizer(pre, return_tensors="pt", add_special_tokens=False).input_ids
    post_ids = tokenizer(post, return_tensors="pt", add_special_tokens=False).input_ids

    # Create input with image token
    img_tok = torch.tensor([[IMAGE_TOKEN_INDEX]], dtype=pre_ids.dtype)
    input_ids = torch.cat([pre_ids, img_tok, post_ids], dim=1).to(device)
    attention_mask = torch.ones_like(input_ids, device=device)

    # Prepare image tensor
    px = vision_tower.image_processor(images=image, return_tensors="pt")["pixel_values"]
    px = px.to(device, dtype=model.dtype)

    # Generate with hidden states
    with torch.no_grad():
        outputs = model.generate(
            inputs=input_ids,
            attention_mask=attention_mask,
            images=px,
            max_new_tokens=100,
            do_sample=False,
            output_hidden_states=True,
            return_dict_in_generate=True
        )

    # Extract hidden states
    if hasattr(outputs, 'hidden_states') and outputs.hidden_states:
        # Get hidden states from first generation step
        first_step_hidden = outputs.hidden_states[0]

        selected_layers = config['selected_layers']
        seq_length = input_ids.shape[1]

        # Find image token position
        image_token_pos = (input_ids == IMAGE_TOKEN_INDEX).nonzero(as_tuple=True)[1].item() if (input_ids == IMAGE_TOKEN_INDEX).any() else seq_length // 2
        query_token_pos = seq_length - 1

        # Extract from selected layers
        vision_token_data = {}
        query_token_data = {}

        for layer_idx in selected_layers:
            if layer_idx < len(first_step_hidden):
                layer_hidden = first_step_hidden[layer_idx]

                vision_emb = layer_hidden[0, image_token_pos, :]
                query_emb = layer_hidden[0, query_token_pos, :]

                vision_token_data[f'layer_{layer_idx}'] = safe_tensor_to_numpy(vision_emb, f"layer_{layer_idx}_vision")
                query_token_data[f'layer_{layer_idx}'] = safe_tensor_to_numpy(query_emb, f"layer_{layer_idx}_query")

        embeddings_data['vision_token_representation'] = vision_token_data
        embeddings_data['query_token_representation'] = query_token_data

    # Extract generated text (assistant response only)
    generated_ids = outputs.sequences
    full_text = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]

    # Extract only the assistant's response
    if "assistant" in full_text.lower():
        parts = full_text.lower().split("assistant")
        if len(parts) > 1:
            answer = full_text[full_text.lower().index("assistant") + len("assistant"):].strip()
        else:
            answer = full_text.strip()
    elif question in full_text:
        answer = full_text.split(question)[-1].strip()
    else:
        answer = full_text.strip()

    embeddings_data['answer'] = answer

    return embeddings_data

def write_batch_to_hdf5(batch_file, batch_results, image_ids, questions, gt_answers):
    """Write batch to HDF5 file."""
    try:
        with h5py.File(batch_file, 'w') as f:
            for idx, (question_id, result) in enumerate(batch_results.items()):
                # Create group for this question
                group = f.create_group(str(question_id))
                
                # Store metadata
                group.create_dataset('question', data=str(questions[idx]).encode('utf-8'))
                group.create_dataset('image_id', data=str(image_ids[idx]).encode('utf-8'))
                group.create_dataset('ground_truth_answer', data=str(gt_answers[idx]).encode('utf-8'))
                
                # Store vision_only_representation
                if 'vision_only_representation' in result and result['vision_only_representation'] is not None:
                    group.create_dataset('vision_only_representation',
                                       data=np.array(result['vision_only_representation'], dtype=np.float32),
                                       chunks=True,
                                       compression='gzip')
                
                # Store vision_token_representation
                if 'vision_token_representation' in result:
                    vision_group = group.create_group('vision_token_representation')
                    for layer_name, layer_emb in result['vision_token_representation'].items():
                        if layer_emb is not None:
                            vision_group.create_dataset(layer_name,
                                                       data=np.array(layer_emb, dtype=np.float32),
                                                       chunks=True,
                                                       compression='gzip')
                
                # Store query_token_representation
                if 'query_token_representation' in result:
                    query_group = group.create_group('query_token_representation')
                    for layer_name, layer_emb in result['query_token_representation'].items():
                        if layer_emb is not None:
                            query_group.create_dataset(layer_name,
                                                      data=np.array(layer_emb, dtype=np.float32),
                                                      chunks=True,
                                                      compression='gzip')
                
                # Store answer
                if 'answer' in result:
                    group.create_dataset('answer', data=str(result['answer']).encode('utf-8'))
        
        logger.info(f"Successfully wrote batch to {batch_file}")
    
    except Exception as e:
        logger.error(f"Error writing batch to HDF5: {e}")
        raise

def main():
    # Parse arguments
    parser = argparse.ArgumentParser(description='FastVLM Embedding Extraction')
    parser.add_argument('--test', action='store_true', help='Run in test mode (process only 3 samples)')
    args = parser.parse_args()
    
    # Check CUDA
    if torch.cuda.is_available():
        device = torch.device("cuda")
        logger.info(f"Using CUDA device: {torch.cuda.get_device_name(0)}")
    else:
        device = torch.device("cpu")
        logger.info("CUDA not available, using CPU")
    
    # Download model
    model_dir = download_model()
    
    # Load model with trust_remote_code
    logger.info(f"Loading FastVLM model: {MODEL_REPO}")
    try:
        model = AutoModelForCausalLM.from_pretrained(
            model_dir,
            trust_remote_code=True,
            device_map="auto",
            torch_dtype=torch.float16
        )
        tokenizer = AutoTokenizer.from_pretrained(model_dir, trust_remote_code=True)
        logger.info("Model loaded successfully")
    except Exception as e:
        logger.error(f"Error loading model: {e}")
        raise
    
    # Detect model layers
    # For Qwen2-7B, there are typically 32 layers
    if hasattr(model.config, 'num_hidden_layers'):
        total_layers = model.config.num_hidden_layers
    elif hasattr(model, 'language_model') and hasattr(model.language_model.config, 'num_hidden_layers'):
        total_layers = model.language_model.config.num_hidden_layers
    else:
        total_layers = 32  # Default for Qwen2-7B
    
    selected_layers = get_layer_indices(total_layers)
    config = {
        'total_layers': total_layers,
        'selected_layers': selected_layers
    }
    
    logger.info(f"Model architecture: {total_layers} layers")
    logger.info(f"Selected layers: {selected_layers}")
    
    # Load CSV
    df = pd.read_csv(CSV_PATH)
    logger.info(f"Loaded {len(df)} samples from CSV")
    
    # Test mode
    if args.test:
        logger.info("TEST MODE: Processing 3 random samples")
        df = df.sample(n=min(3, len(df)))
    
    total_batches = (len(df) + BATCH_SIZE - 1) // BATCH_SIZE
    logger.info(f"Processing {len(df)} samples in {total_batches} batches")
    
    processed_count = 0
    failed_count = 0
    
    for batch_idx in range(total_batches):
        start_idx = batch_idx * BATCH_SIZE
        end_idx = min(start_idx + BATCH_SIZE, len(df))
        batch = df.iloc[start_idx:end_idx]
        
        logger.info(f"\nProcessing batch {batch_idx + 1}/{total_batches} (samples {start_idx + 1}-{end_idx})")
        
        batch_results = {}
        batch_image_ids = []
        batch_questions = []
        batch_gt_answers = []
        
        for _, row in batch.iterrows():
            # Support both image_id and image_name
            image_id = row.get('image_id') or row.get('image_name')
            image_path = os.path.join(IMAGES_DIR, image_id)
            question = str(row['question']) if pd.notna(row['question']) else ""
            question_id = row['question_id']
            
            # Handle ground truth answer
            gt_answer = row.get('answer') or row.get('gt_answer')
            gt_answer = str(gt_answer) if pd.notna(gt_answer) and str(gt_answer).strip() else "N/A"
            
            try:
                if not os.path.exists(image_path):
                    logger.warning(f"❌ FAIL [{question_id}]: Image not found: {image_path}")
                    failed_count += 1
                    continue
                
                result = extract_embeddings(image_path, question, model, tokenizer, device, config)
                
                batch_results[question_id] = result
                batch_image_ids.append(str(image_id))
                batch_questions.append(question)
                batch_gt_answers.append(gt_answer)
                
                processed_count += 1
                logger.info(f"✅ PASS [{question_id}]: Processed successfully ({processed_count}/{len(df)})")
                
                # Clear CUDA cache
                torch.cuda.empty_cache()
            
            except Exception as e:
                logger.error(f"❌ FAIL [{question_id}]: {e}")
                failed_count += 1
                torch.cuda.empty_cache()
                continue
        
        # Write batch to HDF5
        if batch_results:
            batch_file = os.path.join(RESULTS_DIR, f"fastvlm_7b_embeddings_part_{batch_idx + 1:03d}.h5")
            write_batch_to_hdf5(batch_file, batch_results, batch_image_ids, batch_questions, batch_gt_answers)
            logger.info(f"💾 Checkpoint saved with {len(batch_results)} samples")
        
        logger.info(f"Batch {batch_idx + 1} completed")
    
    logger.info(f"\n✅ Processing completed!")
    logger.info(f"   Total processed: {processed_count} samples")
    logger.info(f"   Total failed: {failed_count} samples")
    if processed_count + failed_count > 0:
        logger.info(f"   Success rate: {100 * processed_count / (processed_count + failed_count):.2f}%")
    logger.info(f"   Results saved to: {RESULTS_DIR}")

if __name__ == "__main__":
    main()
