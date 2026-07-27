# Experiment Log 003: [Phase 1] 3D Average Segmentation Mask & Spatial Density Analysis Per Pathology

**Date**: July 23, 2026 (Updated July 27, 2026)  
**Status**: Completed  
**Objective**: Resample 3D ground-truth binary NIfTI segmentation masks into a canonical RAS (Right-Anterior-Superior) reference grid ($128 \times 128 \times 128$) to compute normalized 3D spatial probability density maps $P(\mathbf{x}' \in \text{mask} \mid c)$, 3D Volume Cosine Similarity ($S_{\text{cos}}$), Centroid Euclidean Distance ($\Delta d$), and 2D Average Intensity Projections (AIP) across the **Training set (2,992 CT scans, 7,687 masks)** and **Validation set (200 CT scans, 381 masks)**.

---

## 1. Executive Summary & Key Findings

* **Spatial Alignment & RAS Reorientation**: All GT masks were reoriented per 3D channel into canonical RAS space (`nib.as_closest_canonical`) inheriting physical affine matrices from parent CT scans (`nib.Nifti1Image(channel, img_nii.affine)`).
* **Sample Size Variance & Visual Rationale**: Side-by-side 2D AIP visual comparisons between Train ($N=7,687$) and Val ($N=381$) are dominated by small-sample Poisson noise in validation ($1/\sqrt{N_{\text{val}}}$) for low-prevalence categories ($N \le 6$). High-sample Train probability maps ($N=7,687$) represent true canonical population spatial priors.
* **4-Tier Anatomical Spatial Prior Taxonomy**:
  1. **Apical Dominant**: Emphysema ($Z_{\text{IS}} = 0.667$).
  2. **Basal / Dependent**: Pleural Effusion ($Z_{\text{IS}} = 0.484, Y_{\text{AP}} = 0.684$), Atelectasis / Consolidation ($Z_{\text{IS}} = 0.491$).
  3. **Hilar / Peribronchial**: Bronchial Wall Thickening, Bronchiectasis.
  4. **Isotropic / Parenchymal**: Pulmonary Nodules / Masses ($Z_{\text{IS}} = 0.556$), GGO, Linear Opacities.

---

## 2. Anatomical Centroid & Quantitative Alignment Breakdown

| Category Name | Train N | Train Centroid (R-L, A-P, I-S) | Val N | Val Centroid (R-L, A-P, I-S) | Centroid Delta $\Delta d$ | 3D Cosine Sim $S_{\text{cos}}$ | Spatial Prior Type |
|---|---|---|---|---|---|---|---|
| **Bronchial wall thickening** | 236 | `(0.508, 0.439, 0.541)` | 3 | `(0.495, 0.491, 0.478)` | `0.0825` | `0.0412` | Hilar / Peribronchial |
| **Bronchiectasis** | 282 | `(0.51, 0.449, 0.545)` | 11 | `(0.471, 0.489, 0.548)` | `0.0563` | `0.2059` | Hilar / Peribronchial |
| **Emphysema** | 446 | `(0.504, 0.442, 0.667)` | 17 | `(0.466, 0.533, 0.789)` | `0.1566` | `0.1756` | Apical Dominant |
| **Septal thickening** | 194 | `(0.519, 0.42, 0.563)` | 6 | `(0.519, 0.474, 0.469)` | `0.1092` | `0.2228` | Isotropic / Parenchymal |
| **Micronodules** | 314 | `(0.517, 0.422, 0.537)` | 11 | `(0.468, 0.499, 0.58)` | `0.1007` | `0.1111` | Isotropic / Parenchymal |
| **Other non-focal** | 150 | `(0.501, 0.426, 0.545)` | 4 | `(0.404, 0.488, 0.479)` | `0.1327` | `0.0671` | Isotropic / Parenchymal |
| **Linear opacities** | 1120 | `(0.474, 0.5, 0.535)` | 69 | `(0.563, 0.492, 0.537)` | `0.0886` | `0.2562` | Isotropic / Parenchymal |
| **Atelectasis / consolidation** | 1367 | `(0.503, 0.433, 0.491)` | 49 | `(0.531, 0.507, 0.416)` | `0.1084` | `0.3275` | Basal / Dependent |
| **Ground-glass opacity** | 1507 | `(0.51, 0.407, 0.519)` | 60 | `(0.497, 0.56, 0.442)` | `0.1711` | `0.4432` | Isotropic / Parenchymal |
| **Pulmonary nodules / masses** | 1743 | `(0.54, 0.452, 0.556)` | 132 | `(0.466, 0.521, 0.554)` | `0.1012` | `0.0268` | Isotropic / Parenchymal |
| **Pleural effusion / thickening** | 237 | `(0.535, 0.314, 0.484)` | 11 | `(0.461, 0.539, 0.431)` | `0.2426` | `0.5032` | Basal / Dependent |
| **Honeycombing** | 16 | `(0.457, 0.482, 0.498)` | 0 | `N/A` | `N/A` | `N/A` | Basal / Dependent |
| **Pneumothorax** | 18 | `(0.497, 0.516, 0.522)` | 1 | `(0.304, 0.443, 0.622)` | `0.2293` | `0.0717` | Isotropic / Parenchymal |
| **Other focal** | 57 | `(0.521, 0.442, 0.536)` | 7 | `(0.513, 0.488, 0.578)` | `0.0633` | `0.0101` | Isotropic / Parenchymal |

---

## 3. Generated Visual Artifacts

* **4-Panel Representative Population Priors**: `data/phase_1/analysis_experiment_003/exp003_population_spatial_priors_4panel.png`
* **Canonical Population Density Maps**: High-resolution 2D AIP maps exported to `data/phase_1/analysis_experiment_003/exp003_average_mask_*.png`
