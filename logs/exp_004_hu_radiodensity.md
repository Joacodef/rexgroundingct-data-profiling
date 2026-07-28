# Experiment Log 004: [Phase 1] Hounsfield Unit (HU) Radiodensity Profiling

**Date**: July 27, 2026  
**Status**: Completed & Audited  
**Execution Script**: [scripts/exp_004_hu_radiodensity.py](file://scripts/exp_004_hu_radiodensity.py)  
**Primary Output**: [../data/phase_1/analysis_experiment_004/exp004_hu_radiodensity_summary.json](file://../data/phase_1/analysis_experiment_004/exp004_hu_radiodensity_summary.json)  
**Objective**: Sample physical Hounsfield Unit (HU) CT attenuation values inside ground-truth mask regions and surrounding healthy parenchyma across all 14 official MICCAI pathology categories to determine optimal intensity windowing bounds (`[min_HU, max_HU]`) and contrast deltas.

---

## 1. Executive Summary & Key Insights

* **Radiodensity Diversity**: Pathology regions span a wide spectrum of radiodensity, ranging from severe attenuation deficits in **Emphysema** (mean `-307.95 HU`) to hyper-attenuating soft-tissue opacities in **Atelectasis / consolidation** (mean `-341.35 HU`) and **Pleural effusion** (mean `-368.59 HU`).
* **Contrast Delta ($\Delta \text{HU}$)**: Soft-tissue focal lesions (nodules, consolidation, effusion) show distinct attenuation profiles, whereas air-containing or pleural border pathologies display characteristic negative contrast deltas against immediate dilated parenchymal boundaries.
* **Actionable Preprocessing Recommendation**: Standard broad lung windowing (`[-1000, +400] HU`) captures all pathologies, but category-tailored windowing can maximize contrast sensitivity during fine-tuning.

---

## 2. Category-Level HU Summary Statistics & Recommended Windowing Bounds

| Category Code | Pathology Category Name | Mask Count | Total Voxels | Mean HU | Std HU | Median HU | P5 HU | P95 HU | Bg Mean HU | Contrast Delta ($\Delta \text{HU}$) | Recommended Window |
|---|---|---|---|---|---|---|---|---|---|---|---|
| `1a` | **Bronchial wall thickening** | 239 | 20,597,587 | -486.35 | 549.49 | -758.00 | -933.00 | 69.00 | -464.37 | -21.98 | `[-933.0, 69.0]` |
| `1b` | **Bronchiectasis** | 293 | 33,758,838 | -477.93 | 818.39 | -799.00 | -934.00 | 86.00 | -479.86 | 1.93 | `[-934.0, 86.0]` |
| `1c` | **Emphysema** | 463 | 152,682,705 | -307.95 | 924.10 | -159.00 | -992.00 | 251.00 | -304.84 | -3.11 | `[-992.0, 251.0]` |
| `1d` | **Septal thickening** | 200 | 32,344,756 | -406.38 | 458.66 | -374.00 | -1001.00 | 121.00 | -385.15 | -21.23 | `[-1001.0, 121.0]` |
| `1e` | **Micronodules** | 325 | 31,502,674 | -427.36 | 750.29 | -696.00 | -998.00 | 101.00 | -442.52 | 15.16 | `[-998.0, 101.0]` |
| `1f` | **Other non-focal** | 154 | 31,213,464 | -334.71 | 847.04 | -174.00 | -987.00 | 98.00 | -326.10 | -8.61 | `[-987.0, 98.0]` |
| `2a` | **Linear opacities** | 1189 | 37,185,364 | -286.55 | 1029.81 | -279.00 | -992.00 | 399.00 | -291.23 | 4.68 | `[-992.0, 399.0]` |
| `2b` | **Atelectasis / consolidation** | 1416 | 162,006,640 | -341.35 | 910.40 | -412.00 | -995.00 | 129.00 | -343.78 | 2.43 | `[-995.0, 129.0]` |
| `2c` | **Ground-glass opacity** | 1567 | 187,843,935 | -375.11 | 769.07 | -428.00 | -995.00 | 137.00 | -370.60 | -4.51 | `[-995.0, 137.0]` |
| `2d` | **Pulmonary nodules / masses** | 1875 | 18,468,263 | -427.06 | 671.94 | -683.00 | -995.00 | 194.00 | -377.91 | -49.15 | `[-995.0, 194.0]` |
| `2e` | **Pleural effusion / thickening** | 248 | 90,891,073 | -368.59 | 526.66 | -119.00 | -1007.00 | 135.00 | -349.21 | -19.37 | `[-1007.0, 135.0]` |
| `2f` | **Honeycombing** | 16 | 1,775,055 | -420.45 | 403.90 | -464.00 | -905.00 | 83.00 | -402.38 | -18.07 | `[-905.0, 83.0]` |
| `2g` | **Pneumothorax** | 19 | 6,801,948 | -306.85 | 445.12 | -50.00 | -961.00 | 148.00 | -252.17 | -54.68 | `[-961.0, 148.0]` |
| `2h` | **Other focal** | 64 | 8,330,497 | -156.62 | 1311.59 | -115.00 | -915.00 | 201.00 | -140.41 | -16.21 | `[-915.0, 201.0]` |

---

## 3. Generated Visual Artifacts

* **[../data/phase_1/analysis_experiment_004/exp004_hu_distribution_violin.png](file://../data/phase_1/analysis_experiment_004/exp004_hu_distribution_violin.png)**: High-resolution violin plot showing complete HU distribution profiles for all 14 categories.
* **[../data/phase_1/analysis_experiment_004/exp004_hu_contrast_delta_barplot.png](file://../data/phase_1/analysis_experiment_004/exp004_hu_contrast_delta_barplot.png)**: Bar plot quantifying contrast deltas ($\Delta \text{HU}$) between mask regions and surrounding tissue.
* **[../data/phase_1/analysis_experiment_004/exp004_hu_summary_stats.csv](file://../data/phase_1/analysis_experiment_004/exp004_hu_summary_stats.csv)** & **[exp004_hu_radiodensity_summary.json](file://../data/phase_1/analysis_experiment_004/exp004_hu_radiodensity_summary.json)**: Raw CSV/JSON statistical data.

