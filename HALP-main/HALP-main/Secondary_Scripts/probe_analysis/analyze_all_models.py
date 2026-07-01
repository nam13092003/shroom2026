"""
Analyze All Models and All Probes - Category Performance Analysis
==================================================================
This script runs category analysis for all 8 models and all their probes (88 total analyses).

Models:
- Gemma3-12B (42 layers)
- FastVLM-7B (32 layers)
- LLaVA-Next-8B (32 layers)
- Molmo-V1 (28 layers)
- Qwen2.5-VL-7B (28 layers)
- Llama-3.2-11B-Vision (32 layers)
- Phi4-VL (32 layers)
- SmolVLM2-2.2B (24 layers)

Each model has 11 probes:
- 1 vision_only
- 5 vision_token (layers: 0, n/4, n/2, 3n/4, n-1)
- 5 query_token (layers: 0, n/4, n/2, 3n/4, n-1)
"""

import os
import subprocess
import json
import pandas as pd
from datetime import datetime
import logging

# Setup logging
log_file = f'/root/akhil/probe_analysis/batch_analysis_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ==================== MODEL CONFIGURATIONS ====================

MODEL_CONFIGS = {
    "gemma3": {
        "model_name": "Gemma3-12B",
        "num_layers": 42,
        "h5_dir": "/root/akhil/HALP_EACL_Models/Models/Gemma3/gemma3_output",
        "csv_path": "/root/akhil/FInal_CSV_Hallucination/gemma3_manually_reviewed.csv",
        "probe_base": "/root/akhil/probe_training_scripts/gemma3_model_probe/results",
        "output_base": "/root/akhil/probe_analysis/results/gemma3",
        "vision_dim": 1152,
        "text_dim": 3072
    },
    "fastvlm": {
        "model_name": "FastVLM-7B",
        "num_layers": 32,
        "h5_dir": "/root/akhil/HALP_EACL_Models/Models/FastVLM/fastvlm_output",
        "csv_path": "/root/akhil/FInal_CSV_Hallucination/fastvlm_manually_reviewed.csv",
        "probe_base": "/root/akhil/probe_training_scripts/fastvlm_model_probe/results",
        "output_base": "/root/akhil/probe_analysis/results/fastvlm",
        "vision_dim": 1024,
        "text_dim": 4096
    },
    "llava_next": {
        "model_name": "LLaVA-Next-8B",
        "num_layers": 32,
        "h5_dir": "/root/akhil/HALP_EACL_Models/Models/LLaVA_Next/llava_next_output",
        "csv_path": "/root/akhil/FInal_CSV_Hallucination/llava_next_manually_reviewed.csv",
        "probe_base": "/root/akhil/probe_training_scripts/llava_next_model_probe/results",
        "output_base": "/root/akhil/probe_analysis/results/llava_next",
        "vision_dim": 1024,
        "text_dim": 4096
    },
    "molmo": {
        "model_name": "Molmo-V1",
        "num_layers": 28,
        "h5_dir": "/root/akhil/HALP_EACL_Models/Models/Molmo/molmo_output",
        "csv_path": "/root/akhil/FInal_CSV_Hallucination/molmo_manually_reviewed.csv",
        "probe_base": "/root/akhil/probe_training_scripts/molmo_model_probe/results",
        "output_base": "/root/akhil/probe_analysis/results/molmo",
        "vision_dim": 1152,
        "text_dim": 4096
    },
    "qwen": {
        "model_name": "Qwen2.5-VL-7B",
        "num_layers": 28,
        "h5_dir": "/root/akhil/HALP_EACL_Models/Models/Qwen/qwen_output",
        "csv_path": "/root/akhil/FInal_CSV_Hallucination/qwen_manually_reviewed.csv",
        "probe_base": "/root/akhil/probe_training_scripts/qwen_model_probe/results",
        "output_base": "/root/akhil/probe_analysis/results/qwen",
        "vision_dim": 1280,
        "text_dim": 3584
    },
    "llama": {
        "model_name": "Llama-3.2-11B-Vision",
        "num_layers": 32,
        "h5_dir": "/root/akhil/HALP_EACL_Models/Models/Llama/llama_output",
        "csv_path": "/root/akhil/FInal_CSV_Hallucination/llama_manually_reviewed.csv",
        "probe_base": "/root/akhil/probe_training_scripts/llama_model_probe/results",
        "output_base": "/root/akhil/probe_analysis/results/llama",
        "vision_dim": 1280,
        "text_dim": 4096
    },
    "phi4": {
        "model_name": "Phi4-VL",
        "num_layers": 32,
        "h5_dir": "/root/akhil/HALP_EACL_Models/Models/Phi4/phi4_output",
        "csv_path": "/root/akhil/FInal_CSV_Hallucination/phi4_manually_reviewed.csv",
        "probe_base": "/root/akhil/probe_training_scripts/phi4_model_probe/results",
        "output_base": "/root/akhil/probe_analysis/results/phi4",
        "vision_dim": 1024,
        "text_dim": 3072
    },
    "smolvlm": {
        "model_name": "SmolVLM2-2.2B",
        "num_layers": 24,
        "h5_dir": "/root/akhil/HALP_EACL_Models/Models/Smol_VL/smolvlm_output",
        "csv_path": "/root/akhil/FInal_CSV_Hallucination/smolvlm_manually_reviewed.csv",
        "probe_base": "/root/akhil/probe_training_scripts/smolvlm_model_probe/results",
        "output_base": "/root/akhil/probe_analysis/results/smolvlm",
        "vision_dim": 1152,
        "text_dim": 2048
    }
}

