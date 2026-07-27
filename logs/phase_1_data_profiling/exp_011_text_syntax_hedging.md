# Experiment Log 011: [Phase 1] Structural & Syntax Clinical Text Profiling

**Status**: Completed  
**Date**: July 2026  
**Primary Output**: `data/phase_1/analysis_part_c/clinical_text_syntax_stats.json`  

---

## 1. Executive Summary & Objective

Experiment 011 profiles radiology report text prompts across all 7,687 finding queries in ReXGroundingCT. The analysis quantifies word count length, multi-finding compound clause prevalence, diagnostic hedging/uncertainty language, and anatomical spatial preposition alignment.

## 2. Global Text Prompt Syntax Summary

* **Total Finding Prompts**: `8650` queries.
* **Prompt Length (Words)**: Median `10.0 words` (Mean: `10.8 words`, Range: 1–38 words).
* **Multi-Finding Compound Prompts**: `1624` prompts (`18.77%`).
* **Diagnostic Hedging / Uncertainty**: `33` prompts (`0.38%`).
* **Anatomical Spatial Prepositions**: `6274` prompts (`72.53%`).

---

## 3. Category-Level Clinical Text Profiling Matrix

| Cat Code | Category Name | Findings | Median Word Count | Compound Prompts (%) | Hedging Language (%) | Spatial Prepositions (%) |
|---|---|---|---|---|---|---|
| `1a` | **Bronchial wall thickening** | 245 | `7.0` | `10.20%` | `0.00%` | `86.94%` |
| `1b` | **Bronchiectasis** | 304 | `9.0` | `17.43%` | `0.00%` | `53.29%` |
| `1c` | **Emphysema** | 490 | `6.0` | `5.71%` | `0.00%` | `35.31%` |
| `1d` | **Septal thickening** | 209 | `9.0` | `20.57%` | `0.48%` | `61.24%` |
| `1e` | **Micronodules** | 341 | `10.0` | `17.30%` | `0.00%` | `61.58%` |
| `1f` | **Other non-focal** | 158 | `7.0` | `10.76%` | `0.63%` | `41.14%` |
| `2a` | **Linear opacities** | 1302 | `10.0` | `18.97%` | `0.61%` | `82.41%` |
| `2b` | **Atelectasis / consolidation** | 1505 | `11.0` | `30.83%` | `0.60%` | `83.12%` |
| `2c` | **Ground-glass opacity** | 1654 | `12.0` | `26.90%` | `0.24%` | `80.77%` |
| `2d` | **Pulmonary nodules / masses** | 2065 | `11.0` | `9.35%` | `0.44%` | `65.08%` |
| `2e` | **Pleural effusion / thickening** | 275 | `9.0` | `12.00%` | `0.00%` | `90.18%` |
| `2f` | **Honeycombing** | 16 | `11.0` | `18.75%` | `0.00%` | `75.00%` |
| `2g` | **Pneumothorax** | 20 | `8.0` | `15.00%` | `0.00%` | `95.00%` |
| `2h` | **Other focal** | 66 | `8.5` | `16.67%` | `1.52%` | `60.61%` |
