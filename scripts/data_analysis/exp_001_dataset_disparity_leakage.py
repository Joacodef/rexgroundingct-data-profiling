import os
import json
import pandas as pd
import numpy as np
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from scripts.config import DATASET_JSON, DATA_DIR

# Load paths relative to environment via centralized scripts.config
DATA_JSON = str(DATASET_JSON)
OUTPUT_DIR = str(DATA_DIR / 'phase_1' / 'analysis_experiment_001')
os.makedirs(OUTPUT_DIR, exist_ok=True)

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
    finding_records = []
    patient_map = {'train': set(), 'val': set(), 'test': set()}

    for split_name, items in dataset.items():
        total_scans = len(items)
        total_findings = 0
        instance_counts = []

        for item in items:
            fname = item.get('name', '')
            pid = parse_patient_id(fname)
            patient_map[split_name].add(pid)

            cats = item.get('categories', {})
            entity_counts = item.get('entity_counts', {})
            total_findings += len(cats)

            for f_idx, cat_code in cats.items():
                ecount = entity_counts.get(str(f_idx), 1)
                instance_counts.append(ecount)
                finding_records.append({
                    'Split': split_name,
                    'PatientID': pid,
                    'Filename': fname,
                    'CategoryCode': cat_code,
                    'InstanceCount': ecount
                })

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

    summary_data = {
        'SplitSummary': split_stats,
        'PatientLeakageAudit': {
            'Train_Val_Overlap_Count': len(train_val_leak),
            'Train_Val_Overlap_Patients': train_val_leak,
            'Train_Test_Overlap_Count': len(train_test_leak),
            'Train_Test_Overlap_Patients': train_test_leak,
            'Val_Test_Overlap_Count': len(val_test_leak),
            'Val_Test_Overlap_Patients': val_test_leak,
        }
    }

    out_json = os.path.join(OUTPUT_DIR, 'exp001_disparity_leakage_summary.json')
    with open(out_json, 'w') as f:
        json.dump(summary_data, f, indent=2)

    print(f"Successfully generated Exp 001 summary JSON at {out_json}")

if __name__ == '__main__':
    main()
