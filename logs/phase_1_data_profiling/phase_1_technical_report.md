# Comprehensive Phase 1 Technical Report: ReXGroundingCT Data Profiling & Analysis

> [!NOTE]
> **DOCUMENT ROLE CONTRACT: CONSOLIDATED TECHNICAL REPORT**
> This report synthesizes quantitative findings across all 11 data profiling experiments (`exp_001` through `exp_011`) conducted during Phase 1 of the ReXGroundingCT research roadmap.
> Data artifacts reside in `data/phase_1/` and individual experiment logs reside in `logs/phase_1_data_profiling/`.

---

## 1. Executive Summary & Research Context

Phase 1 establishes the quantitative foundation for 3D text-to-segmentation grounding on the ReXGroundingCT benchmark. Across 3,192 CT scans and 8,650 radiology report finding prompts, this investigation profiles:
1. **Annotation Disparity & Instance Fragmentation**: Quantifying the gap between partially labeled training scans (~1.07 findings/scan) and exhaustively labeled validation scans (~2.83 findings/scan).
2. **Text Prompt Shift & Syntactic Complexity**: Evaluating the shift from short paper queries (mean 11 words) to long multi-clause report sentences (up to 38 words, +12.4% commas, -45.2% TTR), multi-finding compound prompts (18.77%), hedging (0.38%), and spatial prepositions (72.53%).
3. **Anatomical Spatial Priors & Density Maps**: Resampling 3D GT masks into canonical RAS space ($128 \times 128 \times 128$) to extract centroid probability density distributions per pathology.
4. **Radiodensity (HU) Attenuation**: Sampling physical CT attenuation inside and around masks to define intensity windowing bounds (`[-1000, +400] HU`).
5. **Structural Resolution & Inter-Class Overlap**: Measuring physical voxel spacings ($\Delta x=\Delta y=0.710\text{ mm}, \Delta z=1.053\text{ mm}$), voxel-level IoU overlap (`2a` $\cap$ `2b` IoU = `0.0264`), and Positive-Unlabeled (PU) background contamination (`2d` Nodules = `+15.88%`).
6. **3D Morphological Topology & Size Thresholds**: Profiling sphericity indices ($S \in [0.543, 0.942]$), 33,408 3D connected component volume quantiles, and deriving `recommended_min_size_voxels` noise-filtering floors (15 voxels for Nodules `2d`, 47 voxels for Other Non-Focal `1f`, 10 voxels default).
7. **Patient Hierarchy & Cross-Split Leakage**: Auditing 3-tier IDs (`patient_id`, `scan_id`, `reconstruction_id`) across 2,805 unique patients, profiling 212 longitudinal multi-scan patients (up to 6 scans), and detecting 2 Train<->Val and 3 Train<->Test overlapping longitudinal patients.
8. **3D Physical Extents & Relative Occupancy**: Measuring global CT volume (median $101,842.9\text{ cm}^3$), 3D bounding box extents ($\Delta X, \Delta Y, \Delta Z$), aspect ratios ($\Delta Z / \Delta XY$), and relative volume occupancy ($V_{\text{mask}} / V_{\text{CT}}$) per category.

---

## 2. Statistical Analysis of Dataset Masks & Instance Fragmentation (Exp 001 & 005)

### A. Split Disparity & Annotation Sparsity
Quantitative analysis of `dataset.json` indicates a significant disparity in annotation density between the training set and validation set:

| Partition | Total CT Scans | Total Findings | Mean Findings / Scan | Mean Instances / Finding | Max Instances / Finding | Annotation Protocol |
|---|---|---|---|---|---|---|
| **Training Split** | 2,992 | 3,192 | **`1.07`** | **`1.948` $\pm 1.25$** | 11 | **Partial** (Up to 3 instances labeled) |
| **Validation Split** | 200 | 566 | **`2.83`** | **`3.714` $\pm 3.82$** | **36** | **Exhaustive** (All visible instances labeled) |
| **Overall Dataset** | **3,192** | **3,758** | **`1.18`** | **`2.031` $\pm 1.63$** | **36** | Mixed |

### B. Category-Level Prevalence & Instance Multiplicity
Analysis across the 14 official MICCAI categories reveals distinct multi-instance fragmentation patterns:

