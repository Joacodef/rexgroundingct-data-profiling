import os
import json
import numpy as np
import pandas as pd
import nibabel as nib
import matplotlib.pyplot as plt
import seaborn as sns
from tqdm import tqdm
from scipy.ndimage import binary_dilation
from concurrent.futures import ProcessPoolExecutor, as_completed
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from scripts.config import (
    DATASET_JSON,
    RAW_IMAGES_DIR,
    RAW_MASKS_DIR,
    DATA_DIR,
    CATEGORY_MAP
)

DATA_JSON = str(DATASET_JSON)
IMG_DIR = str(RAW_IMAGES_DIR)
SEG_DIR = str(RAW_MASKS_DIR)
OUTPUT_DIR = str(DATA_DIR / "phase_1" / "analysis_experiment_004")
MAX_WORKERS = 32
MAX_SAMPLES_PER_MASK = 10000

os.makedirs(OUTPUT_DIR, exist_ok=True)


def process_single_scan(item_info):
    """Worker function to parse 3D CT scan and 4D mask, extracting HU values inside & around masks."""
    split_name, item = item_info
    filename = item['name']
    img_path = os.path.join(IMG_DIR, filename)
    mask_path = os.path.join(SEG_DIR, filename)

    results = []
    if not os.path.exists(img_path) or not os.path.exists(mask_path):
        return split_name, results

    try:
        img_nii = nib.load(img_path)
        mask_nii = nib.load(mask_path)
        
        ras_img = nib.as_closest_canonical(img_nii)
        ras_mask = nib.as_closest_canonical(mask_nii)

        img_data = ras_img.get_fdata().astype(np.float32)
        mask_data = ras_mask.get_fdata()  # 4D shape: (F, X, Y, Z)
    except Exception:
        return split_name, results

    if len(mask_data.shape) != 4 or img_data.shape != mask_data.shape[1:]:
        return split_name, results

    categories_dict = item.get('categories', {})

    for f_idx_str, cat_code in categories_dict.items():
        cat_code = str(cat_code)
        if cat_code not in CATEGORY_MAP:
            continue

        f_idx = int(f_idx_str)
        if f_idx >= mask_data.shape[0]:
            continue

        channel_mask = mask_data[f_idx] > 0.5  # 3D binary array (X, Y, Z)
        if not np.any(channel_mask):
            continue

        # Extract HU values inside the finding mask
        hu_in_mask = img_data[channel_mask]
        
        # Downsample voxels if dense to prevent excessive memory usage
        if len(hu_in_mask) > MAX_SAMPLES_PER_MASK:
            hu_in_mask = np.random.choice(hu_in_mask, size=MAX_SAMPLES_PER_MASK, replace=False)

        # Extract HU values from surrounding healthy tissue (dilated margin)
        dilated = binary_dilation(channel_mask, iterations=3)
        surrounding_mask = dilated & (~channel_mask)
        hu_surrounding = img_data[surrounding_mask]

        if len(hu_surrounding) > MAX_SAMPLES_PER_MASK:
            hu_surrounding = np.random.choice(hu_surrounding, size=MAX_SAMPLES_PER_MASK, replace=False)

        results.append({
            'cat_code': cat_code,
            'hu_in_mask': hu_in_mask,
            'hu_surrounding': hu_surrounding,
            'voxel_count': int(np.sum(channel_mask))
        })

    return split_name, results


