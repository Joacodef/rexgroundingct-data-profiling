# Experiment Log 009: [Phase 1] Patient, Longitudinal Scan & Reconstruction Series Hierarchy Analysis

**Status**: Completed  
**Date**: July 2026  
**Primary Output**: `data/phase_1/analysis_part_a/patient_hierarchy_summary.json`  

---

## 1. Executive Summary

Experiment 009 profiles the 3-tier hierarchy across all 3,192 scans and identifies cross-split patient overlaps.

## 2. Dataset Hierarchy Breakdown

| Split | Total NIfTI Volumes | Unique Patients | Unique Longitudinal Scans |
|---|---|---|---|
| **Train** | 2578 | `2334` | `2578` |
| **Val** | 200 | `190` | `200` |
| **Test** | 300 | `281` | `300` |

## 3. Data Leakage Audit Findings

* Train <-> Val Overlap: `2` patients (['1841', '2936'])
* Train <-> Test Overlap: `3` patients (['3357', '3675', '39'])
* Val <-> Test Overlap: `5` patients (['13119', '13278', '13479', '13492', '13583'])