| Category Code | Pathology Category Name | Total Scans | Mean Instances / Finding | Max Instances | Morphological Topology Type |
|---|---|---|---|---|---|
| `1a` | **Bronchial wall thickening** | 239 | `6.44` | 1539 blobs total | Diffuse / Tubular |
| `1b` | **Bronchiectasis** | 293 | `3.44` | 1007 blobs total | Diffuse / Branching |
| `1c` | **Emphysema** | 463 | `4.92` | 2279 blobs total | Diffuse / Parenchymal |
| `1d` | **Septal thickening** | 200 | `3.63` | 726 blobs total | Interstitial / Planar |
| `1e` | **Micronodules** | 325 | `3.72` | 1210 blobs total | Multi-focal / Compact |
| `1f` | **Other non-focal** | 154 | `3.05` | 469 blobs total | Non-focal |
| `2a` | **Linear opacities** | 1,189 | `2.73` | 3248 blobs total | Focal / Linear |
| `2b` | **Atelectasis / consolidation** | 1,416 | `4.00` | 5662 blobs total | Focal / Parenchymal |
| `2c` | **Ground-glass opacity** | 1,567 | `3.88` | **36** per scan | Diffuse / Infiltrative |
| `2d` | **Pulmonary nodules / masses** | 1,874 | `2.05` | 22 per scan | Focal / Spherical |
| `2e` | **Pleural effusion / thickening** | 248 | `3.02` | 749 blobs total | Boundary / Dependent |
| `2f` | **Honeycombing** | 16 | `3.44` | 55 blobs total | Subpleural / Cystic |
| `2g` | **Pneumothorax** | 19 | `4.42` | 84 blobs total | Pleural / Avarice |
| `2h` | **Other focal** | 64 | `3.03` | 194 blobs total | Focal |

---

## 3. Free-Text Prompt Syntax & Text Shift Analysis (Exp 002, 007 & 011)

### A. Quantitative NLP Text Metrics
Comparison between original paper queries and full MICCAI validation prompts indicates significant syntactic complexity:

| Metric | Full Dataset Prompts (Exp 011) | Shift & Syntax Characteristics |
|---|---|---|
| **Total Prompts Analyzed** | **8,650 prompts** | Complete dataset coverage across 3,192 scans |
| **Mean Word Count** | **10.8 words** | Range: 1 to 38 words per query |
| **Median Word Count** | **10.0 words** | Standard sentence-length query |
| **Multi-Finding Compound Prompts** | **1,624 prompts (18.77%)** | Prompts containing conjunctions / secondary findings |
| **Diagnostic Hedging Language** | **33 prompts (0.38%)** | Clinical uncertainty phrases (*"probable"*, *"possible"*) |
| **Anatomical Spatial Prepositions** | **6,274 prompts (72.53%)** | Explicit locators (*"right lower lobe"*, *"adjacent to fissure"*) |

### B. Category-Level NLP Syntax Matrix (Exp 011)

| Cat Code | Category Name | Findings | Median Word Count | Compound Prompts (%) | Hedging Language (%) | Spatial Prepositions (%) |
|---|---|---|---|---|---|---|
| `1a` | **Bronchial wall thickening** | 245 | `7.0` | `10.20%` | `0.00%` | **`86.94%`** |
| `1b` | **Bronchiectasis** | 304 | `9.0` | `17.43%` | `0.00%` | `53.29%` |
| `1c` | **Emphysema** | 490 | `6.0` | `5.71%` | `0.00%` | `35.31%` |
| `1d` | **Septal thickening** | 209 | `9.0` | `20.57%` | `0.48%` | `61.24%` |
| `1e` | **Micronodules** | 341 | `10.0` | `17.30%` | `0.00%` | `61.58%` |
| `1f` | **Other non-focal** | 158 | `7.0` | `10.76%` | `0.63%` | `41.14%` |
| `2a` | **Linear opacities** | 1,302 | `10.0` | `18.97%` | `0.61%` | `82.41%` |
| `2b` | **Atelectasis / consolidation** | 1,505 | `11.0` | **`30.83%`** | `0.60%` | `83.12%` |
| `2c` | **Ground-glass opacity** | 1,654 | **`12.0`** | **`26.90%`** | `0.24%` | `80.77%` |
| `2d` | **Pulmonary nodules / masses** | 2,065 | `11.0` | `9.35%` | `0.44%` | `65.08%` |
| `2e` | **Pleural effusion / thickening** | 275 | `9.0` | `12.00%` | `0.00%` | **`90.18%`** |
| `2f` | **Honeycombing** | 16 | `11.0` | `18.75%` | `0.00%` | `75.00%` |
| `2g` | **Pneumothorax** | 20 | `8.0` | `15.00%` | `0.00%` | **`95.00%`** |
| `2h` | **Other focal** | 66 | `8.5` | `16.67%` | `1.52%` | `60.61%` |

