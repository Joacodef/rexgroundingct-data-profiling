# Experiment Log 003: [Phase 1] 3D Spatial Centroids & Population Density Priors

**Date**: July 2026 (Consolidated July 27, 2026)  
**Status**: Completed  
**Primary Output**: `data/phase_1/analysis_experiment_003/exp003_spatial_density_priors_summary.json`  
**Consolidated Script**: `scripts/data_analysis/exp_003_spatial_density_priors.py`

---

## 1. Executive Summary & Objective

Experiment 003 quantifies 3D spatial coordinate distributions across all 14 official ReXGroundingCT finding categories. By mapping 3D ground-truth masks into a canonical $128 \times 128 \times 128$ Right-Anterior-Superior (RAS) grid, we compute relative spatial centroids $(RL, AP, IS)$, evaluate population probability density maps $P(\mathbf{x}' \in \text{mask} \mid c)$, measure spatial alignment metrics ($S_{cos}$ and $\Delta d$), and establish a **4-Tier Spatial Density Prior Taxonomy**.

---

## 2. 3D RAS Centroids & Spatial Prior Taxonomy Matrix

Relative centroid coordinates $(RL, AP, IS) \in [0.0, 1.0]^3$ represent normalized positions along Right-Left, Anterior-Posterior, and Inferior-Superior anatomical axes in canonical RAS space:

| Category Code | Finding Category | Train Masks | Val Masks | Train Centroid $(RL, AP, IS)$ | Val Centroid $(RL, AP, IS)$ | Centroid Shift $\Delta d$ | Cosine Sim $S_{cos}$ | 4-Tier Spatial Prior Taxonomy |
|---|---|---|---|---|---|---|---|---|
| **1a** | Bronchial wall thickening | 236 | 3 | `(0.508, 0.439, 0.541)` | `(0.495, 0.491, 0.478)` | `0.0825` | `0.0412` | Hilar / Peribronchial |
| **1b** | Bronchiectasis | 282 | 11 | `(0.510, 0.449, 0.545)` | `(0.471, 0.489, 0.548)` | `0.0563` | `0.2059` | Hilar / Peribronchial |
| **1c** | Emphysema | 446 | 17 | `(0.504, 0.442, 0.667)` | `(0.466, 0.533, 0.789)` | `0.1566` | `0.1756` | **Apical Dominant** |
| **1d** | Septal thickening | 194 | 6 | `(0.519, 0.420, 0.563)` | `(0.519, 0.474, 0.469)` | `0.1092` | `0.2228` | Isotropic / Parenchymal |
| **1e** | Micronodules | 314 | 11 | `(0.517, 0.422, 0.537)` | `(0.468, 0.499, 0.580)` | `0.1007` | `0.1111` | Isotropic / Parenchymal |
| **1f** | Other non-focal | 150 | 4 | `(0.501, 0.426, 0.545)` | `(0.404, 0.488, 0.479)` | `0.1327` | `0.0671` | Isotropic / Parenchymal |
| **2a** | Linear opacities | 1,120 | 69 | `(0.474, 0.500, 0.535)` | `(0.563, 0.492, 0.537)` | `0.0886` | `0.2562` | Isotropic / Parenchymal |
| **2b** | Atelectasis / consolidation | 1,367 | 49 | `(0.503, 0.433, 0.491)` | `(0.531, 0.507, 0.416)` | `0.1084` | `0.3275` | **Basal / Dependent** |
| **2c** | Ground-glass opacity | 1,507 | 60 | `(0.510, 0.407, 0.519)` | `(0.497, 0.560, 0.442)` | `0.1711` | `0.4432` | Isotropic / Parenchymal |
| **2d** | Pulmonary nodules / masses | 1,743 | 132 | `(0.540, 0.452, 0.556)` | `(0.466, 0.521, 0.554)` | `0.1012` | `0.0268` | Isotropic / Parenchymal |
| **2e** | Pleural effusion / thickening | 237 | 11 | `(0.535, 0.314, 0.484)` | `(0.461, 0.539, 0.431)` | `0.2426` | `0.5032` | **Basal / Dependent** |
| **2f** | Honeycombing | 16 | 0 | `(0.457, 0.482, 0.498)` | N/A | N/A | N/A | **Basal / Dependent** |
| **2g** | Pneumothorax | 18 | 1 | `(0.497, 0.516, 0.522)` | `(0.304, 0.443, 0.622)` | `0.2293` | `0.0717` | Isotropic / Parenchymal |
| **2h** | Other focal | 57 | 7 | `(0.521, 0.442, 0.536)` | `(0.513, 0.488, 0.578)` | `0.0633` | `0.0101` | Isotropic / Parenchymal |

---

## 3. Key Scientific Insights & Spatial Prior Taxonomy

### 1. Apical Dominant Taxonomy (Emphysema `1c`)
* **Apical Shift**: Emphysema exhibits an Inferior-Superior centroid of $IS = 0.667$ in Train ($IS = 0.789$ in Val), concentrating heavily in the upper pulmonary zones.

### 2. Basal / Dependent Taxonomy (Pleural Effusion `2e`, Atelectasis `2b`, Honeycombing `2f`)
* **Posterior & Inferior Concentration**: Pleural effusion (`2e`) demonstrates strong posterior/inferior localization with $AP = 0.314$ and $IS = 0.484$. Atelectasis (`2b`) and Honeycombing (`2f`) concentrate in dependent lung bases.

### 3. Hilar / Peribronchial Taxonomy (Bronchial Wall Thickening `1a`, Bronchiectasis `1b`)
* **Central Airway Radiating**: Airway-centered findings maintain tight central hilar centroids ($RL \approx 0.508-0.510, IS \approx 0.541-0.545$).

### 4. Isotropic / Parenchymal Taxonomy (Nodules `2d`, GGO `2c`, Linear Opacities `2a`)
* **Broad Parenchymal Distribution**: Nodules (`2d`), GGO (`2c`), and micronodules (`1e`) are widely distributed across mid-to-lower pulmonary fields ($IS \approx 0.52 - 0.56, RL \approx 0.51 - 0.54$).

---

## 4. Artifact & Script References

* **Summary Output JSON**: `data/phase_1/analysis_experiment_003/exp003_spatial_density_priors_summary.json`
* **Canonical Population 4-Panel Figure**: `data/phase_1/analysis_experiment_003/exp003_population_spatial_priors_4panel.png`
* **Analysis Entrypoint**: `scripts/data_analysis/exp_003_spatial_density_priors.py`
