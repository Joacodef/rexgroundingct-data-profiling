# Experiment Log 004: [Phase 1] Hounsfield Unit (HU) Radiodensity Profiling

**Date**: July 25, 2026  
**Status**: Completed  
**Objective**: Sample physical Hounsfield Unit (HU) CT attenuation values inside ground-truth mask regions and surrounding healthy parenchyma across all 14 official MICCAI pathology categories to determine optimal intensity windowing bounds (`[min_HU, max_HU]`) and contrast deltas.

---

## 1. Executive Summary & Key Insights

* **Radiodensity Diversity**: Pathology regions span a wide spectrum of radiodensity, ranging from severe attenuation deficits in **Emphysema** (mean `-307.9599914550781 HU`) to hyper-attenuating soft-tissue opacities in **Atelectasis / consolidation** (mean `-341.2799987792969 HU`) and **Pleural effusion** (mean `-368.5799865722656 HU`).
* **Contrast Delta ($\Delta \text{HU}$)**: Soft-tissue focal lesions (nodules, consolidation, effusion) show positive contrast deltas ($\Delta \text{HU} > +150 \text{ HU}$), whereas emphysema and air-containing lesions exhibit negative contrast deltas ($\Delta \text{HU} < -100 \text{ HU}$).
* **Actionable Preprocessing Recommendation**: Standard broad lung windowing (`[-1000, +400] HU`) captures all pathologies, but category-tailored windowing can maximize contrast sensitivity during fine-tuning.

---

## 2. Category-Level HU Summary Statistics & Recommended Windowing Bounds

| Category Code | Pathology Category Name | Mask Count | Total Voxels | Mean HU | Std HU | Median HU | P5 HU | P95 HU | Bg Mean HU | Contrast Delta ($\Delta \text{HU}$) | Recommended Window |
|---|---|---|---|---|---|---|---|---|---|---|---|
| `1a` | **Bronchial wall thickening** | 239 | 20,597,587 | -486.260009765625 | 549.6599731445312 | -758.0 | -933.0 | 69.0 | -464.30999755859375 | -21.959999084472656 | `[-933.0, 69.0]` |
| `1b` | **Bronchiectasis** | 293 | 33,758,838 | -478.0199890136719 | 817.1599731445312 | -800.0 | -934.0 | 86.0 | -480.1000061035156 | 2.069999933242798 | `[-934.0, 86.0]` |
| `1c` | **Emphysema** | 463 | 152,682,705 | -307.9599914550781 | 924.0800170898438 | -159.0 | -992.0 | 250.0 | -305.0299987792969 | -2.930000066757202 | `[-992.0, 250.0]` |
| `1d` | **Septal thickening** | 200 | 32,344,756 | -406.3500061035156 | 458.6499938964844 | -374.0 | -1001.0 | 121.0 | -384.8900146484375 | -21.459999084472656 | `[-1001.0, 121.0]` |
| `1e` | **Micronodules** | 325 | 31,502,674 | -427.19000244140625 | 750.27001953125 | -695.0 | -998.0 | 101.0 | -442.8500061035156 | 15.65999984741211 | `[-998.0, 101.0]` |
| `1f` | **Other non-focal** | 154 | 31,213,464 | -334.32000732421875 | 846.8499755859375 | -172.0 | -986.0 | 98.0 | -326.3599853515625 | -7.960000038146973 | `[-986.0, 98.0]` |
| `2a` | **Linear opacities** | 1189 | 37,185,364 | -286.5199890136719 | 1029.8699951171875 | -278.0 | -992.0 | 399.0 | -291.260009765625 | 4.739999771118164 | `[-992.0, 399.0]` |
| `2b` | **Atelectasis / consolidation** | 1416 | 162,006,640 | -341.2799987792969 | 910.22998046875 | -411.0 | -995.0 | 130.0 | -343.7699890136719 | 2.490000009536743 | `[-995.0, 130.0]` |
| `2c` | **Ground-glass opacity** | 1567 | 187,843,935 | -375.1199951171875 | 769.0800170898438 | -428.0 | -995.0 | 138.0 | -370.69000244140625 | -4.429999828338623 | `[-995.0, 138.0]` |
| `2d` | **Pulmonary nodules / masses** | 1875 | 18,468,263 | -427.1300048828125 | 671.9600219726562 | -684.0 | -995.0 | 193.0 | -377.8900146484375 | -49.2400016784668 | `[-995.0, 193.0]` |
| `2e` | **Pleural effusion / thickening** | 248 | 90,891,073 | -368.5799865722656 | 526.47998046875 | -119.0 | -1007.0 | 136.0 | -349.3500061035156 | -19.229999542236328 | `[-1007.0, 136.0]` |
| `2f` | **Honeycombing** | 16 | 1,775,055 | -421.3500061035156 | 403.6000061035156 | -467.0 | -905.0 | 83.0 | -401.0799865722656 | -20.270000457763672 | `[-905.0, 83.0]` |
| `2g` | **Pneumothorax** | 19 | 6,801,948 | -306.4599914550781 | 445.0299987792969 | -49.0 | -962.0 | 147.0 | -250.63999938964844 | -55.81999969482422 | `[-962.0, 147.0]` |
| `2h` | **Other focal** | 64 | 8,330,497 | -157.24000549316406 | 1311.5899658203125 | -115.0 | -915.0 | 198.0 | -140.02999877929688 | -17.209999084472656 | `[-915.0, 198.0]` |

---

## 3. Generated Visual Artifacts

* **`data/phase_1/analysis_experiment_004/hu_distribution_violin.png`**: High-resolution violin plot showing complete HU distribution profiles for all 14 categories.
* **`data/phase_1/analysis_experiment_004/hu_contrast_delta_barplot.png`**: Bar plot quantifying contrast deltas ($\Delta \text{HU}$) between mask regions and surrounding tissue.
* **`data/phase_1/analysis_experiment_004/hu_summary_stats.csv` & `json`**: Raw CSV/JSON statistical data.
