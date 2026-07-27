import os
import json
import numpy as np
import pandas as pd
import nibabel as nib
import matplotlib.pyplot as plt
from pathlib import Path
from tqdm import tqdm
from scipy.ndimage import zoom
from concurrent.futures import ProcessPoolExecutor, as_completed

import sys

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from scripts.config import (
    CATEGORY_MAP,
    SPATIAL_TAXONOMY,
    DATASET_JSON,
    RAW_IMAGES_DIR,
    RAW_MASKS_DIR,
    DATA_DIR
)

# Target directory and environment configuration from centralized config
DATA_JSON = str(DATASET_JSON)
IMG_DIR = str(RAW_IMAGES_DIR)
SEG_DIR = str(RAW_MASKS_DIR)
OUTPUT_DIR = str(DATA_DIR / 'phase_1' / 'analysis_experiment_003')
TARGET_GRID = (128, 128, 128)  # (X, Y, Z) in RAS space
MAX_WORKERS = min(32, os.cpu_count() or 4)

os.makedirs(OUTPUT_DIR, exist_ok=True)


def resample_3d_mask(mask_3d, target_shape=TARGET_GRID):
    """Resample 3D boolean/binary mask array to canonical target_shape (128, 128, 128)."""
    curr_shape = mask_3d.shape
    if curr_shape == target_shape:
        return mask_3d.astype(np.float32)
    zoom_factors = [t / float(c) for t, c in zip(target_shape, curr_shape)]
    resampled = zoom(mask_3d.astype(np.float32), zoom_factors, order=1)
    return np.clip(resampled, 0.0, 1.0)

def process_single_scan(item_info):
    """Worker function to process one NIfTI mask file with parent CT image affine inheritance per 3D channel."""
    split_name, item = item_info
    filename = item['name']
    mask_path = os.path.join(SEG_DIR, filename)
    img_path = os.path.join(IMG_DIR, filename)

    results = []
    if not os.path.exists(mask_path):
        return split_name, results

    try:
        mask_nii = nib.load(mask_path)
        mask_raw_data = mask_nii.get_fdata()  # 4D shape: (F, X, Y, Z)

        if os.path.exists(img_path):
            img_nii = nib.load(img_path)
            ct_affine = img_nii.affine
        else:
            ct_affine = mask_nii.affine
    except Exception:
        return split_name, results

    categories_dict = item.get('categories', {})

    for f_idx_str, cat_code in categories_dict.items():
        cat_code = str(cat_code)
        if cat_code not in CATEGORY_MAP:
            continue

        f_idx = int(f_idx_str)
        if f_idx >= mask_raw_data.shape[0]:
            continue

        raw_channel = mask_raw_data[f_idx]  # 3D array (X, Y, Z)
        if not np.any(raw_channel > 0.5):
            continue

        # Reorient 3D finding mask channel into canonical RAS using parent CT affine
        channel_nii = nib.Nifti1Image(raw_channel.astype(np.float32), ct_affine)
        ras_channel_nii = nib.as_closest_canonical(channel_nii)
        channel_mask = ras_channel_nii.get_fdata() > 0.5

        if not np.any(channel_mask):
            continue

        # Compute relative centroid in canonical RAS space [RL, AP, IS]
        coords = np.argwhere(channel_mask)
        centroid_rel = coords.mean(axis=0) / np.array(channel_mask.shape)

        # Resample to canonical target grid
        resampled = resample_3d_mask(channel_mask, TARGET_GRID)
        results.append((cat_code, resampled, centroid_rel))

    return split_name, results

def create_accumulator():
    return {
        cat: {
            'sum': np.zeros(TARGET_GRID, dtype=np.float64),
            'count': 0,
            'centroids': []
        }
        for cat in CATEGORY_MAP.keys()
    }

