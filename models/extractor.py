import torch
import torch.nn as nn
from typing import Dict, List, Tuple, Any, Optional
from PIL import Image

class Qwen25VLExtractor:
    """
    Feature extractor for Qwen2.5-VL.
    Extracts:
    1. Vision features from the vision encoder.
    2. Decoder hidden states for text tokens.
    3. Query token hidden states (global query representation).
    4. Text-to-image cross-attentions.
    """
    def __init__(self, model: nn.Module, processor: Any, tokenizer: Any, device: torch.device):
        self.model = model
        self.processor = processor
        self.tokenizer = tokenizer
        self.device = device
        
        # Find image pad token ID
        try:
            self.image_pad_token_id = self.tokenizer.convert_tokens_to_ids("<|image_pad|>")
        except Exception:
            self.image_pad_token_id = None
            
        # Detect layers counts
        if hasattr(self.model, 'model') and hasattr(self.model.model, 'layers'):
            self.num_layers = len(self.model.model.layers)
        elif hasattr(self.model, 'model') and hasattr(self.model.model, 'language_model') and hasattr(self.model.model.language_model, 'layers'):
            self.num_layers = len(self.model.model.language_model.layers)
        else:
            self.num_layers = 28  # fallback default for 7B

    def find_vision_and_text_indices(self, input_ids: torch.Tensor) -> Tuple[List[int], List[int]]:
        """
        Find indices of vision tokens and text tokens in the sequence.
        """
        seq = input_ids.tolist()
        vision_indices = []
        text_indices = []
        
        # If image_pad_token_id is not set, try to guess or use fallback
        pad_id = self.image_pad_token_id
        if pad_id is None:
            # Fallback: Qwen2.5-VL pad ID is often 151655 or similar, let's search tokenizer vocab
            for tok, idx in self.tokenizer.get_vocab().items():
                if "image" in tok or "pad" in tok:
                    pad_id = idx
                    break
            if pad_id is None:
                pad_id = 151655 # default Qwen image pad
                
        for idx, token_id in enumerate(seq):
            if token_id == pad_id:
                vision_indices.append(idx)
            else:
                text_indices.append(idx)
                
        return vision_indices, text_indices

    def extract_features(
        self,
        image: Image.Image,
        prompt: str,
        response: str
    ) -> Dict[str, torch.Tensor]:
        """
        Run a forward pass on (Image + Prompt + Response) and extract all multitask features.
        
        Returns:
            Dict containing:
                - vision_features: [num_patches, d_vision]
                - decoder_hidden_states: [resp_len, d_hidden]
                - query_hidden_states: [d_hidden]
                - cross_attention: [resp_len, num_patches]
        """
        # 1. Format user message using chat template
        # Qwen2.5-VL templates format:
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "image", "image": image},
                    {"type": "text", "text": prompt}
                ]
            },
            {
                "role": "assistant",
                "content": [
                    {"type": "text", "text": response}
                ]
            }
        ]
        
        # Process multimodal inputs
        # Wait, the apply_chat_template expects Assistant role or we can just concatenate prompt and response
        # Let's format manually to have strict control over token sequence:
        # Prompt context + Response context
        from qwen_vl_utils import process_vision_info
        text = self.processor.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=False
        )
        image_inputs, video_inputs = process_vision_info(messages)
        
        inputs = self.processor(
            text=[text],
            images=image_inputs,
            videos=video_inputs,
            padding=True,
            return_tensors="pt"
        ).to(self.device)
        
        input_ids = inputs['input_ids'][0]
        
        # Find boundaries
        vision_indices, text_indices = self.find_vision_and_text_indices(inputs['input_ids'][0])
        num_patches = len(vision_indices)
        
        # Tokenize prompt to find the boundary between prompt and response
        prompt_messages = [
            {
                "role": "user",
                "content": [
                    {"type": "image", "image": image},
                    {"type": "text", "text": prompt}
                ]
            }
        ]
        prompt_text = self.processor.apply_chat_template(
            prompt_messages, tokenize=False, add_generation_prompt=True
        )
        prompt_inputs = self.processor(
            text=[prompt_text],
            images=image_inputs,
            videos=video_inputs,
            padding=True,
            return_tensors="pt"
        )
        prompt_len = prompt_inputs['input_ids'].shape[1]
        
        # The response tokens start at index prompt_len
        response_indices = [idx for idx in range(len(input_ids)) if idx >= prompt_len]
        resp_len = len(response_indices)
        
        # Registers hooks to capture hidden states
        captured_hidden_states = {}
        hooks = []
        
        def make_hook(layer_idx):
            def hook(module, input, output):
                if isinstance(output, tuple):
                    captured_hidden_states[layer_idx] = output[0].detach()
                else:
                    captured_hidden_states[layer_idx] = output.detach()
            return hook

        # Access layers
        if hasattr(self.model, 'model') and hasattr(self.model.model, 'layers'):
            layers = self.model.model.layers
        elif hasattr(self.model, 'model') and hasattr(self.model.model, 'language_model') and hasattr(self.model.model.language_model, 'layers'):
            layers = self.model.model.language_model.layers
        else:
            layers = []
            
        # Hook last layer
        target_layer = len(layers) - 1
        if target_layer >= 0:
            hook = layers[target_layer].register_forward_hook(make_hook(target_layer))
            hooks.append(hook)
            
        # Capture raw vision features (before projector)
        vision_features_dict = {}
        def vision_hook(module, input, output):
            vision_features_dict['features'] = output.detach()
            
        if hasattr(self.model, 'visual') and hasattr(self.model.visual, 'blocks'):
            # hook last ViT block
            v_hook = self.model.visual.blocks[-1].register_forward_hook(vision_hook)
            hooks.append(v_hook)
            
        # Run forward pass
        try:
            with torch.no_grad():
                outputs = self.model(
                    **inputs,
                    output_attentions=True,
                    return_dict=True
                )
                
            # Extract captured features
            # 1. Vision Features [num_patches, d_vision]
            raw_v_features = vision_features_dict.get('features', None)
            if raw_v_features is not None:
                # Shape is usually [seq_len, batch, dim] or [batch, seq_len, dim]
                # For ViT patch output: shape is [num_patches, dim] (batch size 1)
                if raw_v_features.dim() == 3:
                    raw_v_features = raw_v_features[0]
                vision_features = raw_v_features.cpu().float()
            else:
                # Fallback: use model's internal representation from the prompt processor
                d_vision = 1280 # default for Qwen2.5-VL ViT
                vision_features = torch.zeros((max(1, num_patches), d_vision))
                
            # 2. Decoder Hidden States [resp_len, d_hidden]
            last_hidden_states = captured_hidden_states.get(target_layer, None)
            if last_hidden_states is not None:
                # shape is [batch, total_seq_len, d_hidden]
                # extract response indices
                # ensure response indices fall within bounds
                valid_resp_indices = [idx for idx in response_indices if idx < last_hidden_states.shape[1]]
                decoder_hidden_states = last_hidden_states[0, valid_resp_indices, :].cpu().float()
                
                # 3. Query Hidden States [d_hidden]
                # represent the query by taking the last query token (just before assistant response starts)
                query_idx = min(prompt_len - 1, last_hidden_states.shape[1] - 1)
                query_hidden_states = last_hidden_states[0, query_idx, :].cpu().float()
            else:
                d_hidden = self.model.config.hidden_size if hasattr(self.model, 'config') else 3584
                decoder_hidden_states = torch.zeros((max(1, resp_len), d_hidden))
                query_hidden_states = torch.zeros(d_hidden)
                
            # 4. Cross Attention [resp_len, num_patches]
            # output_attentions returns a tuple of attention maps (one per layer)
            # each layer has shape [batch, num_heads, total_seq_len, total_seq_len]
            if outputs.attentions is not None:
                # average attention over last few layers and all heads
                # let's use the last layer's attention
                last_layer_attn = outputs.attentions[-1][0] # shape: [num_heads, total_seq_len, total_seq_len]
                mean_head_attn = last_layer_attn.mean(dim=0) # shape: [total_seq_len, total_seq_len]
                
                # extract attention of response tokens over vision tokens
                cross_attention = torch.zeros((max(1, resp_len), max(1, num_patches)))
                for r_i, r_idx in enumerate(response_indices):
                    if r_idx >= mean_head_attn.shape[0]:
                        continue
                    for v_i, v_idx in enumerate(vision_indices):
                        if v_idx >= mean_head_attn.shape[1]:
                            continue
                        cross_attention[r_i, v_i] = mean_head_attn[r_idx, v_idx].item()
                # normalize rows (attention distribution over image patches)
                row_sums = cross_attention.sum(dim=-1, keepdim=True)
                cross_attention = cross_attention / (row_sums + 1e-8)
            else:
                cross_attention = torch.zeros((max(1, resp_len), max(1, num_patches)))
                
        finally:
            # Remove hooks
            for hook in hooks:
                hook.remove()
                
        return {
            'vision_features': vision_features,
            'decoder_hidden_states': decoder_hidden_states,
            'query_hidden_states': query_hidden_states,
            'cross_attention': cross_attention
        }
