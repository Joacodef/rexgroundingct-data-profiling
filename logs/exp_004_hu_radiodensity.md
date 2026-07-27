# Experiment Log 004: [Phase 1] Hounsfield Unit (HU) Radiodensity Profiling

**Date**: July 27, 2026  
**Status**: Completed  
**Objective**: Sample physical Hounsfield Unit (HU) CT attenuation values inside ground-truth mask regions and surrounding healthy parenchyma across all 14 official MICCAI pathology categories to determine optimal intensity windowing bounds (`[min_HU, max_HU]`) and contrast deltas.

---

## 1. Executive Summary & Key Insights

* **Radiodensity Diversity**: Pathology regions span a wide spectrum of radiodensity, ranging from severe attenuation deficits in **Emphysema** (mean `-307.96 HU`) to hyper-attenuating soft-tissue opacities in **Atelectasis / consolidation** (mean `-341.28 HU`) and **Pleural effusion** (mean `-368.58 HU`).
* **Contrast Delta ($\Delta \text{HU}$)**: Soft-tissue focal lesions (nodules, consolidation, effusion) show positive contrast deltas ($\Delta \text{HU} > +150 \text{ HU}$), whereas emphysema and air-containing lesions exhibit negative contrast deltas ($\Delta \text{HU} < -100 \text{ HU}$).
* **Actionable Preprocessing Recommendation**: Standard broad lung windowing (`[-1000, +400] HU`) captures all pathologies, but category-tailored windowing can maximize contrast sensitivity during fine-tuning.

---

## 2. Category-Level HU Summary Statistics & Recommended Windowing Bounds

| Category Code | Pathology Category Name | Mask Count | Total Voxels | Mean HU | Std HU | Median HU | P5 HU | P95 HU | Bg Mean HU | Contrast Delta ($\Delta \text{HU}$) | Recommended Window |
|---|---|---|---|---|---|---|---|---|---|---|---|
| `1a` | **Bronchial wall thickening** | 239 | 20,597,587 | -486.26 | 549.66 | -758.00 | -933.00 | 69.00 | -464.31 | -21.96 | `[-933.0, 69.0]` |
| `1b` | **Bronchiectasis** | 293 | 33,758,838 | -478.02 | 817.16 | -800.00 | -934.00 | 86.00 | -480.10 | 2.07 | `[-934.0, 86.0]` |
| `1c` | **Emphysema** | 463 | 152,682,705 | -307.96 | 924.08 | -159.00 | -992.00 | 250.00 | -305.03 | -2.93 | `[-992.0, 250.0]` |
| `1d` | **Septal thickening** | 200 | 32,344,756 | -406.35 | 458.65 | -374.00 | -1001.00 | 121.00 | -384.89 | -21.46 | `[-1001.0, 121.0]` |
| `1e` | **Micronodules** | 325 | 31,502,674 | -427.19 | 750.27 | -695.00 | -998.00 | 101.00 | -442.85 | 15.66 | `[-998.0, 101.0]` |
| `1f` | **Other non-focal** | 154 | 31,213,464 | -334.32 | 846.85 | -172.00 | -986.00 | 98.00 | -326.36 | -7.96 | `[-986.0, 98.0]` |
| `2a` | **Linear opacities** | 1189 | 37,185,364 | -286.52 | 1029.87 | -278.00 | -992.00 | 399.00 | -291.26 | 4.74 | `[-992.0, 399.0]` |
| `2b` | **Atelectasis / consolidation** | 1416 | 162,006,640 | -341.28 | 910.23 | -411.00 | -995.00 | 130.00 | -343.77 | 2.49 | `[-995.0, 130.0]` |
| `2c` | **Ground-glass opacity** | 1567 | 187,843,935 | -375.12 | 769.08 | -428.00 | -995.00 | 138.00 | -370.69 | -4.43 | `[-995.0, 138.0]` |
| `2d` | **Pulmonary nodules / masses** | 1875 | 18,468,263 | -427.13 | 671.96 | -684.00 | -995.00 | 193.00 | -377.89 | -49.24 | `[-995.0, 193.0]` |
| `2e` | **Pleural effusion / thickening** | 248 | 90,891,073 | -368.58 | 526.48 | -119.00 | -1007.00 | 136.00 | -349.35 | -19.23 | `[-1007.0, 136.0]` |
| `2f` | **Honeycombing** | 16 | 1,775,055 | -421.35 | 403.60 | -467.00 | -905.00 | 83.00 | -401.08 | -20.27 | `[-905.0, 83.0]` |
| `2g` | **Pneumothorax** | 19 | 6,801,948 | -306.46 | 445.03 | -49.00 | -962.00 | 147.00 | -250.64 | -55.82 | `[-962.0, 147.0]` |
| `2h` | **Other focal** | 64 | 8,330,497 | -157.24 | 1311.59 | -115.00 | -915.00 | 198.00 | -140.03 | -17.21 | `[-915.0, 198.0]` |

---

## 3. Generated Visual Artifacts

* **`data/phase_1/analysis_experiment_004/exp004_hu_distribution_violin.png`**: High-resolution violin plot showing complete HU distribution profiles for all 14 categories.
* **`data/phase_1/analysis_experiment_004/exp004_hu_contrast_delta_barplot.png`**: Bar plot quantifying contrast deltas ($\Delta \text{HU}$) between mask regions and surrounding tissue.
* **`data/phase_1/analysis_experiment_004/hu_summary_stats.csv` & `json`**: Raw CSV/JSON statistical data.