def main():
    existing_json = os.path.join(OUTPUT_DIR, 'centroids_summary.json')
    out_summary_json = os.path.join(OUTPUT_DIR, 'exp003_spatial_density_priors_summary.json')

    if not os.path.exists(DATA_JSON) and os.path.exists(existing_json):
        print(f"Dataset not found, using existing centroids summary at {existing_json}")
        with open(existing_json, 'r') as f:
            summary_records = json.load(f)
        with open(out_summary_json, 'w') as f:
            json.dump(summary_records, f, indent=2)
        print(f"Exported Exp 003 summary JSON to {out_summary_json}")
        return

    if not os.path.exists(DATA_JSON):
        print(f"Error: Dataset JSON not found at {DATA_JSON}")
        return

    with open(DATA_JSON, 'r') as f:
        dataset = json.load(f)

    accumulators = {
        'train': create_accumulator(),
        'val': create_accumulator()
    }

    tasks = []
    for split_name in ['train', 'val']:
        for item in dataset.get(split_name, []):
            tasks.append((split_name, item))

    print(f"Parallelizing 3D RAS spatial density analysis across {MAX_WORKERS} CPU workers ({len(tasks)} scans)...")

    with ProcessPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = [executor.submit(process_single_scan, t) for t in tasks]
        for future in tqdm(as_completed(futures), total=len(tasks), desc="Processing 3D Masks"):
            split_name, results = future.result()
            for cat_code, resampled_mask, centroid_rel in results:
                accum = accumulators[split_name][cat_code]
                accum['sum'] += resampled_mask
                accum['count'] += 1
                accum['centroids'].append(centroid_rel)

    prob_maps = {'train': {}, 'val': {}}
    alignment_stats = []

    for split_name in ['train', 'val']:
        for code in CATEGORY_MAP.keys():
            accum = accumulators[split_name][code]
            count = accum['count']
            if count > 0:
                prob_maps[split_name][code] = accum['sum'] / count
            else:
                prob_maps[split_name][code] = np.zeros(TARGET_GRID, dtype=np.float32)

    for code in sorted(CATEGORY_MAP.keys()):
        title = CATEGORY_MAP[code]
        tr_map = prob_maps['train'][code]
        vl_map = prob_maps['val'][code]
        tr_count = accumulators['train'][code]['count']
        vl_count = accumulators['val'][code]['count']

        tr_centroids = np.array(accumulators['train'][code]['centroids'])
        vl_centroids = np.array(accumulators['val'][code]['centroids'])

        tr_c = tr_centroids.mean(axis=0) if len(tr_centroids) > 0 else np.array([np.nan]*3)
        vl_c = vl_centroids.mean(axis=0) if len(vl_centroids) > 0 else np.array([np.nan]*3)

        if not np.isnan(tr_c).any() and not np.isnan(vl_c).any():
            delta_d = float(np.linalg.norm(tr_c - vl_c))
        else:
            delta_d = None

        tr_vec = tr_map.flatten()
        vl_vec = vl_map.flatten()
        norm_tr = np.linalg.norm(tr_vec)
        norm_vl = np.linalg.norm(vl_vec)
        if norm_tr > 0 and norm_vl > 0:
            cos_sim = float(np.dot(tr_vec, vl_vec) / (norm_tr * norm_vl))
        else:
            cos_sim = None

        taxonomy_type = SPATIAL_TAXONOMY.get(code, 'Isotropic / Parenchymal')

        alignment_stats.append({
            'CategoryCode': code,
            'CategoryName': title,
            'TrainMasks': tr_count,
            'ValMasks': vl_count,
            'TrainCentroid_RL': round(float(tr_c[0]), 3) if not np.isnan(tr_c[0]) else None,
            'TrainCentroid_AP': round(float(tr_c[1]), 3) if not np.isnan(tr_c[1]) else None,
            'TrainCentroid_IS': round(float(tr_c[2]), 3) if not np.isnan(tr_c[2]) else None,
            'ValCentroid_RL': round(float(vl_c[0]), 3) if not np.isnan(vl_c[0]) else None,
            'ValCentroid_AP': round(float(vl_c[1]), 3) if not np.isnan(vl_c[1]) else None,
            'ValCentroid_IS': round(float(vl_c[2]), 3) if not np.isnan(vl_c[2]) else None,
            'CentroidDelta_d': round(delta_d, 4) if delta_d is not None else None,
            'CosineSimilarity_Scos': round(cos_sim, 4) if cos_sim is not None else None,
            'SpatialPriorType': taxonomy_type
        })

    # Save summary JSON files
    with open(out_summary_json, 'w') as f:
        json.dump(alignment_stats, f, indent=2)
    with open(existing_json, 'w') as f:
        json.dump(alignment_stats, f, indent=2)

    print(f"Successfully generated Exp 003 summary JSON at {out_summary_json}")

    # Generate 4-Panel Taxonomy Figure if maps exist
    try:
        key_panel_cats = [
            ('1c', 'Emphysema', 'Apical Dominant Prior'),
            ('2e', 'Pleural effusion / thickening', 'Basal / Dependent Prior'),
            ('1a', 'Bronchial wall thickening', 'Hilar / Peribronchial Prior'),
            ('2d', 'Pulmonary nodules / masses', 'Isotropic / Parenchymal Prior')
        ]

        fig, axes = plt.subplots(2, 2, figsize=(12, 10))
        fig.suptitle('Canonical Population Spatial Probability Density Priors (Train Split N=7,687)', fontsize=14, fontweight='bold')

        for ax, (code, title, prior_label) in zip(axes.flat, key_panel_cats):
            tr_map = prob_maps['train'][code]
            tr_count = accumulators['train'][code]['count']
            coronal_proj = tr_map.mean(axis=1).T[::-1, :]

            im = ax.imshow(coronal_proj, cmap='hot', vmin=0, vmax=coronal_proj.max())
            ax.set_title(f"{title} ({code})\n[{prior_label}, N={tr_count}]", fontsize=11, fontweight='bold')
            ax.set_xlabel('Right (R) ---------> Left (L)')
            ax.set_ylabel('Superior (S) <--- (I)')
            fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)

        plt.tight_layout()
        panel_path = os.path.join(OUTPUT_DIR, 'exp003_population_spatial_priors_4panel.png')
        plt.savefig(panel_path, dpi=300)
        plt.close()
        print(f"Generated 4-panel spatial prior figure at {panel_path}")
    except Exception as e:
        print(f"Note: Visualization figure generation skipped or encountered issue: {e}")

if __name__ == '__main__':
    main()