# ==================== PROBE GENERATION ====================

def get_layer_indices(num_layers):
    """Calculate layer indices for a given number of layers."""
    return {
        "layer_0": 0,
        "layer_n4": num_layers // 4,
        "layer_n2": num_layers // 2,
        "layer_3n4": (3 * num_layers) // 4,
        "layer_nm1": num_layers - 1
    }

def generate_probe_configs(model_key, config):
    """Generate all probe configurations for a model."""
    num_layers = config["num_layers"]
    layers = get_layer_indices(num_layers)

    probes = []

    # Vision only probe
    probes.append({
        "model_key": model_key,
        "model_name": config["model_name"],
        "embedding_type": "vision_only_representation",
        "layer_name": None,
        "input_dim": config["vision_dim"],
        "probe_dir": "vision_only",
        "output_name": "vision_only"
    })

    # Vision token probes
    for layer_key, layer_idx in layers.items():
        probes.append({
            "model_key": model_key,
            "model_name": config["model_name"],
            "embedding_type": "vision_token_representation",
            "layer_name": f"layer_{layer_idx}",
            "input_dim": config["text_dim"],
            "probe_dir": f"vision_token_layer{layer_idx}",
            "output_name": f"vision_token_layer{layer_idx}"
        })

    # Query token probes
    for layer_key, layer_idx in layers.items():
        probes.append({
            "model_key": model_key,
            "model_name": config["model_name"],
            "embedding_type": "query_token_representation",
            "layer_name": f"layer_{layer_idx}",
            "input_dim": config["text_dim"],
            "probe_dir": f"query_token_layer{layer_idx}",
            "output_name": f"query_token_layer{layer_idx}"
        })

    return probes

# ==================== ANALYSIS SCRIPT TEMPLATE ====================

