#!/usr/bin/env python3
import sys
from pathlib import Path

old_code = '''    if len(embeddings_list) == 0:
        raise ValueError(f"No embeddings found for {embedding_type}" + (f"/{layer_name}" if layer_name else ""))

    embeddings = np.stack(embeddings_list)
    labels = np.array(labels_list)'''

new_code = '''    if len(embeddings_list) == 0:
        raise ValueError(f"No embeddings found for {embedding_type}" + (f"/{layer_name}" if layer_name else ""))

    # Handle variable-size embeddings (for vision_only_representation in some models)
    # Check if all embeddings have the same shape
    shapes = [emb.shape for emb in embeddings_list]
    if len(set(shapes)) > 1:
        # Variable shapes detected - pad to max length
        max_len = max(emb.shape[0] for emb in embeddings_list)
        logger.info(f"Variable embedding shapes detected. Padding to max length: {max_len}")
        padded_embeddings = []
        for emb in embeddings_list:
            if len(emb.shape) == 1:  # 1D embeddings
                padded = np.zeros(max_len, dtype=emb.dtype)
                padded[:len(emb)] = emb
                padded_embeddings.append(padded)
            else:
                raise ValueError(f"Unexpected embedding shape: {emb.shape}")
        embeddings = np.stack(padded_embeddings)
    else:
        embeddings = np.stack(embeddings_list)

    labels = np.array(labels_list)'''

for script in Path('.').glob('*.py'):
    if script.name.startswith(('02_', '03_', '04_', '05_', '06_', '07_', '08_', '09_', '10_', '11_')):
        content = script.read_text()
        if old_code in content:
            content = content.replace(old_code, new_code)
            script.write_text(content)
            print(f"Updated {script.name}")
        else:
            print(f"Skipped {script.name} (pattern not found)")
