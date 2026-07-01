"""
Verify H5 file access for vision_token and query_token representations
"""

import h5py
import glob

# Paths
H5_DIR = "/root/akhil/HALP_EACL_Models/Models/Gemma3_12B/gemma_output"

# Gemma3 has 48 layers, selected layers are: 0, 12, 24, 36, 47
SELECTED_LAYERS = [0, 12, 24, 36, 47]

print("=" * 80)
print("VERIFYING LAYER-BASED EMBEDDINGS ACCESS")
print("=" * 80)

# Find H5 files
h5_files = sorted(glob.glob(f"{H5_DIR}/*.h5"))
print(f"\nFound {len(h5_files)} H5 files")

# Check first H5 file
first_h5 = h5_files[0]
print(f"\nInspecting: {first_h5}")

with h5py.File(first_h5, 'r') as f:
    question_ids = list(f.keys())
    first_qid = question_ids[0]

    print(f"\nSample: {first_qid}")
    sample_group = f[first_qid]

    print(f"Top-level keys: {list(sample_group.keys())}")

    # Check vision_token_representation
    print(f"\n1. Checking 'vision_token_representation':")
    if 'vision_token_representation' in sample_group:
        vision_group = sample_group['vision_token_representation']
        print(f"   ✅ Found 'vision_token_representation'")
        print(f"   Type: {type(vision_group)}")
        print(f"   Layer keys: {list(vision_group.keys())}")

        # Check each selected layer
        print(f"\n   Checking selected layers: {SELECTED_LAYERS}")
        for layer_idx in SELECTED_LAYERS:
            layer_name = f'layer_{layer_idx}'
            if layer_name in vision_group:
                embedding = vision_group[layer_name][:]
                print(f"   ✅ {layer_name}: shape={embedding.shape}, dtype={embedding.dtype}")
            else:
                print(f"   ❌ {layer_name}: NOT FOUND")
                print(f"      Available: {list(vision_group.keys())}")
    else:
        print(f"   ❌ 'vision_token_representation' NOT found")

    # Check query_token_representation
    print(f"\n2. Checking 'query_token_representation':")
    if 'query_token_representation' in sample_group:
        query_group = sample_group['query_token_representation']
        print(f"   ✅ Found 'query_token_representation'")
        print(f"   Type: {type(query_group)}")
        print(f"   Layer keys: {list(query_group.keys())}")

        # Check each selected layer
        print(f"\n   Checking selected layers: {SELECTED_LAYERS}")
        for layer_idx in SELECTED_LAYERS:
            layer_name = f'layer_{layer_idx}'
            if layer_name in query_group:
                embedding = query_group[layer_name][:]
                print(f"   ✅ {layer_name}: shape={embedding.shape}, dtype={embedding.dtype}")
            else:
                print(f"   ❌ {layer_name}: NOT FOUND")
                print(f"      Available: {list(query_group.keys())}")
    else:
        print(f"   ❌ 'query_token_representation' NOT found")

# Summary
print("\n" + "=" * 80)
print("EMBEDDING TYPE MAPPINGS FOR PROBE SCRIPTS:")
print("=" * 80)

print("\n01_vision_only_probe.py:")
print(f"   EMBEDDING_TYPE = 'vision_only_representation'")

print("\n02_vision_token_layer0_probe.py:")
print(f"   EMBEDDING_TYPE = 'vision_token_representation'")
print(f"   LAYER_NAME = 'layer_0'")

print("\n03_vision_token_layer_n_4_probe.py:")
print(f"   EMBEDDING_TYPE = 'vision_token_representation'")
print(f"   LAYER_NAME = 'layer_12'  # n//4 where n=48")

print("\n04_vision_token_layer_n_2_probe.py:")
print(f"   EMBEDDING_TYPE = 'vision_token_representation'")
print(f"   LAYER_NAME = 'layer_24'  # n//2 where n=48")

print("\n05_vision_token_layer_3n_4_probe.py:")
print(f"   EMBEDDING_TYPE = 'vision_token_representation'")
print(f"   LAYER_NAME = 'layer_36'  # 3n//4 where n=48")

print("\n06_vision_token_layer_n_probe.py:")
print(f"   EMBEDDING_TYPE = 'vision_token_representation'")
print(f"   LAYER_NAME = 'layer_47'  # n-1 where n=48")

print("\n07_query_token_layer0_probe.py:")
print(f"   EMBEDDING_TYPE = 'query_token_representation'")
print(f"   LAYER_NAME = 'layer_0'")

print("\n08_query_token_layer_n_4_probe.py:")
print(f"   EMBEDDING_TYPE = 'query_token_representation'")
print(f"   LAYER_NAME = 'layer_12'")

print("\n09_query_token_layer_n_2_probe.py:")
print(f"   EMBEDDING_TYPE = 'query_token_representation'")
print(f"   LAYER_NAME = 'layer_24'")

print("\n10_query_token_layer_3n_4_probe.py:")
print(f"   EMBEDDING_TYPE = 'query_token_representation'")
print(f"   LAYER_NAME = 'layer_36'")

print("\n11_query_token_layer_n_probe.py:")
print(f"   EMBEDDING_TYPE = 'query_token_representation'")
print(f"   LAYER_NAME = 'layer_47'")

print("\n" + "=" * 80)
print("✅ VERIFICATION COMPLETE!")
print("=" * 80)