ANALYSIS_TEMPLATE = '''"""
Category Analysis for {model_name} - {probe_name}
Auto-generated analysis script
"""

import os
import h5py
import pandas as pd
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score
import json
import logging
from datetime import datetime
import glob
from tqdm import tqdm

# Configuration
CONFIG = {{
    "MODEL_NAME": "{model_name}",
    "EMBEDDING_TYPE": "{embedding_type}",
    "LAYER_NAME": {layer_name},

    "H5_DIR": "{h5_dir}",
    "CSV_PATH": "{csv_path}",
    "CATEGORY_CSV_PATH": "/root/akhil/final_data/sampled_10k_relational_dataset.csv",

    "MODEL_CHECKPOINT": "{checkpoint_path}",
    "OUTPUT_DIR": "{output_dir}",

    "TARGET_COLUMN": "is_hallucinating_manual",
    "TEST_SIZE": 0.2,
    "RANDOM_STATE": 42,

    "LAYER_SIZES": [512, 256, 128],
    "DROPOUT_RATE": 0.3,

    "DEVICE": "cuda" if torch.cuda.is_available() else "cpu"
}}

# Setup logging
os.makedirs(CONFIG["OUTPUT_DIR"], exist_ok=True)
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
log_file = os.path.join(CONFIG["OUTPUT_DIR"], f'analysis_{{timestamp}}.log')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Import the core functions from the main analysis script
import sys
sys.path.insert(0, '/root/akhil/probe_analysis')

from analyze_probe_by_category import (
    load_hallucination_labels,
    load_category_metadata,
    load_embeddings_from_h5,
    HallucinationProbe,
    get_predictions,
    analyze_by_category,
    analyze_by_source,
    generate_markdown_report,
    EmbeddingDataset
)

def verify_paths():
    """Verify all required paths exist."""
    logger.info("=" * 80)
    logger.info("VERIFYING PATHS")
    logger.info("=" * 80)

    paths = {{
        "H5 Directory": CONFIG["H5_DIR"],
        "Hallucination CSV": CONFIG["CSV_PATH"],
        "Category CSV": CONFIG["CATEGORY_CSV_PATH"],
        "Model Checkpoint": CONFIG["MODEL_CHECKPOINT"]
    }}

    all_valid = True
    for name, path in paths.items():
        exists = os.path.exists(path)
        status = "✓" if exists else "✗"
        logger.info(f"{{status}} {{name}}: {{path}}")
        if not exists:
            all_valid = False

    if not all_valid:
        raise FileNotFoundError("Some required paths do not exist.")

    logger.info("\\n✓ All paths verified!\\n")

def main():
    logger.info("=" * 80)
    logger.info(f"PROBE CATEGORY ANALYSIS")
    logger.info(f"{{CONFIG['MODEL_NAME']}} - {{CONFIG['EMBEDDING_TYPE']}}" + (f" / {{CONFIG['LAYER_NAME']}}" if CONFIG['LAYER_NAME'] else ""))
    logger.info("=" * 80)

    verify_paths()

    # Load data
    labels_dict = load_hallucination_labels(CONFIG["CSV_PATH"])
    category_map = load_category_metadata(CONFIG["CATEGORY_CSV_PATH"])

    embeddings, labels, question_ids = load_embeddings_from_h5(
        CONFIG["H5_DIR"],
        CONFIG["EMBEDDING_TYPE"],
        labels_dict,
        layer_name=CONFIG["LAYER_NAME"]
    )

    logger.info(f"\\nTotal samples: {{len(embeddings)}}")
    logger.info(f"Matched with categories: {{len([qid for qid in question_ids if qid in category_map])}}/{{len(question_ids)}}")

    # Create train/test split
    logger.info("\\n" + "=" * 80)
    logger.info("CREATING TRAIN/TEST SPLIT")
    logger.info("=" * 80)

    X_train, X_test, y_train, y_test, train_ids, test_ids = train_test_split(
        embeddings, labels, question_ids,
        test_size=CONFIG["TEST_SIZE"],
        random_state=CONFIG["RANDOM_STATE"],
        stratify=labels
    )

    logger.info(f"Train: {{len(X_train)}}, Test: {{len(X_test)}}")

    # Load model
    logger.info("\\n" + "=" * 80)
    logger.info("LOADING MODEL")
    logger.info("=" * 80)

    checkpoint = torch.load(CONFIG["MODEL_CHECKPOINT"], map_location=CONFIG["DEVICE"])
    input_dim = checkpoint['input_dim']

    model = HallucinationProbe(
        input_dim=input_dim,
        layer_sizes=CONFIG["LAYER_SIZES"],
        dropout_rate=CONFIG["DROPOUT_RATE"]
    ).to(CONFIG["DEVICE"])

    model.load_state_dict(checkpoint['model_state_dict'])
    logger.info("✓ Model loaded!")

    # Get predictions
    logger.info("\\n" + "=" * 80)
    logger.info("GETTING PREDICTIONS")
    logger.info("=" * 80)

    test_probs = get_predictions(model, X_test)
    logger.info(f"✓ Generated {{len(test_probs)}} predictions")

    # Analyze
    category_df, overall_auroc = analyze_by_category(test_ids, y_test, test_probs, category_map)
    source_df = analyze_by_source(test_ids, y_test, test_probs, category_map)
    generate_markdown_report(category_df, source_df, overall_auroc)

    # Save summary
    summary = {{
        'model_name': CONFIG['MODEL_NAME'],
        'embedding_type': CONFIG['EMBEDDING_TYPE'],
        'layer_name': CONFIG['LAYER_NAME'],
        'timestamp': timestamp,
        'overall_auroc': float(overall_auroc),
        'test_samples': len(X_test)
    }}

    with open(os.path.join(CONFIG["OUTPUT_DIR"], 'analysis_summary.json'), 'w') as f:
        json.dump(summary, f, indent=2)

    logger.info("\\n" + "=" * 80)
    logger.info("ANALYSIS COMPLETED!")
    logger.info("=" * 80)

    return overall_auroc

if __name__ == "__main__":
    main()
'''

# ==================== SCRIPT GENERATION ====================

def generate_analysis_script(probe_config, model_config):
    """Generate analysis script for a specific probe."""

    checkpoint_path = os.path.join(
        model_config["probe_base"],
        probe_config["probe_dir"],
        "probe_model.pt"
    )

    output_dir = os.path.join(
        model_config["output_base"],
        probe_config["output_name"]
    )

    layer_name_str = f'"{probe_config["layer_name"]}"' if probe_config["layer_name"] else "None"

    script_content = ANALYSIS_TEMPLATE.format(
        model_name=probe_config["model_name"],
        probe_name=probe_config["output_name"],
        embedding_type=probe_config["embedding_type"],
        layer_name=layer_name_str,
        h5_dir=model_config["h5_dir"],
        csv_path=model_config["csv_path"],
        checkpoint_path=checkpoint_path,
        output_dir=output_dir
    )

    return script_content, checkpoint_path, output_dir

