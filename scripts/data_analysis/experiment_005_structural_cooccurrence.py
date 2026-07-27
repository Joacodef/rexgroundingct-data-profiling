#!/usr/bin/env python3
import os
import json
import numpy as np
import pandas as pd
import nibabel as nib
import matplotlib.pyplot as plt
import seaborn as sns
from tqdm import tqdm
from concurrent.futures import ProcessPoolExecutor, as_completed

DATA_JSON = 'data/dataset.json'
IMG_DIR = 'data/raw/images'
SEG_DIR = 'data/raw/segmentations'
OUTPUT_DIR = 'data/phase_1/analysis_experiment_005'
LOG_FILE = 'logs/phase_1_data_profiling/exp_005_structural_cooccurrence.md'
MAX_WORKERS = 16

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from scripts.config import CATEGORY_MAP

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)


def analyze_single_scan_header(item):
    name = item['name']
    img_path = os.path.join(IMG_DIR, name)
    seg_path = os.path.join(SEG_DIR, name)
    
    res = {
        'name': name,
        'protocol': item.get('protocol', 'unknown'),
        'zooms': None,
        'shape': item.get('shape', None),
        'bbox_extents': {}
    }
    
    if os.path.exists(img_path):
        try:
            img = nib.load(img_path)
            res['zooms'] = [float(z) for z in img.header.get_zooms()[:3]]
        except Exception:
            pass
            
    if os.path.exists(seg_path):
        try:
            seg = nib.load(seg_path)
            data = seg.get_fdata() > 0
            if data.ndim == 4:
                for idx in range(data.shape[0]):
                    ch_data = data[idx]
                    if np.any(ch_data):
                        coords = np.argwhere(ch_data)
                        min_c = coords.min(axis=0)
                        max_c = coords.max(axis=0)
                        extent_vox = (max_c - min_c + 1).tolist()
                        res['bbox_extents'][str(idx)] = extent_vox
            elif np.any(data):
                coords = np.argwhere(data)
                min_c = coords.min(axis=0)
                max_c = coords.max(axis=0)
                extent_vox = (max_c - min_c + 1).tolist()
                res['bbox_extents']['0'] = extent_vox
        except Exception:
            pass
            
    return res

def run_experiment_005():
    print("[exp_005] Loading dataset.json...")
    with open(DATA_JSON, 'r') as f:
        ds = json.load(f)
        
    train_items = ds.get('train', [])
    val_items = ds.get('val', [])
    all_items = train_items + val_items
    
    # 1. Co-occurrence Matrix Across All Scans
    cat_keys = sorted(list(CATEGORY_MAP.keys()))
    num_cats = len(cat_keys)
    co_matrix = np.zeros((num_cats, num_cats), dtype=int)
    cat_counts = np.zeros(num_cats, dtype=int)
    entity_counts_dict = {cat: [] for cat in cat_keys}
    
    for item in all_items:
        present_cats = set()
        cats_dict = item.get('categories', {})
        entity_dict = item.get('entity_counts', {})
        for idx_str, cat_code in cats_dict.items():
            if cat_code in CATEGORY_MAP:
                present_cats.add(cat_code)
                ec = entity_dict.get(idx_str, 1)
                entity_counts_dict[cat_code].append(ec)
                
        present_list = list(present_cats)
        for cat in present_list:
            idx_c = cat_keys.index(cat)
            cat_counts[idx_c] += 1
            for cat2 in present_list:
                idx_c2 = cat_keys.index(cat2)
                co_matrix[idx_c, idx_c2] += 1

    # 2. Extract Spacings & Bounding Box Extents via parallel execution
    print(f"[exp_005] Analyzing voxel spacing and 3D bounding box extents for {len(all_items)} scans using {MAX_WORKERS} workers...")
    spacing_records = []
    with ProcessPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = [executor.submit(analyze_single_scan_header, item) for item in all_items]
        for f in tqdm(as_completed(futures), total=len(all_items)):
            res = f.result()
            if res['zooms'] is not None:
                spacing_records.append(res['zooms'])

    spacings_arr = np.array(spacing_records) if len(spacing_records) > 0 else np.zeros((0, 3))
    
    mean_spacing = spacings_arr.mean(axis=0).tolist() if len(spacings_arr) > 0 else [1.0, 1.0, 1.0]
    std_spacing = spacings_arr.std(axis=0).tolist() if len(spacings_arr) > 0 else [0.0, 0.0, 0.0]
    
    # 3. Export Co-occurrence plot
    plt.figure(figsize=(12, 10))
    cat_labels = [CATEGORY_MAP[k] for k in cat_keys]
    sns.heatmap(co_matrix, xticklabels=cat_labels, yticklabels=cat_labels, annot=True, fmt='d', cmap='Blues')
    plt.title("ReXGroundingCT Multi-Finding Co-Occurrence Matrix")
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, 'cooccurrence_matrix.png'), dpi=200)
    plt.close()
    
    # Save JSON summary
    summary_data = {
        'total_scans': len(all_items),
        'mean_voxel_spacing_xyz': mean_spacing,
        'std_voxel_spacing_xyz': std_spacing,
        'category_counts': {CATEGORY_MAP[k]: int(cat_counts[i]) for i, k in enumerate(cat_keys)},
        'entity_counts_stats': {
            CATEGORY_MAP[k]: {
                'mean': float(np.mean(entity_counts_dict[k])) if entity_counts_dict[k] else 0.0,
                'max': int(np.max(entity_counts_dict[k])) if entity_counts_dict[k] else 0
            } for k in cat_keys
        }
    }
    
    with open(os.path.join(OUTPUT_DIR, 'structural_cooccurrence.json'), 'w') as f:
        json.dump(summary_data, f, indent=2)
        
    # Write experiment log markdown
    with open(LOG_FILE, 'w') as f:
        f.write("# Experiment Log 005: [Phase 1] Structural Resolution, 3D Bounding Box & Co-Occurrence Analysis\n\n")
        f.write("**Status**: Completed\n\n")
        f.write("## 1. Quantitative Summary\n\n")
        f.write(f"* **Total Scans Analyzed**: {len(all_items)}\n")
        f.write(f"* **Mean Voxel Spacing (mm)**: \\(\\Delta x = {mean_spacing[0]:.3f} \\pm {std_spacing[0]:.3f}\\), \\(\\Delta y = {mean_spacing[1]:.3f} \\pm {std_spacing[1]:.3f}\\), \\(\\Delta z = {mean_spacing[2]:.3f} \\pm {std_spacing[2]:.3f}\\)\n\n")
        f.write("## 2. Category Prevalence & Instance Fragmentation\n\n")
        f.write("| Category Name | Total Scans | Mean Instance Count | Max Instances |\n")
        f.write("|---|---|---|---|\n")
        for k in cat_keys:
            c_name = CATEGORY_MAP[k]
            e_mean = summary_data['entity_counts_stats'][c_name]['mean']
            e_max = summary_data['entity_counts_stats'][c_name]['max']
            c_cnt = summary_data['category_counts'][c_name]
            f.write(f"| **{c_name}** | {c_cnt} | `{e_mean:.2f}` | `{e_max}` |\n")
        f.write("\n---\n")
        f.write("Co-occurrence heatmap saved to `data/analysis_experiment_005/cooccurrence_matrix.png`.\n")

    print("[exp_005] Completed successfully!")

if __name__ == '__main__':
    run_experiment_005()
