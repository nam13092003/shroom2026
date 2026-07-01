#!/usr/bin/env python3
"""
Pre-flight verification for SmolVLM probe training.
Checks that all required files and data are accessible.
"""

import os
import h5py
import pandas as pd
import glob
from pathlib import Path

# Configuration
H5_DIR = "/root/akhil/HALP_EACL_Models/Models/Smol_VL/smolvlm_output"
CSV_PATH = "/root/akhil/FInal_CSV_Hallucination/smolvlm_manually_reviewed.csv"
EXPECTED_LAYERS = ["layer_0", "layer_6", "layer_12", "layer_18", "layer_23"]

def print_header(message):
    """Print formatted header."""
    print("\n" + "=" * 80)
    print(f"  {message}")
    print("=" * 80 + "\n")

def check_csv():
    """Verify CSV file exists and has required columns."""
    print("📄 Checking CSV file...")

    if not os.path.exists(CSV_PATH):
        print(f"  ✗ CSV file not found: {CSV_PATH}")
        return False

    try:
        df = pd.read_csv(CSV_PATH, low_memory=False)

        required_columns = ['question_id', 'image_id', 'question', 'is_hallucinating_manual']
        missing_columns = [col for col in required_columns if col not in df.columns]

        if missing_columns:
            print(f"  ✗ Missing columns: {missing_columns}")
            return False

        print(f"  ✓ CSV file found: {CSV_PATH}")
        print(f"  ✓ Total rows: {len(df)}")
        print(f"  ✓ Required columns present: {required_columns}")

        # Check label distribution
        label_counts = df['is_hallucinating_manual'].value_counts()
        print(f"\n  Label distribution:")
        for label, count in label_counts.items():
            percentage = (count / len(df)) * 100
            print(f"    {label}: {count} ({percentage:.1f}%)")

        return True

    except Exception as e:
        print(f"  ✗ Error reading CSV: {e}")
        return False

def check_h5_files():
    """Verify H5 files exist and have required structure."""
    print("\n📁 Checking H5 files...")

    if not os.path.exists(H5_DIR):
        print(f"  ✗ H5 directory not found: {H5_DIR}")
        return False

    h5_files = sorted(glob.glob(os.path.join(H5_DIR, "*.h5")))

    if not h5_files:
        print(f"  ✗ No H5 files found in {H5_DIR}")
        return False

    print(f"  ✓ H5 directory found: {H5_DIR}")
    print(f"  ✓ Found {len(h5_files)} H5 files")

    # Check first file structure
    print(f"\n  Inspecting first file: {Path(h5_files[0]).name}")

    try:
        with h5py.File(h5_files[0], 'r') as f:
            sample_ids = list(f.keys())

            if not sample_ids:
                print("    ✗ No samples found in H5 file")
                return False

            first_sample = f[sample_ids[0]]

            # Check vision_only_representation
            if 'vision_only_representation' in first_sample:
                shape = first_sample['vision_only_representation'].shape
                print(f"    ✓ vision_only_representation: {shape}")
            else:
                print("    ✗ Missing vision_only_representation")
                return False

            # Check vision_token_representation
            if 'vision_token_representation' in first_sample:
                vision_token = first_sample['vision_token_representation']
                layers = sorted(list(vision_token.keys()))
                print(f"    ✓ vision_token_representation: {len(layers)} layers")

                missing_layers = [l for l in EXPECTED_LAYERS if l not in layers]
                if missing_layers:
                    print(f"    ✗ Missing vision token layers: {missing_layers}")
                    return False

                # Check one layer shape
                sample_shape = vision_token[layers[0]].shape
                print(f"      Sample layer shape: {sample_shape}")
            else:
                print("    ✗ Missing vision_token_representation")
                return False

            # Check query_token_representation
            if 'query_token_representation' in first_sample:
                query_token = first_sample['query_token_representation']
                layers = sorted(list(query_token.keys()))
                print(f"    ✓ query_token_representation: {len(layers)} layers")

                missing_layers = [l for l in EXPECTED_LAYERS if l not in layers]
                if missing_layers:
                    print(f"    ✗ Missing query token layers: {missing_layers}")
                    return False

                # Check one layer shape
                sample_shape = query_token[layers[0]].shape
                print(f"      Sample layer shape: {sample_shape}")
            else:
                print("    ✗ Missing query_token_representation")
                return False

            print(f"\n    ✓ First file contains {len(sample_ids)} samples")

        # Count total samples across all files
        total_samples = 0
        for h5_file in h5_files:
            with h5py.File(h5_file, 'r') as f:
                total_samples += len(list(f.keys()))

        print(f"  ✓ Total samples across all H5 files: {total_samples}")

        return True

    except Exception as e:
        print(f"  ✗ Error reading H5 file: {e}")
        return False

def check_dependencies():
    """Check required Python packages."""
    print("\n📦 Checking dependencies...")

    required_packages = [
        'torch',
        'h5py',
        'pandas',
        'numpy',
        'sklearn',
        'matplotlib',
        'seaborn',
        'tqdm'
    ]

    all_available = True

    for package in required_packages:
        try:
            __import__(package)
            print(f"  ✓ {package}")
        except ImportError:
            print(f"  ✗ {package} - NOT INSTALLED")
            all_available = False

    return all_available

def check_cuda():
    """Check CUDA availability."""
    print("\n🖥️  Checking CUDA...")

    try:
        import torch
        if torch.cuda.is_available():
            device_name = torch.cuda.get_device_name(0)
            memory = torch.cuda.get_device_properties(0).total_memory / (1024**3)
            print(f"  ✓ CUDA available")
            print(f"  ✓ Device: {device_name}")
            print(f"  ✓ Memory: {memory:.2f} GB")
            return True
        else:
            print("  ⚠ CUDA not available - will use CPU (slower)")
            return True  # Not a failure, just slower
    except Exception as e:
        print(f"  ✗ Error checking CUDA: {e}")
        return False

def main():
    """Run all verification checks."""
    print_header("SmolVLM Probe Training - Pre-flight Verification")

    checks = [
        ("CSV File", check_csv),
        ("H5 Files", check_h5_files),
        ("Dependencies", check_dependencies),
        ("CUDA", check_cuda)
    ]

    results = []

    for check_name, check_func in checks:
        try:
            result = check_func()
            results.append((check_name, result))
        except Exception as e:
            print(f"\n✗ Unexpected error in {check_name} check: {e}")
            results.append((check_name, False))

    # Summary
    print_header("Verification Summary")

    all_passed = True
    for check_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"  {status}: {check_name}")
        if not result:
            all_passed = False

    print()

    if all_passed:
        print("✅ All checks passed! Ready to run probe training.")
        return 0
    else:
        print("❌ Some checks failed. Please fix the issues before running probe training.")
        return 1

if __name__ == "__main__":
    import sys
    exit_code = main()
    sys.exit(exit_code)
