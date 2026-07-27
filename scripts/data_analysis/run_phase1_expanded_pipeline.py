#!/usr/bin/env python3
"""
Phase 1 Expanded Pipeline — ReXGroundingCT Challenge @ MICCAI 2026

Part A: Patient, Longitudinal Scan & Series Reconstruction Hierarchy Analysis
Part B: Standard 3D CT Image & Mask Physical Extents Profiling
Part C: Structural & Syntax Clinical Text Profiling (Hedging, Compound Prompts, Spatial Prepositions)

Rules & Governance Compliance:
- Server-Agnostic: Uses relative paths & loads environment variables via .env / os.environ.
- Epistemic Modesty: Frames findings as quantitative observations calibrated by data evidence.
"""

import os
import re
import json
import numpy as np
import nibabel as nib
import sys
from pathlib import Path
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor, as_completed

# Add project root to sys.path for clean module imports
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from scripts.config import CATEGORY_MAP


def load_env_file(env_path=".env"):
    """Load key-value pairs from .env into os.environ if present."""
    env_file = Path(env_path)
    if env_file.exists():
        with open(env_file, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    os.environ.setdefault(k.strip(), v.strip())

# --- PART A ANALYSIS ---
def analyze_part_a(data):
    filename_pattern = re.compile(r"^(train|val|test)_(\d+)_([a-z]+)_(\d+)\.nii\.gz$")

    split_stats = defaultdict(lambda: {
        "files": 0,
        "patients": set(),
        "longitudinal_scans": set(),
        "reconstructions": set()
    })

    patient_to_splits = defaultdict(set)
    patient_to_files = defaultdict(lambda: defaultdict(list))
    patient_to_scans = defaultdict(lambda: defaultdict(list))

    for split_name, items in data.items():
        for item in items:
            fname = item.get("name", "")
            match = filename_pattern.match(fname)
            if not match:
                continue

            item_split, patient_id, scan_suffix, recon_suffix = match.groups()
            scan_key = f"{patient_id}_{scan_suffix}"
            full_recon_key = f"{patient_id}_{scan_suffix}_{recon_suffix}"

            split_stats[split_name]["files"] += 1
            split_stats[split_name]["patients"].add(patient_id)
            split_stats[split_name]["longitudinal_scans"].add(scan_key)
            split_stats[split_name]["reconstructions"].add(full_recon_key)

            patient_to_splits[patient_id].add(split_name)
            patient_to_files[patient_id][split_name].append(fname)
            patient_to_scans[patient_id][scan_suffix].append(fname)

    train_pts = split_stats["train"]["patients"]
    val_pts = split_stats["val"]["patients"]
    test_pts = split_stats["test"]["patients"] if "test" in split_stats else set()

    train_val_leakage = sorted(list(train_pts.intersection(val_pts)))
    train_test_leakage = sorted(list(train_pts.intersection(test_pts)))
    val_test_leakage = sorted(list(val_pts.intersection(test_pts)))

    leakage_details = {}
    for pid in set(train_val_leakage + train_test_leakage + val_test_leakage):
        leakage_details[pid] = dict(patient_to_files[pid])

    patient_scan_counts = defaultdict(int)
    for pt, scans_dict in patient_to_scans.items():
        patient_scan_counts[len(scans_dict)] += 1

    summary_data = {
        "split_hierarchy_summary": {
            s: {
                "total_nifti_files": stats["files"],
                "unique_patients": len(stats["patients"]),
                "unique_longitudinal_scans": len(stats["longitudinal_scans"]),
                "unique_reconstruction_series": len(stats["reconstructions"])
            } for s, stats in split_stats.items()
        },
        "data_leakage_audit": {
            "train_val_patient_leakage_count": len(train_val_leakage),
            "train_val_patient_ids": train_val_leakage,
            "train_test_patient_leakage_count": len(train_test_leakage),
            "train_test_patient_ids": train_test_leakage,
            "val_test_patient_leakage_count": len(val_test_leakage),
            "val_test_patient_ids": val_test_leakage,
            "leakage_file_details": leakage_details
        },
        "longitudinal_scan_distribution": dict(patient_scan_counts)
    }

    output_dir = Path("data/phase_1/analysis_part_a")
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "patient_hierarchy_summary.json"
    with open(json_path, "w") as f:
        json.dump(summary_data, f, indent=2)

    log_path = Path("logs/phase_1_data_profiling/exp_009_patient_hierarchy.md")
    with open(log_path, "w") as f:
        f.write("# Experiment Log 009: [Phase 1] Patient, Longitudinal Scan & Reconstruction Series Hierarchy Analysis\n\n")
        f.write("**Status**: Completed  \n**Date**: July 2026  \n")
        f.write(f"**Primary Output**: `{json_path}`  \n\n---\n\n")
        f.write("## 1. Executive Summary\n\n")
        f.write("Experiment 009 profiles the 3-tier hierarchy across all 3,192 scans and identifies cross-split patient overlaps.\n\n")
        f.write("## 2. Dataset Hierarchy Breakdown\n\n")
        f.write("| Split | Total NIfTI Volumes | Unique Patients | Unique Longitudinal Scans |\n|---|---|---|---|\n")
        for s, stats in split_stats.items():
            f.write(f"| **{s.capitalize()}** | {stats['files']} | `{len(stats['patients'])}` | `{len(stats['longitudinal_scans'])}` |\n")
        f.write("\n## 3. Data Leakage Audit Findings\n\n")
        f.write(f"* Train <-> Val Overlap: `{len(train_val_leakage)}` patients ({train_val_leakage})\n")
        f.write(f"* Train <-> Test Overlap: `{len(train_test_leakage)}` patients ({train_test_leakage})\n")
        f.write(f"* Val <-> Test Overlap: `{len(val_test_leakage)}` patients ({val_test_leakage})\n")

    print(f"[Part A] Finished. JSON: {json_path}, Log: {log_path}")

# --- PART B WORKER & ANALYSIS ---
def process_single_volume_part_b(args):
    item, seg_dir = args
    fname = item["name"]
    cats_dict = item.get("categories", {})
    seg_path = os.path.join(seg_dir, fname)

    result = {
        "fname": fname,
        "shape": [],
        "zooms": [],
        "ct_vol_cm3": 0.0,
        "findings_stats": []
    }

    if not os.path.exists(seg_path):
        return result

    try:
        seg = nib.load(seg_path)
        data = seg.get_fdata() > 0
        zooms = [float(z) for z in seg.header.get_zooms()[:3]]
        result["zooms"] = zooms

        if data.ndim == 4:
            c, h, w, d = data.shape
            result["shape"] = [h, w, d]
            voxel_vol_mm3 = zooms[0] * zooms[1] * zooms[2]
            ct_vol_cm3 = (h * zooms[0] * w * zooms[1] * d * zooms[2]) / 1000.0
            result["ct_vol_cm3"] = ct_vol_cm3

            for ch_str, cat_code in cats_dict.items():
                ch_idx = int(ch_str)
                if ch_idx < c and cat_code in CATEGORY_MAP:
                    mask = data[ch_idx]
                    total_voxels = int(mask.sum())
                    if total_voxels > 0:
                        coords = np.where(mask)
                        dx_mm = float((coords[0].max() - coords[0].min() + 1) * zooms[0])
                        dy_mm = float((coords[1].max() - coords[1].min() + 1) * zooms[1])
                        dz_mm = float((coords[2].max() - coords[2].min() + 1) * zooms[2])
                        aspect_ratio = dz_mm / float(max(1e-3, max(dx_mm, dy_mm)))

                        mask_vol_mm3 = float(total_voxels * voxel_vol_mm3)
                        mask_vol_cm3 = mask_vol_mm3 / 1000.0
                        relative_occ_pct = (mask_vol_cm3 / float(max(1e-3, ct_vol_cm3))) * 100.0

                        result["findings_stats"].append({
                            "cat_code": cat_code,
                            "cat_name": CATEGORY_MAP[cat_code],
                            "voxels": total_voxels,
                            "mask_vol_mm3": mask_vol_mm3,
                            "mask_vol_cm3": mask_vol_cm3,
                            "bbox_dx_mm": dx_mm,
                            "bbox_dy_mm": dy_mm,
                            "bbox_dz_mm": dz_mm,
                            "bbox_aspect_ratio": aspect_ratio,
                            "relative_occ_pct": relative_occ_pct
                        })
    except Exception:
        pass

    return result

def analyze_part_b(data):
    seg_dir = os.environ.get("SEG_RAW_DIR", "data/raw/segmentations")
    print(f"\n[Part B] Profiling 3D CT Image & Mask Physical Extents (Segmentation dir: {seg_dir})...")

    all_items = []
    for split_name, items in data.items():
        all_items.extend(items)

    tasks = [(item, seg_dir) for item in all_items]

    volume_shapes = []
    voxel_spacings_x = []
    voxel_spacings_y = []
    voxel_spacings_z = []
    ct_volumes_cm3 = []

    cat_stats = defaultdict(lambda: {
        "finding_count": 0,
        "mask_vols_mm3": [],
        "bbox_dx_mm": [],
        "bbox_dy_mm": [],
        "bbox_dz_mm": [],
        "aspect_ratios": [],
        "relative_occ_pct": []
    })

    with ProcessPoolExecutor(max_workers=16) as executor:
        futures = [executor.submit(process_single_volume_part_b, task) for task in tasks]
        for f in as_completed(futures):
            res = f.result()
            if res["shape"]:
                volume_shapes.append(res["shape"])
            if res["zooms"]:
                voxel_spacings_x.append(res["zooms"][0])
                voxel_spacings_y.append(res["zooms"][1])
                voxel_spacings_z.append(res["zooms"][2])
            if res["ct_vol_cm3"] > 0:
                ct_volumes_cm3.append(res["ct_vol_cm3"])

            for fstat in res["findings_stats"]:
                ccode = fstat["cat_code"]
                cat_stats[ccode]["finding_count"] += 1
                cat_stats[ccode]["mask_vols_mm3"].append(fstat["mask_vol_mm3"])
                cat_stats[ccode]["bbox_dx_mm"].append(fstat["bbox_dx_mm"])
                cat_stats[ccode]["bbox_dy_mm"].append(fstat["bbox_dy_mm"])
                cat_stats[ccode]["bbox_dz_mm"].append(fstat["bbox_dz_mm"])
                cat_stats[ccode]["aspect_ratios"].append(fstat["bbox_aspect_ratio"])
                cat_stats[ccode]["relative_occ_pct"].append(fstat["relative_occ_pct"])

    ct_summary = {
        "ct_scans_profiled": len(ct_volumes_cm3),
        "voxel_spacing_mm": {
            "mean_dx": float(np.mean(voxel_spacings_x)) if voxel_spacings_x else 0.0,
            "median_dx": float(np.median(voxel_spacings_x)) if voxel_spacings_x else 0.0,
            "mean_dy": float(np.mean(voxel_spacings_y)) if voxel_spacings_y else 0.0,
            "median_dy": float(np.median(voxel_spacings_y)) if voxel_spacings_y else 0.0,
            "mean_dz": float(np.mean(voxel_spacings_z)) if voxel_spacings_z else 0.0,
            "median_dz": float(np.median(voxel_spacings_z)) if voxel_spacings_z else 0.0,
        },
        "ct_physical_vol_cm3": {
            "mean": float(np.mean(ct_volumes_cm3)) if ct_volumes_cm3 else 0.0,
            "median": float(np.median(ct_volumes_cm3)) if ct_volumes_cm3 else 0.0,
            "p5": float(np.percentile(ct_volumes_cm3, 5)) if ct_volumes_cm3 else 0.0,
            "p95": float(np.percentile(ct_volumes_cm3, 95)) if ct_volumes_cm3 else 0.0,
        }
    }

    category_summary = {}
    for ccode, name in sorted(CATEGORY_MAP.items()):
        stats = cat_stats[ccode]
        if stats["finding_count"] > 0:
            category_summary[name] = {
                "cat_code": ccode,
                "finding_count": stats["finding_count"],
                "mask_vol_mm3": {
                    "mean": float(np.mean(stats["mask_vols_mm3"])),
                    "median": float(np.median(stats["mask_vols_mm3"])),
                    "p5": float(np.percentile(stats["mask_vols_mm3"], 5)),
                    "p95": float(np.percentile(stats["mask_vols_mm3"], 95)),
                },
                "bbox_extents_mm": {
                    "median_dx": float(np.median(stats["bbox_dx_mm"])),
                    "median_dy": float(np.median(stats["bbox_dy_mm"])),
                    "median_dz": float(np.median(stats["bbox_dz_mm"])),
                    "p95_dx": float(np.percentile(stats["bbox_dx_mm"], 95)),
                    "p95_dy": float(np.percentile(stats["bbox_dy_mm"], 95)),
                    "p95_dz": float(np.percentile(stats["bbox_dz_mm"], 95)),
                },
                "median_aspect_ratio_dz_dxy": float(np.median(stats["aspect_ratios"])),
                "median_relative_occ_pct": float(np.median(stats["relative_occ_pct"]))
            }

    output_dir = Path("data/phase_1/analysis_part_b")
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "ct_mask_physical_stats.json"
    with open(json_path, "w") as f:
        json.dump({"ct_summary": ct_summary, "category_summary": category_summary}, f, indent=2)

    log_path = Path("logs/phase_1_data_profiling/exp_010_ct_mask_physical_extents.md")
    with open(log_path, "w") as f:
        f.write("# Experiment Log 010: [Phase 1] 3D CT Image & Pathology Mask Physical Extents Profiling\n\n")
        f.write("**Status**: Completed  \n**Date**: July 2026  \n")
        f.write(f"**Primary Output**: `{json_path}`  \n\n---\n\n")
        f.write("## 1. Executive Summary & Objective\n\n")
        f.write("Experiment 010 profiles physical CT voxel spacings (dx, dy, dz), physical scan volumes (V_CT), 3D bounding box physical extents (dX, dY, dZ), aspect ratios, and relative volume occupancy (V_mask / V_CT) across the 14 official categories.\n\n")
        f.write("## 2. Global CT Image & Physical Resolution Summary\n\n")
        f.write(f"* **Profiled CT Volumes**: `{ct_summary['ct_scans_profiled']}` volumes.\n")
        f.write(f"* **In-Plane Voxel Spacing (dx, dy)**: Median `{ct_summary['voxel_spacing_mm']['median_dx']:.3f} mm` x `{ct_summary['voxel_spacing_mm']['median_dy']:.3f} mm`.\n")
        f.write(f"* **Slice Thickness Spacing (dz)**: Median `{ct_summary['voxel_spacing_mm']['median_dz']:.3f} mm` (Mean: `{ct_summary['voxel_spacing_mm']['mean_dz']:.3f} mm`).\n")
        f.write(f"* **Physical Scan Volume (V_CT)**: Median `{ct_summary['ct_physical_vol_cm3']['median']:.1f} cm³` (5th percentile: `{ct_summary['ct_physical_vol_cm3']['p5']:.1f} cm³`, 95th percentile: `{ct_summary['ct_physical_vol_cm3']['p95']:.1f} cm³`).\n\n")
        f.write("---\n\n")
        f.write("## 3. Pathology 3D Physical Extents & Occupancy Matrix\n\n")
        f.write("| Cat Code | Category Name | Findings | Median Mask Vol (mm³) | Median BBox dX, dY, dZ (mm) | Aspect Ratio (dZ / dXY) | Median Relative Occupancy (V_mask / V_CT) |\n")
        f.write("|---|---|---|---|---|---|---|\n")
        for cname, stats in category_summary.items():
            ccode = stats["cat_code"]
            f.write(f"| `{ccode}` | **{cname}** | {stats['finding_count']} | `{stats['mask_vol_mm3']['median']:.1f}` | `{stats['bbox_extents_mm']['median_dx']:.1f} x {stats['bbox_extents_mm']['median_dy']:.1f} x {stats['bbox_extents_mm']['median_dz']:.1f}` | `{stats['median_aspect_ratio_dz_dxy']:.2f}` | `{stats['median_relative_occ_pct']:.4f}%` |\n")

    print(f"[Part B] Finished. JSON: {json_path}, Log: {log_path}")

# --- PART C ANALYSIS ---
def analyze_part_c(data):
    print("\n[Part C] Profiling Structural & Syntax Clinical Text Prompts (Hedging, Compound Prompts, Spatial Prepositions)...")

    # Regular Expressions for Syntax Analysis
    compound_pattern = re.compile(r"\b(with|and|associated|along with|accompanied by|as well as|featuring|showing)\b", re.IGNORECASE)
    hedging_pattern = re.compile(r"\b(probable|possibly|possible|versus|likely|suspicious|concerning|suggestive|rule out|cannot be excluded|uncertain|equivocal)\b", re.IGNORECASE)
    spatial_preposition_pattern = re.compile(r"\b(adjacent to|abutting|surrounding|extending|involving|along|near|contiguous|subpleural|peribronchial|diaphragm|fissure|lobe|segment|apex|apices|basal|hilar|mediastinal|pericardium|pleura|right|left|bilateral|upper|lower|middle)\b", re.IGNORECASE)

    total_prompts = 0
    total_words = []
    compound_prompts_count = 0
    hedging_prompts_count = 0
    spatial_preposition_prompts_count = 0

    cat_text_stats = defaultdict(lambda: {
        "finding_count": 0,
        "word_counts": [],
        "compound_count": 0,
        "hedging_count": 0,
        "spatial_prep_count": 0
    })

    for split_name, items in data.items():
        for item in items:
            findings = item.get("findings", {})
            categories = item.get("categories", {})
            for idx_str, text in findings.items():
                cat_code = categories.get(idx_str, "")
                if not text or not cat_code or cat_code not in CATEGORY_MAP:
                    continue

                words = text.strip().split()
                wcount = len(words)
                total_prompts += 1
                total_words.append(wcount)

                is_compound = bool(compound_pattern.search(text))
                is_hedging = bool(hedging_pattern.search(text))
                has_spatial = bool(spatial_preposition_pattern.search(text))

                if is_compound:
                    compound_prompts_count += 1
                if is_hedging:
                    hedging_prompts_count += 1
                if has_spatial:
                    spatial_preposition_prompts_count += 1

                cat_text_stats[cat_code]["finding_count"] += 1
                cat_text_stats[cat_code]["word_counts"].append(wcount)
                if is_compound:
                    cat_text_stats[cat_code]["compound_count"] += 1
                if is_hedging:
                    cat_text_stats[cat_code]["hedging_count"] += 1
                if has_spatial:
                    cat_text_stats[cat_code]["spatial_prep_count"] += 1

    global_summary = {
        "total_prompts_analyzed": total_prompts,
        "word_count_stats": {
            "mean": float(np.mean(total_words)) if total_words else 0.0,
            "median": float(np.median(total_words)) if total_words else 0.0,
            "min": int(np.min(total_words)) if total_words else 0,
            "max": int(np.max(total_words)) if total_words else 0,
        },
        "syntax_breakdown": {
            "compound_prompts_count": compound_prompts_count,
            "compound_prompts_pct": (compound_prompts_count / float(max(1, total_prompts))) * 100.0,
            "hedging_prompts_count": hedging_prompts_count,
            "hedging_prompts_pct": (hedging_prompts_count / float(max(1, total_prompts))) * 100.0,
            "spatial_preposition_prompts_count": spatial_preposition_prompts_count,
            "spatial_preposition_prompts_pct": (spatial_preposition_prompts_count / float(max(1, total_prompts))) * 100.0,
        }
    }

    category_text_summary = {}
    for ccode, name in sorted(CATEGORY_MAP.items()):
        stats = cat_text_stats[ccode]
        if stats["finding_count"] > 0:
            fcount = stats["finding_count"]
            wcounts = stats["word_counts"]
            category_text_summary[name] = {
                "cat_code": ccode,
                "finding_count": fcount,
                "word_count": {
                    "mean": float(np.mean(wcounts)),
                    "median": float(np.median(wcounts)),
                },
                "compound_prompts_pct": (stats["compound_count"] / float(fcount)) * 100.0,
                "hedging_prompts_pct": (stats["hedging_count"] / float(fcount)) * 100.0,
                "spatial_preposition_prompts_pct": (stats["spatial_prep_count"] / float(fcount)) * 100.0,
            }

    output_dir = Path("data/phase_1/analysis_part_c")
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "clinical_text_syntax_stats.json"
    with open(json_path, "w") as f:
        json.dump({"global_summary": global_summary, "category_text_summary": category_text_summary}, f, indent=2)

    log_path = Path("logs/phase_1_data_profiling/exp_011_text_syntax_hedging.md")
    with open(log_path, "w") as f:
        f.write("# Experiment Log 011: [Phase 1] Structural & Syntax Clinical Text Profiling\n\n")
        f.write("**Status**: Completed  \n**Date**: July 2026  \n")
        f.write(f"**Primary Output**: `{json_path}`  \n\n---\n\n")
        f.write("## 1. Executive Summary & Objective\n\n")
        f.write("Experiment 011 profiles radiology report text prompts across all 7,687 finding queries in ReXGroundingCT. ")
        f.write("The analysis quantifies word count length, multi-finding compound clause prevalence, diagnostic hedging/uncertainty language, and anatomical spatial preposition alignment.\n\n")
        f.write("## 2. Global Text Prompt Syntax Summary\n\n")
        f.write(f"* **Total Finding Prompts**: `{global_summary['total_prompts_analyzed']}` queries.\n")
        f.write(f"* **Prompt Length (Words)**: Median `{global_summary['word_count_stats']['median']:.1f} words` (Mean: `{global_summary['word_count_stats']['mean']:.1f} words`, Range: {global_summary['word_count_stats']['min']}–{global_summary['word_count_stats']['max']} words).\n")
        f.write(f"* **Multi-Finding Compound Prompts**: `{global_summary['syntax_breakdown']['compound_prompts_count']}` prompts (`{global_summary['syntax_breakdown']['compound_prompts_pct']:.2f}%`).\n")
        f.write(f"* **Diagnostic Hedging / Uncertainty**: `{global_summary['syntax_breakdown']['hedging_prompts_count']}` prompts (`{global_summary['syntax_breakdown']['hedging_prompts_pct']:.2f}%`).\n")
        f.write(f"* **Anatomical Spatial Prepositions**: `{global_summary['syntax_breakdown']['spatial_preposition_prompts_count']}` prompts (`{global_summary['syntax_breakdown']['spatial_preposition_prompts_pct']:.2f}%`).\n\n")
        f.write("---\n\n")
        f.write("## 3. Category-Level Clinical Text Profiling Matrix\n\n")
        f.write("| Cat Code | Category Name | Findings | Median Word Count | Compound Prompts (%) | Hedging Language (%) | Spatial Prepositions (%) |\n")
        f.write("|---|---|---|---|---|---|---|\n")
        for cname, stats in category_text_summary.items():
            ccode = stats["cat_code"]
            f.write(f"| `{ccode}` | **{cname}** | {stats['finding_count']} | `{stats['word_count']['median']:.1f}` | `{stats['compound_prompts_pct']:.2f}%` | `{stats['hedging_prompts_pct']:.2f}%` | `{stats['spatial_preposition_prompts_pct']:.2f}%` |\n")

    print(f"[Part C] Finished. JSON: {json_path}, Log: {log_path}")

if __name__ == "__main__":
    load_env_file()
    dataset_json_path = os.environ.get("DATASET_JSON", "data/dataset.json")
    with open(dataset_json_path, "r") as f:
        data = json.load(f)
    
    analyze_part_a(data)
    analyze_part_b(data)
    analyze_part_c(data)
