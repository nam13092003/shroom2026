import os
import sys
sys.path.insert(0, '/root/akhil/probe_analysis')
sys.path.insert(0, '/root/akhil/detailed_probe_analysis')

import torch
import pandas as pd
import glob
from analyze_hallucination_types import run_detailed_analysis

MODELS = [
    {"name": "Llama-3.2-11B", "h5_dir": "/root/akhil/HALP_EACL_Models/Models/LLama_32/llama_output", "csv_path": "/root/akhil/FInal_CSV_Hallucination/llama32_manually_reviewed.csv", "probe_base": "/root/akhil/probe_training_scripts/llama32_model_probe/results"},
    {"name": "Phi4-VL", "h5_dir": "/root/akhil/HALP_EACL_Models/Models/Phi4_VL/phi4_output", "csv_path": "/root/akhil/FInal_CSV_Hallucination/phi4vl_manually_reviewed.csv", "probe_base": "/root/akhil/probe_training_scripts/phi4vl_model_probe/results"},
]

all_results = []
for mc in MODELS:
    for cp in sorted(glob.glob(os.path.join(mc['probe_base'], "*/probe_model.pt"))):
        pd_dir = os.path.basename(os.path.dirname(cp))
        ckpt = torch.load(cp, map_location='cpu')
        cfg = ckpt.get('config', {})
        pi = {'probe_dir': pd_dir, 'embedding_type': cfg.get('EMBEDDING_TYPE'), 'layer_name': cfg.get('LAYER_NAME', 'N/A'), 'checkpoint_path': cp}
        od = f"/root/akhil/detailed_probe_analysis/results/{mc['name'].lower().replace('-','_').replace('.','_')}/{pd_dir}"
        if os.path.exists(f"{od}/detailed_summary.json"): continue
        os.makedirs(od, exist_ok=True)
        print(f"Running {mc['name']}/{pd_dir}...", flush=True)
        try:
            auroc, status = run_detailed_analysis(mc, pi, od)
            print(f"  ✓ {status} AUROC={auroc:.4f}" if status=="Success" else f"  ✗ {status}")
            all_results.append({'model': mc['name'], 'probe_dir': pd_dir, 'embedding_type': pi['embedding_type'], 'layer_name': pi['layer_name'], 'auroc': auroc, 'status': status})
        except Exception as e:
            print(f"  ✗ Error: {str(e)[:80]}")
            all_results.append({'model': mc['name'], 'probe_dir': pd_dir, 'embedding_type': pi['embedding_type'], 'layer_name': pi['layer_name'], 'auroc': None, 'status': f"Error: {str(e)[:80]}"})

sp = "/root/akhil/detailed_probe_analysis/detailed_analysis_summary.csv"
if all_results:
    ndf = pd.DataFrame(all_results)
    if os.path.exists(sp):
        edf = pd.read_csv(sp)
        pd.concat([edf, ndf], ignore_index=True).to_csv(sp, index=False)
    else:
        ndf.to_csv(sp, index=False)
    print(f"\nAdded {len(ndf)} results to {sp}")
print("COMPLETE!")
