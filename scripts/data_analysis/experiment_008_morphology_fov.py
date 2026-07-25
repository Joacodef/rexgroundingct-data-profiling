#!/usr/bin/env python3
import os
import json
import numpy as np
import nibabel as nib
from tqdm import tqdm
from scipy.ndimage import binary_erosion
from concurrent.futures import ProcessPoolExecutor, as_completed

DATA_JSON = 'data/dataset.json'
SEG_DIR = 'data/raw/segmentations'
OUTPUT_DIR = 'data/analysis_experiment_008'
LOG_FILE = 'logs/phase_1_data_profiling/exp_008_morphology_fov.md'
MAX_WORKERS = 16

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

CATEGORY_MAP = {
    '1a': 'Bronchial wall thickening',
    '1b': 'Bronchiectasis',
    '1c': 'Emphysema',
    '1d': 'Septal thickening',
    '1e': 'Micronodules',
    '1f': 'Other non-focal',
    '2a': 'Linear opacities',
    '2b': 'Atelectasis / consolidation',
    '2c': 'Ground-glass opacity',
    '2d': 'Pulmonary nodules / masses',
    '2e': 'Pleural effusion / thickening',
    '2f': 'Honeycombing',
    '2g': 'Pneumothorax',
    '2h': 'Other focal'
}

def analyze_mask_morphology(item):
    name = item['name']
    seg_path = os.path.join(SEG_DIR, name)
    cats_dict = item.get('categories', {})
    
    results = []
    if not os.path.exists(seg_path):
        return results

    try:
        seg = nib.load(seg_path)
        data = seg.get_fdata() > 0
        zooms = [float(z) for z in seg.header.get_zooms()[:3]]
        voxel_vol = zooms[0] * zooms[1] * zooms[2]
        
        if data.ndim == 4:
            for ch_idx in range(data.shape[3]):
                ch_str = str(ch_idx)
                if ch_str in cats_dict and cats_dict[ch_str] in CATEGORY_MAP:
                    mask = data[..., ch_idx]
                    vol_vox = mask.sum()
                    if vol_vox > 5:
                        # Estimate surface area via binary erosion boundary
                        eroded = binary_erosion(mask)
                        boundary = np.logical_and(mask, np.logical_not(eroded))
                        surf_vox = boundary.sum()
                        
                        vol_mm3 = vol_vox * voxel_vol
                        surf_mm2 = surf_vox * (zooms[0] * zooms[1])
                        
                        # Sphericity S = pi^(1/3) * (6 * V)^(2/3) / A
                        sphericity = (np.pi ** (1.0 / 3.0)) * ((6.0 * vol_mm3) ** (2.0 / 3.0)) / max(1.0, surf_mm2)
                        sa_v_ratio = surf_mm2 / max(1.0, vol_mm3)
                        
                        results.append({
                            'cat_code': cats_dict[ch_str],
                            'vol_mm3': float(vol_mm3),
                            'surf_mm2': float(surf_mm2),
                            'sphericity': float(min(1.0, sphericity)),
                            'sa_v_ratio': float(sa_v_ratio)
                        })
    except Exception:
        pass
        
    return results

def run_experiment_008():
    print("[exp_008] Loading dataset.json...")
    with open(DATA_JSON, 'r') as f:
        ds = json.load(f)
        
    train_items = ds.get('train', [])
    val_items = ds.get('validation', [])
    all_items = train_items + val_items
    
    print(f"[exp_008] Profiling mask morphology (sphericity & SA/V ratio) for {len(all_items)} scans using {MAX_WORKERS} workers...")
    
    cat_morphology = {k: {'sphericity': [], 'sa_v_ratio': [], 'vol_mm3': []} for k in CATEGORY_MAP.keys()}
    
    with ProcessPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = [executor.submit(analyze_mask_morphology, item) for item in all_items]
        for f in tqdm(as_completed(futures), total=len(all_items)):
            scan_res = f.result()
            for r in scan_res:
                code = r['cat_code']
                if code in cat_morphology:
                    cat_morphology[code]['sphericity'].append(r['sphericity'])
                    cat_morphology[code]['sa_v_ratio'].append(r['sa_v_ratio'])
                    cat_morphology[code]['vol_mm3'].append(r['vol_mm3'])
                    
    # Aggregate stats
    summary_data = {}
    for k, c_name in CATEGORY_MAP.items():
        sph_list = cat_morphology[k]['sphericity']
        sav_list = cat_morphology[k]['sa_v_ratio']
        vol_list = cat_morphology[k]['vol_mm3']
        
        summary_data[c_name] = {
            'count': len(sph_list),
            'mean_sphericity': float(np.mean(sph_list)) if sph_list else 0.0,
            'std_sphericity': float(np.std(sph_list)) if sph_list else 0.0,
            'mean_sa_v_ratio': float(np.mean(sav_list)) if sav_list else 0.0,
            'mean_vol_mm3': float(np.mean(vol_list)) if vol_list else 0.0
        }
        
    with open(os.path.join(OUTPUT_DIR, 'morphology_fov_summary.json'), 'w') as f:
        json.dump(summary_data, f, indent=2)
        
    # Write experiment log markdown
    with open(LOG_FILE, 'w') as f:
        f.write("# Experiment Log 008: [Phase 1] Morphological Sphericity & Surface-to-Volume Ratio Analysis\n\n")
        f.write("**Status**: Completed\n\n")
        f.write("## 1. Quantitative Summary per Pathology\n\n")
        f.write("| Category Name | Sample Count | Mean Volume (mm³) | Mean Sphericity | Mean SA/V Ratio (mm⁻¹) |\n")
        f.write("|---|---|---|---|---|\n")
        for k in sorted(list(CATEGORY_MAP.keys())):
            c_name = CATEGORY_MAP[k]
            st = summary_data[c_name]
            f.write(f"| **{c_name}** | {st['count']} | `{st['mean_vol_mm3']:.1f}` | `{st['mean_sphericity']:.3f}` | `{st['mean_sa_v_ratio']:.4f}` |\n")
        f.write("\n---\n")

    print("[exp_008] Completed successfully!")

if __name__ == '__main__':
    run_experiment_008()
