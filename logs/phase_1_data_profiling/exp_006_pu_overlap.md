# Experiment Log 006: [Phase 1] Positive-Unlabeled (PU) Noise & Inter-Class Overlap Analysis

**Status**: Completed

## 1. Executive Summary

* **Mean Off-Diagonal Voxel IoU**: `0.0003`

## 2. PU Unannotated Contamination Estimation (Train vs Val Rates)

| Category Name | Train Annotated Rate | Val Exhaustive Rate | Estimated PU Unannotated Bias |
|---|---|---|---|
| **Bronchial wall thickening** | `0.071` | `0.015` | `0.000` |
| **Bronchiectasis** | `0.083` | `0.045` | `0.000` |
| **Emphysema** | `0.140` | `0.075` | `0.000` |
| **Septal thickening** | `0.061` | `0.030` | `0.000` |
| **Micronodules** | `0.080` | `0.055` | `0.000` |
| **Other non-focal** | `0.047` | `0.020` | `0.000` |
| **Linear opacities** | `0.268` | `0.315` | `0.047` |
| **Atelectasis / consolidation** | `0.304` | `0.200` | `0.000` |
| **Ground-glass opacity** | `0.377` | `0.265` | `0.000` |
| **Pulmonary nodules / masses** | `0.436` | `0.595` | `0.159` |
| **Pleural effusion / thickening** | `0.061` | `0.055` | `0.000` |
| **Honeycombing** | `0.005` | `0.000` | `0.000` |
| **Pneumothorax** | `0.005` | `0.005` | `0.000` |
| **Other focal** | `0.018` | `0.035` | `0.017` |

---
Voxel IoU heatmap saved to `data/phase_1/analysis_experiment_006/inter_class_iou_matrix.png`.
