import os
import json
import numpy as np
import pandas as pd
import nibabel as nib
import matplotlib.pyplot as plt
import seaborn as sns
from tqdm import tqdm
from scipy.ndimage import zoom
from concurrent.futures import ProcessPoolExecutor, as_completed

DATA_JSON = 'data/dataset.json'
IMG_DIR = 'data/raw/images'
SEG_DIR = 'data/raw/segmentations'
OUTPUT_DIR = 'data/phase_1/analysis_experiment_003'
LOG_FILE = 'logs/phase_1_data_profiling/exp_003_average_mask_profiling.md'
MAX_WORKERS = 32
TARGET_GRID = (128, 128, 128)  # (X, Y, Z) in RAS space

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from scripts.config import CATEGORY_MAP

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)


def resample_3d_mask(mask_3d, target_shape=TARGET_GRID):
    """Resample 3D boolean/binary mask array to target_shape (128, 128, 128)."""
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

        # Compute relative centroid in canonical RAS space
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

SPATIAL_TAXONOMY = {
    '1a': 'Hilar / Peribronchial',
    '1b': 'Hilar / Peribronchial',
    '1c': 'Apical Dominant',
    '1d': 'Isotropic / Parenchymal',
    '1e': 'Isotropic / Parenchymal',
    '1f': 'Isotropic / Parenchymal',
    '2a': 'Isotropic / Parenchymal',
    '2b': 'Basal / Dependent',
    '2c': 'Isotropic / Parenchymal',
    '2d': 'Isotropic / Parenchymal',
    '2e': 'Basal / Dependent',
    '2f': 'Basal / Dependent',
    '2g': 'Isotropic / Parenchymal',
    '2h': 'Isotropic / Parenchymal',
}

def main():
    with open(DATA_JSON, 'r') as f:
        dataset = json.load(f)

    accumulators = {
        'train': create_accumulator(),
        'val': create_accumulator()
    }

    # Prepare task list
    tasks = []
    for split_name in ['train', 'val']:
        for item in dataset.get(split_name, []):
            tasks.append((split_name, item))

    print(f"Parallelizing 3D mask processing across {MAX_WORKERS} CPU workers ({len(tasks)} total scans)...")
    
    with ProcessPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = [executor.submit(process_single_scan, t) for t in tasks]
        for future in tqdm(as_completed(futures), total=len(tasks), desc="Processing 3D NIfTI Masks"):
            split_name, results = future.result()
            for cat_code, resampled_mask, centroid_rel in results:
                accum = accumulators[split_name][cat_code]
                accum['sum'] += resampled_mask
                accum['count'] += 1
                accum['centroids'].append(centroid_rel)

    # Compute average probability maps P(x | cat)
    prob_maps = {'train': {}, 'val': {}}
    alignment_stats = []

    for split_name in ['train', 'val']:
        for code, title in CATEGORY_MAP.items():
            accum = accumulators[split_name][code]
            count = accum['count']
            if count > 0:
                avg_map = accum['sum'] / count
                prob_maps[split_name][code] = avg_map
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
            delta_d = np.linalg.norm(tr_c - vl_c)
        else:
            delta_d = np.nan
            
        tr_vec = tr_map.flatten()
        vl_vec = vl_map.flatten()
        norm_tr = np.linalg.norm(tr_vec)
        norm_vl = np.linalg.norm(vl_vec)
        if norm_tr > 0 and norm_vl > 0:
            cos_sim = np.dot(tr_vec, vl_vec) / (norm_tr * norm_vl)
        else:
            cos_sim = np.nan
            
        taxonomy_type = SPATIAL_TAXONOMY.get(code, 'Isotropic / Parenchymal')
        
        alignment_stats.append({
            'CategoryCode': code,
            'CategoryName': title,
            'TrainMasks': tr_count,
            'ValMasks': vl_count,
            'TrainCentroid_RL': round(float(tr_c[0]), 3) if not np.isnan(tr_c[0]) else 'N/A',
            'TrainCentroid_AP': round(float(tr_c[1]), 3) if not np.isnan(tr_c[1]) else 'N/A',
            'TrainCentroid_IS': round(float(tr_c[2]), 3) if not np.isnan(tr_c[2]) else 'N/A',
            'ValCentroid_RL': round(float(vl_c[0]), 3) if not np.isnan(vl_c[0]) else 'N/A',
            'ValCentroid_AP': round(float(vl_c[1]), 3) if not np.isnan(vl_c[1]) else 'N/A',
            'ValCentroid_IS': round(float(vl_c[2]), 3) if not np.isnan(vl_c[2]) else 'N/A',
            'CentroidDelta_d': round(float(delta_d), 4) if not np.isnan(delta_d) else 'N/A',
            'CosineSimilarity_Scos': round(float(cos_sim), 4) if not np.isnan(cos_sim) else 'N/A',
            'SpatialPriorType': taxonomy_type
        })

    plt.style.use('seaborn-v0_8-white' if 'seaborn-v0_8-white' in plt.style.available else 'default')

    # 1. Export individual Train population density maps (N=7687)
    for code, title in CATEGORY_MAP.items():
        train_map = prob_maps['train'][code]
        train_count = accumulators['train'][code]['count']
        
        c_train = train_map.mean(axis=1).T[::-1, :]
        s_train = train_map.mean(axis=0).T[::-1, :]
        a_train = train_map.mean(axis=2).T[::-1, :]
        
        fig, axes = plt.subplots(1, 3, figsize=(15, 4.5))
        fig.suptitle(f'Canonical Population Spatial Density Map (Train N={train_count}):\n{title}', fontsize=14, fontweight='bold')
        
        vmax = max(c_train.max(), 1e-4)
        axes[0].imshow(c_train, cmap='hot', vmin=0, vmax=vmax)
        axes[0].set_title('Coronal (R -> L vs I -> S)')
        axes[0].set_xlabel('Right (R) ---------> Left (L)')
        axes[0].set_ylabel('Superior (S)\n^\n|\nInferior (I)')
        
        vmax_s = max(s_train.max(), 1e-4)
        axes[1].imshow(s_train, cmap='hot', vmin=0, vmax=vmax_s)
        axes[1].set_title('Sagittal (A -> P vs I -> S)')
        axes[1].set_xlabel('Anterior (A) ---------> Posterior (P)')
        axes[1].set_ylabel('Superior (S)\n^\n|\nInferior (I)')
        
        vmax_a = max(a_train.max(), 1e-4)
        axes[2].imshow(a_train, cmap='hot', vmin=0, vmax=vmax_a)
        axes[2].set_title('Axial (R -> L vs A -> P)')
        axes[2].set_xlabel('Right (R) ---------> Left (L)')
        axes[2].set_ylabel('Anterior (A)\n^\n|\nPosterior (P)')
        
        plt.tight_layout()
        clean_title = title.lower().replace(' ', '_').replace('/', '_')
        plot_filename = f"exp003_average_mask_{code}_{clean_title}.png"
        plt.savefig(os.path.join(OUTPUT_DIR, plot_filename), dpi=300)
        plt.close()

    # 2. Export 4-Panel Representative Population Spatial Prior Taxonomy Figure
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

    # Save summary JSON
    df_centroids = pd.DataFrame(alignment_stats)
    json_path = os.path.join(OUTPUT_DIR, 'centroids_summary.json')
    df_centroids.to_json(json_path, orient='records', indent=2)
    print(f"Successfully processed 3D masks and saved summary statistics to {json_path}")

if __name__ == '__main__':
    main()


