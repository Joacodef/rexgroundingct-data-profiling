import os
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import sys
from pathlib import Path
from collections import defaultdict, Counter

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from scripts.config import DATASET_JSON, DATA_DIR, CATEGORY_MAP

# Load paths relative to environment via centralized scripts.config
DATA_JSON = str(DATASET_JSON)
OUTPUT_DIR = str(DATA_DIR / 'phase_1' / 'analysis_experiment_001')
FIG_DIR = str(ROOT_DIR / 'logs' / 'phase_1_report_overleaf' / 'fig')
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(FIG_DIR, exist_ok=True)

def parse_patient_id(filename):
    """Extract patient ID from filename convention (e.g. train_1841_a_1.nii.gz -> 1841)."""
    parts = filename.split('_')
    if len(parts) >= 2:
        return parts[1]
    return filename

def main():
    if not os.path.exists(DATA_JSON):
        print(f"Dataset file not found at {DATA_JSON}")
        return

    with open(DATA_JSON, 'r') as f:
        dataset = json.load(f)

    split_stats = {}
    patient_map = {'train': set(), 'val': set(), 'test': set()}
    
    # Category-level breakdown accumulators
    cat_split_instances = defaultdict(lambda: {'train': [], 'val': [], 'test': []})
    cat_split_findings = defaultdict(lambda: {'train': 0, 'val': 0, 'test': 0})
    findings_per_scan_counts = {'train': [], 'val': [], 'test': []}
    
    # Scan-level co-occurrence matrix accumulators
    sorted_cat_codes = sorted(list(CATEGORY_MAP.keys()))
    num_cats = len(sorted_cat_codes)
    cat_to_idx = {code: i for i, code in enumerate(sorted_cat_codes)}
    
    cooccurrence_matrix = np.zeros((num_cats, num_cats), dtype=int)
    total_scans_analyzed = 0

    for split_name, items in dataset.items():
        if split_name not in ['train', 'val', 'test']:
            continue
        total_scans = len(items)
        total_findings = 0
        instance_counts = []

        for item in items:
            total_scans_analyzed += 1
            fname = item.get('name', '')
            pid = parse_patient_id(fname)
            patient_map[split_name].add(pid)

            cats = item.get('categories', {})
            entity_counts = item.get('entity_counts', {})
            num_f = len(cats)
            total_findings += num_f
            findings_per_scan_counts[split_name].append(num_f)

            scan_cats_present = set()

            for f_idx, cat_code in cats.items():
                if cat_code not in CATEGORY_MAP:
                    continue
                ecount = entity_counts.get(str(f_idx), 1)
                instance_counts.append(ecount)
                cat_split_instances[cat_code][split_name].append(ecount)
                cat_split_findings[cat_code][split_name] += 1
                scan_cats_present.add(cat_code)

            # Update scan-level co-occurrence matrix across all splits
            for cat_a in scan_cats_present:
                idx_a = cat_to_idx[cat_a]
                for cat_b in scan_cats_present:
                    idx_b = cat_to_idx[cat_b]
                    cooccurrence_matrix[idx_a, idx_b] += 1

        mean_instances = float(np.mean(instance_counts)) if instance_counts else 0.0
        std_instances = float(np.std(instance_counts)) if instance_counts else 0.0
        max_instances = int(np.max(instance_counts)) if instance_counts else 0

        split_stats[split_name] = {
            'TotalScans': total_scans,
            'TotalFindings': total_findings,
            'FindingsPerScan': round(total_findings / total_scans, 2) if total_scans > 0 else 0.0,
            'UniquePatients': len(patient_map[split_name]),
            'MeanInstancesPerFinding': round(mean_instances, 3),
            'StdInstancesPerFinding': round(std_instances, 3),
            'MaxInstancesInFinding': max_instances
        }

    # Cross-split patient leakage audit
    train_val_leak = sorted(list(patient_map['train'].intersection(patient_map['val'])))
    train_test_leak = sorted(list(patient_map['train'].intersection(patient_map['test'])))
    val_test_leak = sorted(list(patient_map['val'].intersection(patient_map['test'])))

    # Category-level disparity breakdown
    category_disparity = {}
    for code in sorted_cat_codes:
        cat_name = CATEGORY_MAP[code]
        tr_inst = cat_split_instances[code]['train']
        vl_inst = cat_split_instances[code]['val']
        ts_inst = cat_split_instances[code]['test']
        
        tr_mean = float(np.mean(tr_inst)) if tr_inst else 0.0
        vl_mean = float(np.mean(vl_inst)) if vl_inst else 0.0
        ts_mean = float(np.mean(ts_inst)) if ts_inst else 0.0
        
        disparity_ratio = round(vl_mean / tr_mean, 2) if tr_mean > 0 else 0.0

        category_disparity[code] = {
            'CategoryName': cat_name,
            'TrainFindingsCount': cat_split_findings[code]['train'],
            'ValFindingsCount': cat_split_findings[code]['val'],
            'TestFindingsCount': cat_split_findings[code]['test'],
            'TrainMeanInstancesPerFinding': round(tr_mean, 3),
            'ValMeanInstancesPerFinding': round(vl_mean, 3),
            'TestMeanInstancesPerFinding': round(ts_mean, 3),
            'DisparityRatio_Val_vs_Train': disparity_ratio
        }

    # Calculate conditional co-occurrence probability matrix P(Cat_J | Cat_I)
    cooccurrence_prob = np.zeros((num_cats, num_cats), dtype=float)
    for i in range(num_cats):
        diag_val = cooccurrence_matrix[i, i]
        if diag_val > 0:
            cooccurrence_prob[i, :] = np.round(cooccurrence_matrix[i, :] / float(diag_val), 4)

    # Save summary JSON
    summary_data = {
        'SplitSummary': split_stats,
        'PatientLeakageAudit': {
            'Train_Val_Overlap_Count': len(train_val_leak),
            'Train_Val_Overlap_Patients': train_val_leak,
            'Train_Test_Overlap_Count': len(train_test_leak),
            'Train_Test_Overlap_Patients': train_test_leak,
            'Val_Test_Overlap_Count': len(val_test_leak),
            'Val_Test_Overlap_Patients': val_test_leak,
        },
        'CategoryLevelDisparity': category_disparity,
        'ScanLevelCoOccurrenceMatrix': {
            'CategoryOrder': [CATEGORY_MAP[c] for c in sorted_cat_codes],
            'AbsoluteCounts': cooccurrence_matrix.tolist(),
            'ConditionalProbabilities': cooccurrence_prob.tolist()
        }
    }

    out_json = os.path.join(OUTPUT_DIR, 'exp001_disparity_leakage_summary.json')
    with open(out_json, 'w') as f:
        json.dump(summary_data, f, indent=2)

    print(f"Successfully generated Exp 001 summary JSON at {out_json}")

    # Set publication plot style
    sns.set_theme(style='whitegrid', palette='muted')
    plt.rcParams.update({'font.sans-serif': 'DejaVu Sans', 'font.size': 11})

    # --- Plot 1: Category Frequency Proportion (%) Across Splits ---
    cat_prop_data = []
    tot_train_f = split_stats['train']['TotalFindings']
    tot_val_f = split_stats['val']['TotalFindings']
    tot_test_f = split_stats['test']['TotalFindings']

    for code in sorted_cat_codes:
        cat_label = f"{code}: {CATEGORY_MAP[code]}"
        tr_cnt = cat_split_findings[code]['train']
        vl_cnt = cat_split_findings[code]['val']
        ts_cnt = cat_split_findings[code]['test']

        cat_prop_data.append({
            'CategoryCode': code,
            'CategoryLabel': cat_label,
            'Split': 'Train',
            'Proportion': (tr_cnt / tot_train_f * 100) if tot_train_f > 0 else 0.0
        })
        cat_prop_data.append({
            'CategoryCode': code,
            'CategoryLabel': cat_label,
            'Split': 'Validation',
            'Proportion': (vl_cnt / tot_val_f * 100) if tot_val_f > 0 else 0.0
        })
        cat_prop_data.append({
            'CategoryCode': code,
            'CategoryLabel': cat_label,
            'Split': 'Test',
            'Proportion': (ts_cnt / tot_test_f * 100) if tot_test_f > 0 else 0.0
        })

    df_cat_prop = pd.DataFrame(cat_prop_data)

    plt.figure(figsize=(14, 7))
    palette = {'Train': '#2b5c8f', 'Validation': '#d95f02', 'Test': '#2ea154'}
    ax1 = sns.barplot(
        data=df_cat_prop,
        x='CategoryCode',
        y='Proportion',
        hue='Split',
        palette=palette
    )

    plt.title('Category Frequency Proportion (%) Across Dataset Splits (Train vs. Validation vs. Test)', fontsize=14, fontweight='bold', pad=15)
    plt.xlabel('Finding Category', fontsize=12, fontweight='bold')
    plt.ylabel('Proportion of Split Findings (%)', fontsize=12, fontweight='bold')
    plt.ylim(0, max(df_cat_prop['Proportion']) * 1.15)
    
    # Custom x-tick labels with category codes and full category names rotated at 35 degrees
    labels = [f"{code}: {CATEGORY_MAP[code]}" for code in sorted_cat_codes]
    ax1.set_xticks(range(len(sorted_cat_codes)))
    ax1.set_xticklabels(labels, rotation=35, ha='right', fontsize=9.5)
    plt.legend(title='Dataset Split', title_fontsize='11', fontsize='10', loc='upper right')
    plt.tight_layout()

    fig1_path_1 = os.path.join(OUTPUT_DIR, 'exp001_category_frequency_breakdown.png')
    fig1_path_2 = os.path.join(FIG_DIR, 'exp001_category_frequency_breakdown.png')
    plt.savefig(fig1_path_1, dpi=300)
    plt.savefig(fig1_path_2, dpi=300)
    plt.close()
    print(f"Successfully generated Category Frequency Proportion figure at {fig1_path_1} and {fig1_path_2}")

    # --- Plot 2: Findings Count per CT Scan Record Distribution Across Splits ---
    findings_per_scan_data = []
    for split_name in ['train', 'val', 'test']:
        counts = findings_per_scan_counts[split_name]
        total_scans = len(counts)
        counter = Counter(counts)
        label_split = 'Train' if split_name == 'train' else ('Validation' if split_name == 'val' else 'Test')
        
        for num_f in range(1, 7):
            if num_f < 6:
                scnt = counter[num_f]
                lbl = str(num_f)
            else:
                scnt = sum(v for k, v in counter.items() if k >= 6)
                lbl = '6+'
                
            findings_per_scan_data.append({
                'FindingsPerScan': lbl,
                'Split': label_split,
                'Proportion': (scnt / total_scans * 100) if total_scans > 0 else 0.0
            })

    df_fps = pd.DataFrame(findings_per_scan_data)

    plt.figure(figsize=(10, 6))
    ax2 = sns.barplot(
        data=df_fps,
        x='FindingsPerScan',
        y='Proportion',
        hue='Split',
        palette=palette
    )

    plt.title('Distribution of Findings Count per CT Scan Record Across Splits', fontsize=14, fontweight='bold', pad=15)
    plt.xlabel('Number of Finding Prompts per CT Scan', fontsize=12, fontweight='bold')
    plt.ylabel('Proportion of CT Scans in Split (%)', fontsize=12, fontweight='bold')
    plt.ylim(0, max(df_fps['Proportion']) * 1.15)

    # Add bar labels
    for p in ax2.patches:
        height = p.get_height()
        if height > 0:
            ax2.annotate(f'{height:.1f}%',
                        (p.get_x() + p.get_width() / 2., height),
                        ha='center', va='bottom', fontsize=8, xytext=(0, 3),
                        textcoords='offset points')

    plt.legend(title='Dataset Split', title_fontsize='11', fontsize='10', loc='upper right')
    plt.tight_layout()

    fig2_path_1 = os.path.join(OUTPUT_DIR, 'exp001_findings_per_scan.png')
    fig2_path_2 = os.path.join(FIG_DIR, 'exp001_findings_per_scan.png')
    plt.savefig(fig2_path_1, dpi=300)
    plt.savefig(fig2_path_2, dpi=300)
    plt.close()
    print(f"Successfully generated Findings per Scan Distribution figure at {fig2_path_1} and {fig2_path_2}")

    # --- Plot 3: Co-Occurrence Heatmap ---
    try:
        labels = [f"{code}: {CATEGORY_MAP[code]}" for code in sorted_cat_codes]
        plt.figure(figsize=(14, 12))
        sns.heatmap(cooccurrence_prob, annot=True, fmt='.2f', cmap='YlGnBu',
                    xticklabels=labels, yticklabels=labels, cbar_kws={'label': 'P(Column Present | Row Present)'})
        plt.title('Scan-Level Multi-Finding Co-Occurrence Matrix P(Col | Row)', fontsize=14, fontweight='bold')
        plt.xticks(rotation=45, ha='right', fontsize=9)
        plt.yticks(rotation=0, fontsize=9)
        plt.tight_layout()
        
        heatmap_path_1 = os.path.join(OUTPUT_DIR, 'exp001_cooccurrence_heatmap.png')
        heatmap_path_2 = os.path.join(FIG_DIR, 'exp001_cooccurrence_heatmap.png')
        plt.savefig(heatmap_path_1, dpi=300)
        plt.savefig(heatmap_path_2, dpi=300)
        plt.close()
        print(f"Successfully generated co-occurrence heatmap figure at {heatmap_path_1} and {heatmap_path_2}")
    except Exception as e:
        print(f"Visualization note: heatmap generation skipped or encountered issue: {e}")

if __name__ == '__main__':
    main()
