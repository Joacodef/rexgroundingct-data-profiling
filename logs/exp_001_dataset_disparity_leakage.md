# Experiment Log 001: [Phase 1] Dataset Disparity, Hierarchy & Patient Leakage Audit

**Date**: July 2026 (Consolidated July 27, 2026)  
**Status**: Completed  
**Primary Output**: `data/phase_1/analysis_experiment_001/exp001_disparity_leakage_summary.json`  
**Consolidated Script**: `scripts/data_analysis/exp_001_dataset_disparity_leakage.py`

---

## 1. Executive Summary & Objective

Experiment 001 quantifies the dataset composition across Train, Validation, and Test splits, evaluating finding density, mask instance fragmentation, positive-unlabeled (PU) annotation sparsity, and patient longitudinal hierarchy to audit cross-split patient leakage.

---

## 2. Dataset Disparity & Annotation Sparsity Matrix

| Split | Total CT Scans | Total Findings | Findings / Scan | Unique Patients | Mean Instances / Finding | Std Dev | Max Instances | Annotation Protocol |
|---|---|---|---|---|---|---|---|---|
| **Train** | 2,992 | 7,687 | `2.57` | 2,334 | `1.948` | $\pm 1.25$ | 11 | Partial / Sparse |
| **Validation** | 200 | 381 | `1.91` | 190 | `3.714` | $\pm 3.82$ | **36** | Exhaustive |
| **Test** | 300 | — | — | 281 | — | — | — | Exhaustive |
| **Total / Overall** | 3,192 | 8,068 | `2.53` | 2,752 | `2.031` | $\pm 1.63$ | 36 | Mixed |

### Key Scientific Findings:
1. **The Instance Sparsity Gap**:
   * Findings in the **Validation split** contain nearly double the mean instance count per finding prompt ($3.714 \pm 3.82$ vs $1.948 \pm 1.25$ in Train), peaking at **36 distinct connected components** per scan for diffuse ground-glass opacities (`2c`).
   * Training set ground-truth masks follow a partial annotation protocol ($\le 3$ instances annotated per finding query), leaving valid secondary instances unannotated in background voxels.
2. **Positive-Unlabeled (PU) Strategy Rationale**:
   * Standard fully-supervised Dice and BCE losses treat all background voxels as negative ($y=0$), penalizing unannotated true-positive findings in the training set and introducing instance suppression bias.
   * This provides the empirical foundation for implementing **Positive-Unlabeled (PU) SPOCO loss** and consistency fine-tuning during Phase 3.

---

## 3. Patient Hierarchy & Cross-Split Leakage Audit

A 3-tier ID decomposition was performed across all 3,192 scans to identify longitudinal scan series belonging to the same physical patient.

| Cross-Split Comparison | Overlapping Patients | Patient IDs | Action Taken |
|---|---|---|---|
| **Train $\leftrightarrow$ Val Overlap** | **2 patients** | `['1841', '2936']` | Flagged for validation isolation to prevent optimistic validation bias. |
| **Train $\leftrightarrow$ Test Overlap** | **3 patients** | `['3357', '3675', '39']` | Noted for final evaluation integrity. |
| **Val $\leftrightarrow$ Test Overlap** | **5 patients** | `['13119', '13278', '13479', '13492', '13583']` | Recorded in validation hierarchy metadata. |

---

## 4. Artifact & Script References

* **Summary Output JSON**: `data/phase_1/analysis_experiment_001/exp001_disparity_leakage_summary.json`
* **Analysis Entrypoint**: `scripts/data_analysis/exp_001_dataset_disparity_leakage.py`
