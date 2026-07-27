# Experiment Log 001: [Phase 1] Statistical Analysis of ReXGroundingCT Masks [COMPLETED]

> [!NOTE]
> **PIVOT NOTICE:**  
> The original plan for Experiment 004 (Exhaustive Multi-Finding Grounding) was discarded in favor of conducting a deep statistical analysis of the dataset's segmentation masks. This helps us understand the true distribution of findings and the gap between sparse annotations in the Train split vs exhaustive annotations in the Validation/Test splits.

* **Date:** July 2026
* **Status:** Completed

---

## 1. Objective
Perform a comprehensive statistical and visual analysis of the ReXGroundingCT dataset to understand dataset imbalances, average findings per volume, and the spatial distribution (heatmaps) of different pathologies.

## 2. Experimental Setup
* **Descriptive Statistics:** Computed volume sizes, unique entities per split, and absolute/relative segmentation volumes across Train and Validation datasets.
* **Spatial Heatmaps:** Generated Maximum Intensity Projections (MIP) in Coronal and Axial planes for the 8 most frequent pathologies.
* **Artifacts Generated:** Plots for entity counts, volume distributions, and 3D heatmaps.

## 3. Results & Findings

* **Dataset Disparity & Sparsity**:
  * **Train Split**: 2,992 CT scans containing 3,192 total findings (**~1.07 findings / scan**). Partial annotation protocol maps to an average of **`1.948` instances / finding** ($\pm 1.25$, Max: 11).
  * **Validation Split**: 200 CT scans containing 566 total findings (**~2.83 findings / scan**). Exhaustive annotation protocol maps to an average of **`3.714` instances / finding** ($\pm 3.82$, Max: **36 instances** for diffuse ground-glass opacities).
  * **Overall Dataset**: 3,192 CT scans, 3,758 total findings, averaging **`2.031` instances / finding** ($\pm 1.63$, Max: 36).

* **Positive-Unlabeled (PU) Strategy Rationale**:
  * The verified sparsity gap indicates that training background voxels contain unannotated true-positive findings. Preliminary observations support the hypothesis that standard fully-supervised BCE/Dice losses penalize predictions on unannotated true lesions, providing empirical rationale for evaluating PU-SPOCO and consistency learning.

* **Generated Artifacts**:
  * Plots and heatmap projections saved to `data/phase_1/analysis_experiment_001/`.
  * Detailed Analysis Scripts: `scripts/data_analysis/dataset_stats.py` and `scripts/data_analysis/mask_heatmaps.py`