# ==================== EXECUTION ====================

def run_analysis(script_path, probe_name):
    """Run a single analysis script."""
    logger.info(f"\\n{'='*80}")
    logger.info(f"Running: {probe_name}")
    logger.info(f"{'='*80}")

    try:
        result = subprocess.run(
            ["python3", script_path],
            capture_output=True,
            text=True,
            timeout=600  # 10 minute timeout
        )

        if result.returncode == 0:
            logger.info(f"✓ SUCCESS: {probe_name}")
            # Extract AUROC from output
            for line in result.stdout.split('\\n'):
                if 'Overall Test AUROC:' in line:
                    auroc = float(line.split(':')[-1].strip())
                    return True, auroc
            return True, None
        else:
            logger.error(f"✗ FAILED: {probe_name}")
            logger.error(f"Error: {result.stderr}")
            return False, None

    except subprocess.TimeoutExpired:
        logger.error(f"✗ TIMEOUT: {probe_name}")
        return False, None
    except Exception as e:
        logger.error(f"✗ ERROR: {probe_name} - {str(e)}")
        return False, None

def main():
    logger.info("=" * 80)
    logger.info("BATCH ANALYSIS: ALL MODELS AND PROBES")
    logger.info("=" * 80)
    logger.info(f"Total models: {len(MODEL_CONFIGS)}")
    logger.info(f"Probes per model: 11")
    logger.info(f"Total analyses: {len(MODEL_CONFIGS) * 11}")
    logger.info("")

    # Track results
    results = []
    scripts_dir = "/root/akhil/probe_analysis/generated_scripts"
    os.makedirs(scripts_dir, exist_ok=True)

    # Generate and run all analyses
    for model_key, model_config in MODEL_CONFIGS.items():
        logger.info(f"\\n{'='*80}")
        logger.info(f"Processing: {model_config['model_name']}")
        logger.info(f"{'='*80}")

        probes = generate_probe_configs(model_key, model_config)
        logger.info(f"Generated {len(probes)} probe configurations")

        for i, probe in enumerate(probes, 1):
            # Generate script
            script_content, checkpoint_path, output_dir = generate_analysis_script(probe, model_config)

            # Check if checkpoint exists
            if not os.path.exists(checkpoint_path):
                logger.warning(f"⚠ SKIP: {probe['output_name']} - Checkpoint not found: {checkpoint_path}")
                results.append({
                    'model': probe['model_name'],
                    'probe': probe['output_name'],
                    'status': 'SKIP',
                    'auroc': None,
                    'reason': 'Checkpoint not found'
                })
                continue

            # Save script
            script_filename = f"{model_key}_{probe['output_name']}_analysis.py"
            script_path = os.path.join(scripts_dir, script_filename)

            with open(script_path, 'w') as f:
                f.write(script_content)

            # Run analysis
            success, auroc = run_analysis(script_path, f"{model_key}/{probe['output_name']}")

            results.append({
                'model': probe['model_name'],
                'probe': probe['output_name'],
                'status': 'SUCCESS' if success else 'FAILED',
                'auroc': auroc,
                'checkpoint': checkpoint_path,
                'output_dir': output_dir
            })

    # Save results summary
    logger.info("\\n" + "=" * 80)
    logger.info("BATCH ANALYSIS COMPLETE")
    logger.info("=" * 80)

    results_df = pd.DataFrame(results)
    results_csv = "/root/akhil/probe_analysis/batch_analysis_results.csv"
    results_df.to_csv(results_csv, index=False)
    logger.info(f"\\nResults saved to: {results_csv}")

    # Print summary
    total = len(results)
    success = len(results_df[results_df['status'] == 'SUCCESS'])
    failed = len(results_df[results_df['status'] == 'FAILED'])
    skipped = len(results_df[results_df['status'] == 'SKIP'])

    logger.info(f"\\nSummary:")
    logger.info(f"  Total: {total}")
    logger.info(f"  ✓ Success: {success}")
    logger.info(f"  ✗ Failed: {failed}")
    logger.info(f"  ⚠ Skipped: {skipped}")

    # Print results by model
    logger.info(f"\\n{'='*80}")
    logger.info("RESULTS BY MODEL")
    logger.info(f"{'='*80}")

    for model_name in results_df['model'].unique():
        model_results = results_df[results_df['model'] == model_name]
        logger.info(f"\\n{model_name}:")
        for _, row in model_results.iterrows():
            auroc_str = f"AUROC: {row['auroc']:.4f}" if row['auroc'] else "No AUROC"
            logger.info(f"  [{row['status']}] {row['probe']:40s} {auroc_str}")

if __name__ == "__main__":
    main()
