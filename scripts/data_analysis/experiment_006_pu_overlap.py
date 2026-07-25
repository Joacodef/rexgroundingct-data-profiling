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
SEG_DIR = 'data/raw/segmentations'
OUTPUT_DIR = 'data/analysis_experiment_006'
LOG_FILE = 'logs/phase_1_data_profiling/exp_006_pu_overlap.md'
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

def analyze_scan_voxel_overlap(item):
    name = item['name']
    seg_path = os.path.join(SEG_DIR, name)
    cats_dict = item.get('categories', {})
    
    cat_keys = sorted(list(CATEGORY_MAP.keys()))
    num_cats = len(cat_keys)
    intersection_mat = np.zeros((num_cats, num_cats), dtype=np.int64)
    union_mat = np.zeros((num_cats, num_cats), dtype=np.int64)
    
    if not os.path.exists(seg_path) or len(cats_dict) < 2:
        return intersection_mat, union_mat

    try:
        seg = nib.load(seg_path)
        data = seg.get_fdata() > 0
        if data.ndim == 4 and data.shape[3] > 1:
            channel_cats = []
            for ch_idx in range(data.shape[3]):
                ch_str = str(ch_idx)
                if ch_str in cats_dict and cats_dict[ch_str] in CATEGORY_MAP:
                    channel_cats.append((ch_idx, cats_dict[ch_str]))
                    
            for i in range(len(channel_cats)):
                ch_i, cat_i = channel_cats[i]
                idx_i = cat_keys.index(cat_i)
                mask_i = data[..., ch_i]
                for j in range(i, len(channel_cats)):
                    ch_j, cat_j = channel_cats[j]
                    idx_j = cat_keys.index(cat_j)
                    mask_j = data[..., ch_j]
                    
                    inter = np.logical_and(mask_i, mask_j).sum()
                    union = np.logical_or(mask_i, mask_j).sum()
                    
                    intersection_mat[idx_i, idx_j] += inter
                    intersection_mat[idx_j, idx_i] += inter
                    union_mat[idx_i, idx_j] += union
                    union_mat[idx_j, idx_i] += union
    except Exception:
        pass
        
    return intersection_mat, union_mat

def run_experiment_006():
    print("[exp_006] Loading dataset.json...")
    with open(DATA_JSON, 'r') as f:
        ds = json.load(f)
        
    val_items = ds.get('validation', [])
    train_items = ds.get('train', [])
    
    cat_keys = sorted(list(CATEGORY_MAP.keys()))
    num_cats = len(cat_keys)
    
    # 1. Compute Voxel-Level Inter-Class Overlap in Validation Split
    print(f"[exp_006] Analyzing voxel-level inter-class overlap across {len(val_items)} validation scans...")
    total_inter = np.zeros((num_cats, num_cats), dtype=np.int64)
    total_union = np.zeros((num_cats, num_cats), dtype=np.int64)
    
    with ProcessPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = [executor.submit(analyze_scan_voxel_overlap, item) for item in val_items]
        for f in tqdm(as_completed(futures), total=len(val_items)):
            inter, union = f.result()
            total_inter += inter
            total_union += union
            
    iou_matrix = np.zeros((num_cats, num_cats), dtype=np.float64)
    nz_mask = total_union > 0
    iou_matrix[nz_mask] = total_inter[nz_mask] / total_union[nz_mask].astype(np.float64)
    
    # 2. Compute PU Background Contamination Ratios
    # In Train split (~1 mask/scan), average findings = 1.0. In Val split (~3 masks/scan), average findings = 2.8.
    val_cooccur_counts = np.zeros(num_cats, dtype=float)
    val_total_scans = len(val_items)
    
    for item in val_items:
        present_cats = set(item.get('categories', {}).values())
        for c in present_cats:
            if c in cat_keys:
                idx_c = cat_keys.index(c)
                val_cooccur_counts[idx_c] += 1
                
    pu_unannotated_prob = {}
    for idx, k in enumerate(cat_keys):
        c_name = CATEGORY_MAP[k]
        val_freq = val_cooccur_counts[idx] / max(1, val_total_scans)
        # Train annotated frequency
        train_cnt = sum(1 for item in train_items if k in item.get('categories', {}).values())
        train_freq = train_cnt / max(1, len(train_items))
        # Expected unannotated contamination in train background
        unannotated_bias = max(0.0, val_freq - train_freq)
        pu_unannotated_prob[c_name] = {
            'train_annotated_rate': float(train_freq),
            'val_exhaustive_rate': float(val_freq),
            'estimated_pu_unannotated_bias': float(unannotated_bias)
        }

    # 3. Export Heatmap Plot
    plt.figure(figsize=(12, 10))
    cat_labels = [CATEGORY_MAP[k] for k in cat_keys]
    sns.heatmap(iou_matrix, xticklabels=cat_labels, yticklabels=cat_labels, annot=True, fmt='.3f', cmap='Oranges')
    plt.title("Validation Multi-Label Voxel-Level Inter-Class IoU Matrix")
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, 'inter_class_iou_matrix.png'), dpi=200)
    plt.close()
    
    # Save JSON summary
    summary_data = {
        'pu_unannotated_probabilities': pu_unannotated_prob,
        'mean_inter_class_iou': float(iou_matrix[np.triu_indices(num_cats, k=1)].mean())
    }
    
    with open(os.path.join(OUTPUT_DIR, 'pu_overlap_summary.json'), 'w') as f:
        json.dump(summary_data, f, indent=2)
        
    # Write experiment log markdown
    with open(LOG_FILE, 'w') as f:
        f.write("# Experiment Log 006: [Phase 1] Positive-Unlabeled (PU) Noise & Inter-Class Overlap Analysis\n\n")
        f.write("**Status**: Completed\n\n")
        f.write("## 1. Executive Summary\n\n")
        f.write(f"* **Mean Off-Diagonal Voxel IoU**: `{summary_data['mean_inter_class_iou']:.4f}`\n\n")
        f.write("## 2. PU Unannotated Contamination Estimation (Train vs Val Rates)\n\n")
        f.write("| Category Name | Train Annotated Rate | Val Exhaustive Rate | Estimated PU Unannotated Bias |\n")
        f.write("|---|---|---|---|\n")
        for k in cat_keys:
            c_name = CATEGORY_MAP[k]
            tr_r = pu_unannotated_prob[c_name]['train_annotated_rate']
            val_r = pu_unannotated_prob[c_name]['val_exhaustive_rate']
            pu_b = pu_unannotated_prob[c_name]['estimated_pu_unannotated_bias']
            f.write(f"| **{c_name}** | `{tr_r:.3f}` | `{val_r:.3f}` | `{pu_b:.3f}` |\n")
        f.write("\n---\n")
        f.write("Voxel IoU heatmap saved to `data/analysis_experiment_006/inter_class_iou_matrix.png`.\n")

    print("[exp_006] Completed successfully!")

if __name__ == '__main__':
    run_experiment_006()
