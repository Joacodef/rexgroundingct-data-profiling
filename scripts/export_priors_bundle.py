"""
Phase 1 Empirical Priors Bundle Exporter for ReXGroundingCT.

This script consolidates analysis summaries from all 5 profiling experiments
(exp_001 to exp_005) into a unified JSON artifact:
    ../data/phase_1/phase_1_priors_bundle.json

This artifact provides downstream training & inference pipelines (e.g. VoxTell fine-tuning
in rexgroundingct-model-training) with canonical spatial priors, HU windowing bounds,
component topology thresholds, and category disparity multipliers.
"""

import json
from pathlib import Path
from datetime import datetime
from config import DATA_DIR, CATEGORY_MAP, NON_FOCAL_CATEGORIES, SPATIAL_TAXONOMY

def export_priors_bundle():
    phase_1_dir = DATA_DIR / "phase_1"
    exp001_file = phase_1_dir / "analysis_experiment_001" / "exp001_disparity_leakage_summary.json"
    exp002_file = phase_1_dir / "analysis_experiment_002" / "exp002_nlp_prompt_syntax_summary.json"
    exp003_file = phase_1_dir / "analysis_experiment_003" / "exp003_spatial_density_priors_summary.json"
    exp004_file = phase_1_dir / "analysis_experiment_004" / "exp004_hu_radiodensity_summary.json"
    exp005_file = phase_1_dir / "analysis_experiment_005" / "exp005_morphology_noise_pruning_summary.json"

    # Verify input files existence
    for fpath in [exp001_file, exp002_file, exp003_file, exp004_file, exp005_file]:
        if not fpath.exists():
            raise FileNotFoundError(f"Required experiment summary missing: {fpath}")

    # 1. Load raw JSON summaries
    with open(exp001_file, "r") as f:
        exp001 = json.load(f)
    with open(exp002_file, "r") as f:
        exp002 = json.load(f)
    with open(exp003_file, "r") as f:
        exp003 = json.load(f)
    with open(exp004_file, "r") as f:
        exp004 = json.load(f)
    with open(exp005_file, "r") as f:
        exp005 = json.load(f)

    # Index Exp 003, Exp 004, Exp 005 by category code
    exp003_map = {item["CategoryCode"]: item for item in exp003}
    exp004_map = {item["Category Code"]: item for item in exp004}
    
    # exp005 is keyed by category name
    exp005_map = {}
    for cat_name, cat_data in exp005.items():
        code = cat_data.get("cat_code")
        if code:
            exp005_map[code] = cat_data

    # 2. Build Category Priors Dictionary
    category_priors = {}
    exp001_cat_disparity = exp001.get("CategoryLevelDisparity", {})

    for code, name in CATEGORY_MAP.items():
        e1 = exp001_cat_disparity.get(code, {})
        e3 = exp003_map.get(code, {})
        e4 = exp004_map.get(code, {})
        e5 = exp005_map.get(code, {})

        pathology_type = "Non-Focal" if code in NON_FOCAL_CATEGORIES else "Focal"

        category_priors[code] = {
            "category_code": code,
            "category_name": name,
            "pathology_type": pathology_type,
            "disparity_summary": {
                "train_findings_count": e1.get("TrainFindingsCount", 0),
                "val_findings_count": e1.get("ValFindingsCount", 0),
                "test_findings_count": e1.get("TestFindingsCount", 0),
                "train_scan_prevalence_pct": e1.get("TrainScanPrevalencePct", 0.0),
                "val_scan_prevalence_pct": e1.get("ValScanPrevalencePct", 0.0),
                "train_mean_instances": e1.get("TrainInstanceStats", {}).get("Mean", 1.0),
                "val_mean_instances": e1.get("ValInstanceStats", {}).get("Mean", 1.0),
                "disparity_ratio_val_vs_train": e1.get("DisparityRatio_Val_vs_Train", 1.0)
            },
            "spatial_prior": {
                "taxonomy": SPATIAL_TAXONOMY.get(code, e3.get("SpatialPriorType", "Isotropic / Parenchymal")),
                "train_centroid_ras": [
                    e3.get("TrainCentroid_RL", 0.5),
                    e3.get("TrainCentroid_AP", 0.5),
                    e3.get("TrainCentroid_IS", 0.5)
                ],
                "val_centroid_ras": [
                    e3.get("ValCentroid_RL", 0.5),
                    e3.get("ValCentroid_AP", 0.5),
                    e3.get("ValCentroid_IS", 0.5)
                ],
                "centroid_delta_d": e3.get("CentroidDelta_d", None),
                "cosine_similarity_scos": e3.get("CosineSimilarity_Scos", None)
            },
            "hu_intensity_windowing": {
                "recommended_window_min": e4.get("Recommended Window Min", -1024.0),
                "recommended_window_max": e4.get("Recommended Window Max", 3071.0),
                "mean_hu": e4.get("Mean HU", 0.0),
                "std_hu": e4.get("Std HU", 0.0),
                "median_hu": e4.get("Median HU", 0.0),
                "p5_hu": e4.get("P5 HU", -1024.0),
                "p95_hu": e4.get("P95 HU", 3071.0),
                "bg_mean_hu": e4.get("Bg Mean HU", 0.0),
                "contrast_delta_hu": e4.get("Contrast Delta HU", 0.0)
            },
            "component_topology": {
                "recommended_min_size_voxels": e5.get("recommended_min_size_voxels", 10),
                "total_components_count": e5.get("total_components_count", 0),
                "mean_components_per_finding": e5.get("mean_components_per_finding", 0.0),
                "mean_sphericity": e5.get("mean_sphericity", 0.0),
                "mean_sa_v_ratio": e5.get("mean_sa_v_ratio", 0.0),
                "physical_extent_mm": {
                    "extent_x_mm": e5.get("physical_extent_mm_stats", {}).get("mean_extent_X_mm", 0.0),
                    "extent_y_mm": e5.get("physical_extent_mm_stats", {}).get("mean_extent_Y_mm", 0.0),
                    "extent_z_mm": e5.get("physical_extent_mm_stats", {}).get("mean_extent_Z_mm", 0.0),
                    "aspect_ratio_z_vs_xy": e5.get("physical_extent_mm_stats", {}).get("mean_aspect_ratio_Z_vs_XY", 0.0)
                },
                "component_voxel_stats": e5.get("component_voxel_stats", {}),
                "component_vol_mm3_stats": e5.get("component_vol_mm3_stats", {})
            }
        }

    # 3. Assemble Full Bundle Document
    priors_bundle = {
        "bundle_metadata": {
            "version": "1.0.0",
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "description": "Consolidated Phase 1 empirical priors bundle from ReXGroundingCT data profiling.",
            "source_dataset": "ReXGroundingCT Challenge 2026 (3,063 unique patients, 3,492 CT scans)",
            "categories_count": 14
        },
        "dataset_split_summary": exp001.get("SplitSummary", {}),
        "patient_leakage_audit": exp001.get("PatientLeakageAudit", {}),
        "cooccurrence_matrix_14x14": exp001.get("ScanLevelCoOccurrenceMatrix", {}),
        "nlp_prompt_priors": {
            "global_summary": exp002.get("global_summary", {}),
            "validation_text_shift": exp002.get("validation_text_shift", {})
        },
        "category_priors": category_priors
    }

    # 4. Save to output JSON file
    output_bundle_path = phase_1_dir / "phase_1_priors_bundle.json"
    with open(output_bundle_path, "w") as f:
        json.dump(priors_bundle, f, indent=2)

    print(f"✅ Successfully exported Empirical Priors Bundle to: {output_bundle_path}")
    print(f"   Bundle contains priors for {len(category_priors)} finding categories.")
    print(f"   File size: {output_bundle_path.stat().st_size / 1024:.2f} KB")

if __name__ == "__main__":
    export_priors_bundle()
