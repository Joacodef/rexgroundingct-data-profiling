#!/usr/bin/env python3
import os
import json
import numpy as np
import nibabel as nib
from tqdm import tqdm
from scipy.ndimage import binary_erosion, label
from concurrent.futures import ProcessPoolExecutor, as_completed
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from scripts.config import (
    CATEGORY_MAP,
    DATASET_JSON,
    RAW_MASKS_DIR,
    DATA_DIR
)

DATA_JSON = str(DATASET_JSON)
SEG_DIR = str(RAW_MASKS_DIR)
OUTPUT_DIR = str(DATA_DIR / 'phase_1' / 'analysis_experiment_005')
MAX_WORKERS = min(32, os.cpu_count() or 4)

os.makedirs(OUTPUT_DIR, exist_ok=True)


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
            for ch_str, cat_code in cats_dict.items():
                ch_idx = int(ch_str)
                if ch_idx < data.shape[0] and cat_code in CATEGORY_MAP:
                    mask = data[ch_idx]
                    total_vol_vox = mask.sum()
                    if total_vol_vox > 0:
                        # Extract 3D connected components (lesion blobs)
                        labeled_mask, num_components = label(mask)
                        
                        comp_voxels = []
                        comp_vols_mm3 = []
                        comp_sphericities = []
                        comp_sa_v_ratios = []
                        
                        for comp_id in range(1, num_components + 1):
                            c_mask = (labeled_mask == comp_id)
                            c_voxels = int(c_mask.sum())
                            if c_voxels < 1:
                                continue
                            
                            c_vol_mm3 = float(c_voxels * voxel_vol)
                            comp_voxels.append(c_voxels)
                            comp_vols_mm3.append(c_vol_mm3)
                            
                            if c_voxels > 5:
                                eroded = binary_erosion(c_mask)
                                boundary = np.logical_and(c_mask, np.logical_not(eroded))
                                surf_vox = boundary.sum()
                                surf_mm2 = surf_vox * (zooms[0] * zooms[1])
                                
                                sphericity = (np.pi ** (1.0 / 3.0)) * ((6.0 * c_vol_mm3) ** (2.0 / 3.0)) / max(1.0, surf_mm2)
                                sa_v_ratio = surf_mm2 / max(1.0, c_vol_mm3)
                                comp_sphericities.append(float(min(1.0, sphericity)))
                                comp_sa_v_ratios.append(float(sa_v_ratio))

                        results.append({
                            'cat_code': cat_code,
                            'total_vol_mm3': float(total_vol_vox * voxel_vol),
                            'num_components': int(num_components),
                            'comp_voxels': comp_voxels,
                            'comp_vols_mm3': comp_vols_mm3,
                            'sphericities': comp_sphericities,
                            'sa_v_ratios': comp_sa_v_ratios
                        })
    except Exception:
        pass
        
    return results


def run_experiment_005():
    if not os.path.exists(DATA_JSON):
        print(f"[exp_005] Error: Dataset JSON not found at {DATA_JSON}")
        return

    print(f"[exp_005] Loading dataset from {DATA_JSON}...")
    with open(DATA_JSON, 'r') as f:
        ds = json.load(f)
        
    train_items = ds.get('train', [])
    val_items = ds.get('val', [])
    all_items = train_items + val_items
    
    print(f"[exp_005] Profiling 3D connected-component morphology across {len(all_items)} scans using {MAX_WORKERS} workers...")
    
    cat_data = {
        k: {
            'total_mask_vols_mm3': [],
            'num_components_per_finding': [],
            'all_comp_voxels': [],
            'all_comp_vols_mm3': [],
            'all_sphericities': [],
            'all_sa_v_ratios': []
        } for k in CATEGORY_MAP.keys()
    }
    
    with ProcessPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = [executor.submit(analyze_mask_morphology, item) for item in all_items]
        for f in tqdm(as_completed(futures), total=len(all_items), desc="Processing Mask Topology"):
            scan_res = f.result()
            for r in scan_res:
                code = r['cat_code']
                if code in cat_data:
                    cat_data[code]['total_mask_vols_mm3'].append(r['total_vol_mm3'])
                    cat_data[code]['num_components_per_finding'].append(r['num_components'])
                    cat_data[code]['all_comp_voxels'].extend(r['comp_voxels'])
                    cat_data[code]['all_comp_vols_mm3'].extend(r['comp_vols_mm3'])
                    cat_data[code]['all_sphericities'].extend(r['sphericities'])
                    cat_data[code]['all_sa_v_ratios'].extend(r['sa_v_ratios'])
                    
    # Aggregate stats per category
    summary_data = {}
    for k, c_name in sorted(CATEGORY_MAP.items()):
        comp_vox = cat_data[k]['all_comp_voxels']
        comp_vols = cat_data[k]['all_comp_vols_mm3']
        sph_list = cat_data[k]['all_sphericities']
        sav_list = cat_data[k]['all_sa_v_ratios']
        num_comps = cat_data[k]['num_components_per_finding']
        total_vols = cat_data[k]['total_mask_vols_mm3']
        
        p5_vox = int(np.percentile(comp_vox, 5)) if comp_vox else 0
        med_vox = int(np.median(comp_vox)) if comp_vox else 0
        p95_vox = int(np.percentile(comp_vox, 95)) if comp_vox else 0
        
        summary_data[c_name] = {
            'cat_code': k,
            'findings_count': len(total_vols),
            'total_components_count': len(comp_vox),
            'mean_components_per_finding': round(float(np.mean(num_comps)), 2) if num_comps else 0.0,
            'mean_mask_vol_mm3': round(float(np.mean(total_vols)), 2) if total_vols else 0.0,
            'component_voxel_stats': {
                'min': int(np.min(comp_vox)) if comp_vox else 0,
                'p5': p5_vox,
                'median': med_vox,
                'p95': p95_vox,
                'max': int(np.max(comp_vox)) if comp_vox else 0
            },
            'component_vol_mm3_stats': {
                'mean': round(float(np.mean(comp_vols)), 2) if comp_vols else 0.0,
                'p5': round(float(np.percentile(comp_vols, 5)), 2) if comp_vols else 0.0,
                'median': round(float(np.median(comp_vols)), 2) if comp_vols else 0.0,
                'p95': round(float(np.percentile(comp_vols, 95)), 2) if comp_vols else 0.0
            },
            'mean_sphericity': round(float(np.mean(sph_list)), 4) if sph_list else 0.0,
            'mean_sa_v_ratio': round(float(np.mean(sav_list)), 4) if sav_list else 0.0,
            'recommended_min_size_voxels': max(10, p5_vox)
        }
        
    out_json = os.path.join(OUTPUT_DIR, 'exp005_morphology_noise_pruning_summary.json')
    with open(out_json, 'w') as f:
        json.dump(summary_data, f, indent=2)

    print(f"[exp_005] Summary JSON successfully generated at {out_json}")


if __name__ == '__main__':
    run_experiment_005()
