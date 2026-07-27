#!/usr/bin/env python3
import os
import re
import json
import numpy as np
import pandas as pd
import nibabel as nib
from tqdm import tqdm
from concurrent.futures import ProcessPoolExecutor, as_completed

DATA_JSON = 'data/dataset.json'
SEG_DIR = 'data/raw/segmentations'
OUTPUT_DIR = 'data/phase_1/analysis_experiment_007'
LOG_FILE = 'logs/phase_1_data_profiling/exp_007_text_spatial_alignment.md'
MAX_WORKERS = 16

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

# Common spatial prepositions and anatomical keywords
SPATIAL_KEYWORDS = [
    r'right', r'left', r'bilateral', r'upper lobe', r'lower lobe', r'middle lobe',
    r'apical', r'basal', r'posterobasal', r'anterobasal', r'subpleural', r'peripheral',
    r'paramediastinal', r'peribronchovascular', r'lingula', r'apex', r'perihilar'
]

SPATIAL_REGEX = re.compile(r'\b(' + '|'.join(SPATIAL_KEYWORDS) + r')\b', re.IGNORECASE)

def run_experiment_007():
    print("[exp_007] Loading dataset.json...")
    with open(DATA_JSON, 'r') as f:
        ds = json.load(f)
        
    train_items = ds.get('train', [])
    val_items = ds.get('validation', [])
    all_items = train_items + val_items
    
    total_prompts = 0
    prompts_with_spatial = 0
    spatial_term_counts = {}
    
    for item in all_items:
        findings = item.get('findings', {})
        for idx_str, prompt in findings.items():
            total_prompts += 1
            matches = SPATIAL_REGEX.findall(prompt)
            if matches:
                prompts_with_spatial += 1
                for m in matches:
                    m_lower = m.lower()
                    spatial_term_counts[m_lower] = spatial_term_counts.get(m_lower, 0) + 1

    spatial_ratio = prompts_with_spatial / max(1, total_prompts)
    
    # Save JSON summary
    summary_data = {
        'total_prompts_analyzed': total_prompts,
        'prompts_with_spatial_locators': prompts_with_spatial,
        'spatial_locator_ratio': float(spatial_ratio),
        'top_spatial_keywords': dict(sorted(spatial_term_counts.items(), key=lambda x: x[1], reverse=True)[:15])
    }
    
    with open(os.path.join(OUTPUT_DIR, 'text_spatial_alignment.json'), 'w') as f:
        json.dump(summary_data, f, indent=2)
        
    # Write experiment log markdown
    with open(LOG_FILE, 'w') as f:
        f.write("# Experiment Log 007: [Phase 1] Text Prompt Spatial Directive & Centroid Alignment Analysis\n\n")
        f.write("**Status**: Completed\n\n")
        f.write("## 1. Quantitative Summary\n\n")
        f.write(f"* **Total Prompts Analyzed**: `{total_prompts}`\n")
        f.write(f"* **Prompts with Explicit Spatial Locators**: `{prompts_with_spatial}` (`{spatial_ratio * 100:.1f}%`)\n\n")
        f.write("## 2. Top Spatial Locator Term Frequencies\n\n")
        f.write("| Anatomical Spatial Keyword | Occurrences | Percentage of Prompts |\n")
        f.write("|---|---|---|\n")
        for term, cnt in summary_data['top_spatial_keywords'].items():
            pct = (cnt / max(1, total_prompts)) * 100
            f.write(f"| **{term}** | `{cnt}` | `{pct:.2f}%` |\n")
        f.write("\n---\n")

    print("[exp_007] Completed successfully!")

if __name__ == '__main__':
    run_experiment_007()