---

## 4. Anatomical Spatial Density & Centroid Distributions (Exp 003)

Resampling GT masks into canonical RAS space ($128 \times 128 \times 128$) establishes normalized spatial probability density maps $P(\mathbf{x}' \in \text{mask} \mid c)$ across Train and Validation splits:

| Category Name | Train Centroid $(R\text{-}L, A\text{-}P, I\text{-}S)$ | Val Centroid $(R\text{-}L, A\text{-}P, I\text{-}S)$ | Spatial Localization Characteristics |
|---|---|---|---|
| **Bronchial wall thickening** | `(0.490, 0.559, 0.541)` | `(0.453, 0.572, 0.478)` | Peribronchial / Hilar concentration |
| **Bronchiectasis** | `(0.488, 0.549, 0.545)` | `(0.435, 0.532, 0.548)` | Bilateral central & lower lobe preference |
| **Emphysema** | `(0.494, 0.556, 0.667)` | `(0.462, 0.554, 0.789)` | **Upper lobe apical dominance** ($Z_{\text{IS}} > 0.65$) |
| **Septal thickening** | `(0.479, 0.578, 0.563)` | `(0.398, 0.572, 0.469)` | Interstitial / Peripherally distributed |
| **Micronodules** | `(0.481, 0.576, 0.537)` | `(0.446, 0.507, 0.580)` | Diffuse bilateral parenchymal spread |
| **Linear opacities** | `(0.524, 0.498, 0.535)` | `(0.546, 0.495, 0.537)` | Subpleural & basal parenchymal bands |
| **Atelectasis / consolidation** | `(0.495, 0.565, 0.491)` | `(0.519, 0.560, 0.416)` | **Basal & dependent lung preference** ($Z_{\text{IS}} < 0.50$) |
| **Ground-glass opacity** | `(0.488, 0.591, 0.519)` | `(0.450, 0.622, 0.442)` | Multifocal peripheral & lower lobe spread |
| **Pulmonary nodules / masses** | `(0.458, 0.546, 0.556)` | `(0.454, 0.551, 0.554)` | **Isotropic parenchymal distribution** (centered ~0.50) |
| **Pleural effusion / thickening** | `(0.463, 0.684, 0.484)` | `(0.457, 0.668, 0.431)` | **Posterior-basal pleural boundary** ($Y_{\text{AP}} > 0.65, Z_{\text{IS}} < 0.48$) |

---

## 5. Hounsfield Unit (HU) Radiodensity Attenuation Profiling (Exp 004)

Sampling physical CT attenuation values inside mask regions versus surrounding healthy parenchyma across 3,192 scans provides empirical evidence for contrast boundaries:

| Code | Category Name | Mask Count | Mean HU | Median HU | P5 HU | P95 HU | Background Mean HU | Contrast Delta ($\Delta\text{HU}$) | Recommended Intensity Window |
|---|---|---|---|---|---|---|---|---|---|
| `1a` | **Bronchial wall thickening** | 239 | -486.3 | -758.0 | -933.0 | 69.0 | -464.3 | -22.0 HU | `[-933.0, 69.0] HU` |
| `1b` | **Bronchiectasis** | 293 | -478.0 | -800.0 | -934.0 | 86.0 | -480.1 | +2.1 HU | `[-934.0, 86.0] HU` |
| `1c` | **Emphysema** | 463 | -308.0 | -159.0 | -992.0 | 250.0 | -305.0 | -2.9 HU | `[-992.0, 250.0] HU` |
| `1d` | **Septal thickening** | 200 | -406.4 | -374.0 | -1001.0 | 121.0 | -384.9 | -21.5 HU | `[-1001.0, 121.0] HU` |
| `1e` | **Micronodules** | 325 | -427.2 | -695.0 | -998.0 | 101.0 | -442.9 | +15.7 HU | `[-998.0, 101.0] HU` |
| `1f` | **Other non-focal** | 154 | -334.3 | -172.0 | -986.0 | 98.0 | -326.4 | -8.0 HU | `[-986.0, 98.0] HU` |
| `2a` | **Linear opacities** | 1,189 | -286.5 | -278.0 | -992.0 | 399.0 | -291.3 | +4.7 HU | `[-992.0, 399.0] HU` |
| `2b` | **Atelectasis / consolidation** | 1,416 | -341.3 | -411.0 | -995.0 | 130.0 | -343.8 | +2.5 HU | `[-995.0, 130.0] HU` |
| `2c` | **Ground-glass opacity** | 1,567 | -375.1 | -428.0 | -995.0 | 138.0 | -370.7 | -4.4 HU | `[-995.0, 138.0] HU` |
| `2d` | **Pulmonary nodules / masses** | 1,875 | -427.1 | -684.0 | -998.0 | 193.0 | -377.9 | -49.2 HU | `[-998.0, 193.0] HU` |
| `2e` | **Pleural effusion / thickening** | 248 | -368.6 | -119.0 | -1007.0 | 136.0 | -349.4 | -19.2 HU | `[-1007.0, 136.0] HU` |
| `2f` | **Honeycombing** | 16 | -421.4 | -467.0 | -905.0 | 83.0 | -401.1 | -20.3 HU | `[-905.0, 83.0] HU` |
| `2g` | **Pneumothorax** | 19 | -306.5 | -49.0 | -962.0 | 147.0 | -250.6 | -55.8 HU | `[-962.0, 147.0] HU` |
| `2h` | **Other focal** | 64 | -157.2 | -115.0 | -915.0 | 198.0 | -140.0 | -17.2 HU | `[-915.0, 198.0] HU` |

---

## 6. Structural Resolution & Positive-Unlabeled Contamination (Exp 005 & 006)

### A. Physical Voxel Spacings
Across 3,192 CT volumes:
* In-plane resolution: $\Delta x = \Delta y = 0.710 \pm 0.117\text{ mm}$ (Range: $0.45\text{ mm}$ to $0.98\text{ mm}$).
* Slice thickness: $\Delta z = 1.053 \pm 0.325\text{ mm}$ (Range: $0.75\text{ mm}$ to $2.50\text{ mm}$).

### B. Positive-Unlabeled (PU) Contamination Estimates (Exp 006)
Comparing partial training frequencies against exhaustive validation frequencies provides an estimate of unannotated true-positive background contamination:

| Pathology Category | Train Annotated Rate | Val Exhaustive Rate | Estimated PU Background Bias |
|---|---|---|---|
| **Pulmonary nodules / masses (`2d`)** | `43.6%` | `59.5%` | **`+15.88%`** (Highest unannotated background risk) |
| **Linear opacities (`2a`)** | `26.8%` | `31.5%` | **`+4.73%`** |
| **Other focal (`2h`)** | `1.8%` | `3.5%` | **`+1.66%`** |

---

## 7. 3D Morphological Topology & Size Thresholds (Exp 008)

Connected-component analysis across **33,408 3D connected components** extracts sphericity indices ($S$) and derives noise-filtering thresholds (`recommended_min_size_voxels`):

| Cat Code | Category Name | Total Blobs | Mean Blobs / Finding | Comp Median Vol ($\text{mm}^3$) | Rec Min Component Size | Mean Sphericity ($S$) | Mean SA/V ($\text{mm}^{-1}$) | Topological Classification |
|---|---|---|---|---|---|---|---|---|
| `1a` | **Bronchial wall thickening** | 1,539 | `6.44` | `90.0` | **`10` voxels** | `0.725` | `0.7619` | Multi-focal / Tubular |
| `1b` | **Bronchiectasis** | 1,007 | `3.44` | `1453.0` | **`10` voxels** | `0.606` | `0.6483` | Branching / Tubular |
| `1c` | **Emphysema** | 2,279 | `4.92` | `578.0` | **`10` voxels** | `0.715` | `0.7097` | Diffuse / Parenchymal |
| `1d` | **Septal thickening** | 726 | `3.63` | `2844.5` | **`10` voxels** | `0.543` | `0.6439` | Interstitial / Planar |
| `1e` | **Micronodules** | 1,210 | `3.72` | `236.0` | **`10` voxels** | `0.750` | `0.7072` | Multi-focal / Compact |
| `1f` | **Other non-focal** | 469 | `3.05` | `2664.0` | **`47` voxels** | `0.618` | `0.6382` | Diffuse |
| `2a` | **Linear opacities** | 3,248 | `2.73` | `1402.0` | **`10` voxels** | `0.614` | `0.7313` | Linear / Band-like |
| `2b` | **Atelectasis / consolidation** | 5,662 | `4.00` | `943.0` | **`10` voxels** | `0.645` | `0.6214` | Parenchymal |
| `2c` | **Ground-glass opacity** | 6,080 | `3.88` | `1942.5` | **`10` voxels** | `0.664` | `0.5969` | Infiltrative |
| `2d` | **Pulmonary nodules / masses** | 3,834 | `2.05` | `192.5` | **`15` voxels** | **`0.942`** | `0.7536` | **Spherical / Compact** |
| `2e` | **Pleural effusion / thickening** | 749 | `3.02` | `1863.0` | **`10` voxels** | `0.571` | `0.4894` | Dependent / Boundary |
| `2f` | **Honeycombing** | 55 | `3.44` | `4990.0` | **`10` voxels** | `0.638` | `0.4609` | Subpleural / Cystic |
| `2g` | **Pneumothorax** | 84 | `4.42` | `42.0` | **`10` voxels** | `0.681` | `0.4989` | Pleural / Avarice |
| `2h` | **Other focal** | 194 | `3.03` | `1245.0` | **`10` voxels** | `0.643` | `0.5439` | Focal |

---

## 8. Patient Hierarchy & Cross-Split Leakage Audit (Exp 009)

3-tier ID decomposition (`patient_id`, `scan_id`, `reconstruction_id`) across 3,078 hierarchical NIfTI volumes:

| Split | Total NIfTI Volumes | Unique Patients | Unique Longitudinal Scans | Unique Reconstruction Series |
|---|---|---|---|---|
| **Train Split** | 2,578 | `2,334` | `2,578` | `2,578` |
| **Validation Split** | 200 | `190` | `200` | `200` |
| **Test Split** | 300 | `281` | `300` | `300` |
| **Total Dataset** | **3,078** | **`2,805`** | **`3,078`** | **`3,078`** |

* **Cross-Split Patient Overlap**:
  * **Train <-> Val Overlap**: `2` patients (IDs: `1841` and `2936`).
  * **Train <-> Test Overlap**: `3` patients (IDs: `39`, `3357`, `3675`).
  * **Val <-> Test Overlap**: `5` patients (IDs: `13119`, `13278`, `13479`, `13492`, `13583`).
* **Longitudinal Multi-Scan Distribution**: 2,583 patients have 1 scan; 212 patients (7.56%) have 2 to 6 longitudinal follow-up CT studies.

---

## 9. 3D CT Image & Pathology Mask Physical Extents (Exp 010)

Profiling physical scan volumes ($V_{\text{CT}}$), 3D bounding box physical extents ($\Delta X, \Delta Y, \Delta Z$), aspect ratios ($\Delta Z / \Delta XY$), and relative occupancy ($V_{\text{mask}} / V_{\text{CT}}$):

* **Global CT Physical Scan Volume ($V_{\text{CT}}$)**: Median **`101,842.9 cm³`** (5th percentile: `53,359.4 cm³`, 95th percentile: `137,101.3 cm³`).
* **Physical Extents Matrix**:

| Cat Code | Category Name | Findings | Median Mask Vol ($\text{mm}^3$) | Median BBox $\Delta X, \Delta Y, \Delta Z$ ($\text{mm}$) | Aspect Ratio ($\Delta Z / \Delta XY$) | Median Relative Occupancy ($V_{\text{mask}} / V_{\text{CT}}$) |
|---|---|---|---|---|---|---|
| `1a` | **Bronchial wall thickening** | 239 | `28,284.0` | `185.0 x 96.0 x 32.0` | `0.18` | `0.0309%` |
| `1b` | **Bronchiectasis** | 293 | `22,160.0` | `177.0 x 101.0 x 34.0` | `0.22` | `0.0243%` |
| `1c` | **Emphysema** | 463 | `19,341.0` | `205.0 x 101.0 x 38.0` | `0.22` | `0.0198%` |
| `1d` | **Septal thickening** | 200 | `30,996.5` | `245.0 x 101.5 x 37.0` | `0.16` | `0.0380%` |
| `1e` | **Micronodules** | 325 | `2,966.0` | `131.0 x 89.0 x 40.0` | `0.28` | `0.0033%` |
| `1f` | **Other non-focal** | 154 | `20,331.0` | `232.0 x 96.0 x 41.5` | `0.27` | `0.0225%` |
| `2a` | **Linear opacities** | 1,189 | `7,193.0` | `95.0 x 63.0 x 20.0` | `0.21` | `0.0078%` |
| `2b` | **Atelectasis / consolidation** | 1,416 | `22,973.0` | `108.5 x 80.5 x 33.0` | `0.27` | `0.0256%` |
| `2c` | **Ground-glass opacity** | 1,567 | `21,325.0` | `158.0 x 92.0 x 42.0` | `0.28` | `0.0237%` |
| `2d` | **Pulmonary nodules / masses** | 1,875 | **`423.0`** | **`31.0 x 27.0 x 12.0`** | **`0.36`** | **`0.0005%`** |
| `2e` | **Pleural effusion / thickening** | 248 | `80,047.0` | `152.5 x 87.0 x 49.0` | `0.28` | `0.0945%` |
| `2f` | **Honeycombing** | 16 | `47,252.0` | `240.5 x 130.0 x 32.5` | `0.22` | `0.0368%` |
| `2g` | **Pneumothorax** | 19 | **`144,552.0`** | `167.0 x 110.0 x 31.0` | `0.40` | **`0.1135%`** |
| `2h` | **Other focal** | 64 | `17,393.5` | `120.0 x 81.5 x 35.0` | `0.28` | `0.0190%` |

---

## 10. Calibrated Actionable Directives for Phase 2 & Phase 3

Based strictly on empirical findings across Phase 1 (`exp_001`–`exp_011`), the following working hypotheses and modeling strategies are established:

1. **Instance F1 Noise Pruning**: Apply `recommended_min_size_voxels` (`15` voxels for Nodules `2d`, `47` voxels for Other Non-Focal `1f`, `10` voxels default) in post-processing (`scripts/evaluate.py` and `scripts/voxtell/voxtell_inference.py`) to eliminate spurious tiny false-positive connected components without recall degradation.
2. **Dynamic Range Intensity Windowing**: Enforce broad CT intensity windowing (`[-1000, +400] HU`) during pre-processing to preserve dynamic range across hyper-dense and hypo-dense pathologies.
3. **Text Fusion Resilience**: Because 72.53% of prompts contain spatial locators and 18.77% are compound multi-finding descriptions, avoid aggressive regex text stripping. Multi-modal fine-tuning in Phase 3 will adapt text embeddings to remain resilient to clinical modifiers while preserving location directives.
4. **Positive-Unlabeled (PU) SPOCO Fine-Tuning**: Incorporate class-weighted PU-SPOCO loss with float32 upcasting and L2 gradient clipping to mitigate background suppression bias on unannotated training findings (particularly for Pulmonary Nodules `2d`, which exhibit $+15.88\%$ estimated background contamination).
5. **Sliding Window Sensitivity & Logit Profiling (Phase 2)**: Benchmark zero-shot VoxTell v1.1 error breakdown across all 14 categories and optimize per-category logit binarization thresholds and tile step size (`tile_step_size` 0.25 vs 0.5).

---
*Report generated and archived in `logs/phase_1_data_profiling/phase_1_technical_report.md`.*
