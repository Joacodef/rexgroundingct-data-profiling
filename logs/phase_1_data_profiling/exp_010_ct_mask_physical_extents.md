# Experiment Log 010: [Phase 1] 3D CT Image & Pathology Mask Physical Extents Profiling

**Status**: Completed  
**Date**: July 2026  
**Primary Output**: `data/phase_1/analysis_part_b/ct_mask_physical_stats.json`  

---

## 1. Executive Summary & Objective

Experiment 010 profiles physical CT voxel spacings (dx, dy, dz), physical scan volumes (V_CT), 3D bounding box physical extents (dX, dY, dZ), aspect ratios, and relative volume occupancy (V_mask / V_CT) across the 14 official categories.

## 2. Global CT Image & Physical Resolution Summary

* **Profiled CT Volumes**: `3192` volumes.
* **In-Plane Voxel Spacing (dx, dy)**: Median `1.000 mm` x `1.000 mm`.
* **Slice Thickness Spacing (dz)**: Median `1.000 mm` (Mean: `1.000 mm`).
* **Physical Scan Volume (V_CT)**: Median `101842.9 cm³` (5th percentile: `53359.4 cm³`, 95th percentile: `137101.3 cm³`).

---

## 3. Pathology 3D Physical Extents & Occupancy Matrix

| Cat Code | Category Name | Findings | Median Mask Vol (mm³) | Median BBox dX, dY, dZ (mm) | Aspect Ratio (dZ / dXY) | Median Relative Occupancy (V_mask / V_CT) |
|---|---|---|---|---|---|---|
| `1a` | **Bronchial wall thickening** | 239 | `28284.0` | `185.0 x 96.0 x 32.0` | `0.18` | `0.0309%` |
| `1b` | **Bronchiectasis** | 293 | `22160.0` | `177.0 x 101.0 x 34.0` | `0.22` | `0.0243%` |
| `1c` | **Emphysema** | 463 | `19341.0` | `205.0 x 101.0 x 38.0` | `0.22` | `0.0198%` |
| `1d` | **Septal thickening** | 200 | `30996.5` | `245.0 x 101.5 x 37.0` | `0.16` | `0.0380%` |
| `1e` | **Micronodules** | 325 | `2966.0` | `131.0 x 89.0 x 40.0` | `0.28` | `0.0033%` |
| `1f` | **Other non-focal** | 154 | `20331.0` | `232.0 x 96.0 x 41.5` | `0.27` | `0.0225%` |
| `2a` | **Linear opacities** | 1189 | `7193.0` | `95.0 x 63.0 x 20.0` | `0.21` | `0.0078%` |
| `2b` | **Atelectasis / consolidation** | 1416 | `22973.0` | `108.5 x 80.5 x 33.0` | `0.27` | `0.0256%` |
| `2c` | **Ground-glass opacity** | 1567 | `21325.0` | `158.0 x 92.0 x 42.0` | `0.28` | `0.0237%` |
| `2d` | **Pulmonary nodules / masses** | 1875 | `423.0` | `31.0 x 27.0 x 12.0` | `0.36` | `0.0005%` |
| `2e` | **Pleural effusion / thickening** | 248 | `80047.0` | `152.5 x 87.0 x 49.0` | `0.28` | `0.0945%` |
| `2f` | **Honeycombing** | 16 | `47252.0` | `240.5 x 130.0 x 32.5` | `0.22` | `0.0368%` |
| `2g` | **Pneumothorax** | 19 | `144552.0` | `167.0 x 110.0 x 31.0` | `0.40` | `0.1135%` |
| `2h` | **Other focal** | 64 | `17393.5` | `120.0 x 81.5 x 35.0` | `0.28` | `0.0190%` |