def main():
    with open(DATA_JSON, 'r') as f:
        dataset = json.load(f)

    tasks = []
    for split_name in ['train', 'val']:
        for item in dataset.get(split_name, []):
            tasks.append((split_name, item))

    print(f"Processing {len(tasks)} scans across train and val splits with {MAX_WORKERS} workers...")

    # Accumulate HU values per category
    category_data = {
        cat: {'hu_mask': [], 'hu_bg': [], 'total_voxels': 0, 'mask_count': 0}
        for cat in CATEGORY_MAP.keys()
    }

    with ProcessPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = [executor.submit(process_single_scan, task) for task in tasks]
        for future in tqdm(as_completed(futures), total=len(futures), desc="HU Profiling"):
            split_name, results = future.result()
            for res in results:
                cat = res['cat_code']
                category_data[cat]['hu_mask'].append(res['hu_in_mask'])
                category_data[cat]['hu_bg'].append(res['hu_surrounding'])
                category_data[cat]['total_voxels'] += res['voxel_count']
                category_data[cat]['mask_count'] += 1

    summary_records = []
    violin_df_list = []

    for cat_code, cat_name in CATEGORY_MAP.items():
        data = category_data[cat_code]
        if not data['hu_mask']:
            print(f"Warning: No valid masks found for {cat_name} ({cat_code}).")
            continue

        all_hu_mask = np.concatenate(data['hu_mask'])
        all_hu_bg = np.concatenate(data['hu_bg']) if data['hu_bg'] else np.array([0.0])

        mean_hu = float(np.mean(all_hu_mask))
        std_hu = float(np.std(all_hu_mask))
        median_hu = float(np.median(all_hu_mask))
        p5_hu = float(np.percentile(all_hu_mask, 5))
        p25_hu = float(np.percentile(all_hu_mask, 25))
        p75_hu = float(np.percentile(all_hu_mask, 75))
        p95_hu = float(np.percentile(all_hu_mask, 95))

        bg_mean_hu = float(np.mean(all_hu_bg))
        contrast_delta = mean_hu - bg_mean_hu

        # Recommended window bounds (P5 to P95 clipped to reasonable CT range)
        rec_window_min = float(np.round(np.clip(p5_hu, -1024, 1000), 1))
        rec_window_max = float(np.round(np.clip(p95_hu, -1024, 1000), 1))

        summary_records.append({
            'Category Code': cat_code,
            'Category Name': cat_name,
            'Mask Count': data['mask_count'],
            'Total Voxels': data['total_voxels'],
            'Mean HU': round(mean_hu, 2),
            'Std HU': round(std_hu, 2),
            'Median HU': round(median_hu, 2),
            'P5 HU': round(p5_hu, 2),
            'P25 HU': round(p25_hu, 2),
            'P75 HU': round(p75_hu, 2),
            'P95 HU': round(p95_hu, 2),
            'Bg Mean HU': round(bg_mean_hu, 2),
            'Contrast Delta HU': round(contrast_delta, 2),
            'Recommended Window Min': rec_window_min,
            'Recommended Window Max': rec_window_max
        })

        # Subsample for violin visualization
        subsample = np.random.choice(all_hu_mask, size=min(5000, len(all_hu_mask)), replace=False)
        for hu_val in subsample:
            violin_df_list.append({
                'Category': cat_name,
                'HU Intensity': hu_val
            })

    df_summary = pd.DataFrame(summary_records)
    csv_path = os.path.join(OUTPUT_DIR, 'exp004_hu_summary_stats.csv')
    json_path = os.path.join(OUTPUT_DIR, 'exp004_hu_radiodensity_summary.json')
    
    df_summary.to_csv(csv_path, index=False)
    with open(json_path, 'w') as f:
        json.dump(summary_records, f, indent=2)
    print(f"Summary stats saved to {csv_path} and {json_path}")

    # Generate Visualizations
    df_plot = pd.DataFrame(violin_df_list)

    # 1. Violin plot of HU distributions per category
    plt.figure(figsize=(16, 10))
    sns.violinplot(data=df_plot, x='Category', y='HU Intensity', palette='muted', inner='quartile', cut=0)
    plt.axhline(-1000, color='gray', linestyle='--', alpha=0.6, label='Air (-1000 HU)')
    plt.axhline(-500, color='blue', linestyle=':', alpha=0.6, label='Lung Parenchyma (-500 HU)')
    plt.axhline(0, color='red', linestyle='--', alpha=0.6, label='Water/Soft Tissue (0 HU)')
    plt.xticks(rotation=45, ha='right', fontsize=10)
    plt.ylim(-1100, 400)
    plt.ylabel('Hounsfield Units (HU)', fontsize=12)
    plt.title('Hounsfield Unit (HU) Radiodensity Distribution Across 14 Pathology Categories', fontsize=14, fontweight='bold')
    plt.legend(loc='upper right')
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, 'exp004_hu_distribution_violin.png'), dpi=300)
    plt.close()

    # 2. Bar plot of Contrast Delta HU
    plt.figure(figsize=(14, 8))
    sns.barplot(data=df_summary, x='Category Name', y='Contrast Delta HU', palette='vlag')
    plt.axhline(0, color='black', linewidth=1)
    plt.xticks(rotation=45, ha='right', fontsize=10)
    plt.ylabel('Contrast Delta HU (Pathology - Background)', fontsize=12)
    plt.title('HU Contrast Delta Against Surrounding Healthy Tissue per Pathology', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, 'exp004_hu_contrast_delta_barplot.png'), dpi=300)
    plt.close()
    print("Exp 004 analysis completed successfully!")

if __name__ == '__main__':
    main()
