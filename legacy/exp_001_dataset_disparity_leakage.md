# Experiment Log 001: [Phase 1] Dataset Disparity, Hierarchy & Patient Leakage Audit

**Date**: July 2026 (Consolidated July 28, 2026)  
**Status**: Completed & Audited  
**Execution Script**: [scripts/exp_001_dataset_disparity_leakage.py](file://scripts/exp_001_dataset_disparity_leakage.py)  
**Primary Output**: [../data/phase_1/analysis_experiment_001/exp001_disparity_leakage_summary.json](file://../data/phase_1/analysis_experiment_001/exp001_disparity_leakage_summary.json)  

---

## 1. Executive Summary & Objective

Experiment 001 provides a quantitative audit of the ReXGroundingCT dataset composition across Train (2,992 scans), Validation (200 scans), and Test (300 scans) splits. It analyzes finding density, scan prevalence, mask instance fragmentation, positive-unlabeled (PU) annotation sparsity, cross-pathology count variance, and longitudinal patient hierarchy to identify cross-split leakage.

---

## 2. Macro Dataset Composition & Disparity Matrix

| Split | Total CT Scans | Total Findings | Findings / Scan | Unique Patients | Mean Instances / Finding | Std Dev | Max Instances | Annotation Protocol |
|---|---|---|---|---|---|---|---|---|
| **Train** | 2,992 | 7,687 | `2.57` | 2,603 | `1.948` | $\pm 0.962$ | 11 | Partial / Sparse |
| **Validation** | 200 | 381 | `1.91` | 190 | `3.714` | $\pm 4.441$ | **36** | Exhaustive |
| **Test** | 300 | 582 | `1.94` | 281 | `1.000` | $\pm 0.000$ | 1* | Placeholder |
| **Total / Overall** | 3,192 | 8,650 | `2.71` | 3,063 | `2.000` | $\pm 1.630$ | 36 | Mixed |

*\*Note: Test split instance metadata is placeholder ($1.000 \pm 0.000$) due to official competition ground-truth mask withholding.*

---

## 3. Fine-Grained 14-Category Label Distribution & Disparity Breakdown

The table below breaks down finding frequencies, scan prevalence, and connected-component instance statistics across all 14 categories.

| Code | Category Name | Type | Train Count (%) | Train Prev. (%) | Val Count (%) | Val Prev. (%) | Train Mean Inst. (Med / IQR) | Val Mean Inst. (Med / IQR) | Val Max | Val CV | Disparity Ratio ($\text{Val}/\text{Train}$) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| `1a` | Bronchial wall thickening | Non-Focal | 236 (3.07%) | 7.09% | 3 (0.79%) | 1.50% | 2.047 (2.0 / 1.25) | 4.000 (5.0 / 2.50) | 6 | 0.540 | **1.95x** |
| `1b` | Bronchiectasis | Non-Focal | 282 (3.67%) | 8.26% | 11 (2.89%) | 4.50% | 2.096 (2.0 / 2.00) | 3.273 (2.0 / 3.00) | 10 | 0.845 | **1.56x** |
| `1c` | Emphysema | Non-Focal | 446 (5.80%) | 13.97% | 17 (4.46%) | 7.50% | 2.388 (2.0 / 1.00) | 2.824 (2.0 / 2.00) | 12 | 0.935 | **1.18x** |
| `1d` | Septal thickening | Non-Focal | 194 (2.52%) | 6.15% | 6 (1.57%) | 3.00% | 2.222 (2.0 / 1.00) | 5.500 (4.0 / 4.50) | 10 | 0.522 | **2.48x** |
| `1e` | Micronodules | Non-Focal | 314 (4.08%) | 7.99% | 11 (2.89%) | 5.50% | 2.207 (2.0 / 2.00) | 5.182 (4.0 / 4.00) | 12 | 0.609 | **2.35x** |
| `1f` | Other non-focal | Non-Focal | 150 (1.95%) | 4.75% | 4 (1.05%) | 2.00% | 2.080 (2.0 / 2.00) | 2.750 (1.5 / 2.25) | 7 | 0.905 | **1.32x** |
| `2a` | Linear opacities | Focal | 1,120 (14.57%) | 26.77% | 69 (18.11%) | 31.50% | 1.714 (2.0 / 1.00) | 2.246 (2.0 / 1.00) | 7 | 0.748 | **1.31x** |
| `2b` | Atelectasis / consolidation | Focal | 1,367 (17.78%) | 30.45% | 49 (12.86%) | 20.00% | 1.783 (1.0 / 2.00) | 2.776 (2.0 / 2.00) | 14 | 1.033 | **1.56x** |
| `2c` | Ground-glass opacity | Focal | 1,507 (19.60%) | 37.73% | 60 (15.75%) | 26.50% | 2.230 (2.0 / 2.00) | 7.133 (4.0 / 9.25) | **36** | **1.127** | **3.20x** |
| `2d` | Pulmonary nodules / masses | Focal | 1,743 (22.67%) | 43.62% | 132 (34.65%) | 59.50% | 1.827 (1.0 / 2.00) | 3.530 (2.0 / 3.00) | 22 | 0.982 | **1.93x** |
| `2e` | Pleural effusion / thickening | Focal | 237 (3.08%) | 6.08% | 11 (2.89%) | 5.50% | 1.430 (1.0 / 1.00) | 2.000 (2.0 / 1.50) | 5 | 0.603 | **1.40x** |
| `2f` | Honeycombing | Focal | 16 (0.21%) | 0.50% | 0 (0.00%) | 0.00% | 2.062 (2.0 / 1.00) | N/A | N/A | N/A | N/A |
| `2g` | Pneumothorax | Focal | 36 (0.47%) | 1.20% | 5 (1.31%) | 2.50% | 1.194 (1.0 / 0.00) | 1.400 (1.0 / 1.00) | 2 | 0.393 | **1.17x** |
| `2h` | Other focal | Focal | 29 (0.38%) | 0.97% | 3 (0.79%) | 1.50% | 1.276 (1.0 / 0.00) | 2.000 (2.0 / 1.00) | 3 | 0.433 | **1.57x** |

---

## 4. Grouped Pathology Taxonomy Aggregates

| Group | Categories | Train Findings | Val Findings | Train Mean Inst. | Val Mean Inst. | Disparity Ratio ($\text{Val}/\text{Train}$) |
|---|---|---|---|---|---|---|
| **Non-Focal** | `1a`–`1f` | 1,622 | 52 | 2.204 | 3.788 | **1.72x** |
| **Focal** | `2a`–`2h` | 6,065 | 329 | 1.879 | 3.702 | **1.97x** |

---

## 5. Cross-Pathology Finding Count & Instance Variance Analysis

1. **Diffuse / Multi-Focal vs. Localized Instance Distribution**:
   - **Ground-Glass Opacity (`2c`)** exhibits the highest instance fragmentation in exhaustive validation ground truth, with a mean of **7.133** instances ($\text{IQR} = 9.25$, peak = **36 instances**, $CV = 1.127$). It exhibits a **3.20x disparity ratio** compared to the partially annotated training split ($2.230$ mean instances).
   - **Pulmonary Nodules / Masses (`2d`)** is the most prevalent category across all splits (43.62% Train, 59.50% Val, 53.67% Test scan prevalence). Under exhaustive validation, it averages **3.530 instances** (max 22, $CV = 0.982$) compared to $1.827$ in Train (**1.93x disparity**).
   - **Septal Thickening (`1d`)** and **Micronodules (`1e`)** show substantial annotation disparity (**2.48x** and **2.35x** ratios), with validation instance counts averaging $5.500$ and $5.182$ respectively.

2. **Low-Variance Focal Pathologies**:
   - Focal entities like **Pneumothorax (`2g`)** ($1.400$ Val mean, $CV = 0.393$), **Pleural Effusion (`2e`)** ($2.000$ Val mean, $CV = 0.603$), and **Other Focal (`2h`)** ($2.000$ Val mean, $CV = 0.433$) exhibit bounded instance counts ($\le 5$) with minimal cross-split variance.

3. **Methodological Justification for PU Fine-Tuning**:
   - Training set ground truth caps annotated instances at $\le 3$ per finding query, leaving valid secondary instances unannotated in background voxels.
   - Training standard fully-supervised Dice or BCE loss forces the model to penalize unannotated true-positive instances, creating severe **instance suppression bias**. This provides the empirical justification for **Positive-Unlabeled (PU) SPOCO loss** in Phase 3.

---

## 6. Patient Hierarchy & Cross-Split Leakage Audit

A 3-tier ID decomposition was performed across all 3,192 scans to identify longitudinal scan series belonging to the same physical patient.

| Cross-Split Comparison | Overlapping Patients | Patient IDs | Action Taken |
|---|---|---|---|
| **Train $\leftrightarrow$ Val Overlap** | **2 patients** | `['1841', '2936']` | Flagged for validation isolation to prevent optimistic validation bias. |
| **Train $\leftrightarrow$ Test Overlap** | **4 patients** | `['302', '3357', '3675', '39']` | Noted for final evaluation integrity. |
| **Val $\leftrightarrow$ Test Overlap** | **5 patients** | `['13119', '13278', '13479', '13492', '13583']` | Recorded in validation hierarchy metadata. |

---

## 7. Generated Artifacts & Figures

* **Summary Output JSON**: [../data/phase_1/analysis_experiment_001/exp001_disparity_leakage_summary.json](file://../data/phase_1/analysis_experiment_001/exp001_disparity_leakage_summary.json)
* **Category Frequency Proportion Figure**: [../data/phase_1/analysis_experiment_001/exp001_category_frequency_breakdown.png](file://../data/phase_1/analysis_experiment_001/exp001_category_frequency_breakdown.png)
* **Findings per Scan Distribution Figure**: [../data/phase_1/analysis_experiment_001/exp001_findings_per_scan.png](file://../data/phase_1/analysis_experiment_001/exp001_findings_per_scan.png)
* **Instance Count Boxplot Figure**: [../data/phase_1/analysis_experiment_001/exp001_instance_count_boxplot.png](file://../data/phase_1/analysis_experiment_001/exp001_instance_count_boxplot.png)
* **Heatmap Visualization Figure**: [../data/phase_1/analysis_experiment_001/exp001_cooccurrence_heatmap.png](file://../data/phase_1/analysis_experiment_001/exp001_cooccurrence_heatmap.png)
* **Execution Script**: [scripts/exp_001_dataset_disparity_leakage.py](file://scripts/exp_001_dataset_disparity_leakage.py)
