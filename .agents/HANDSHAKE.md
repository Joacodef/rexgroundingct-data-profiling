# Handshake: ReXGroundingCT Data Profiling Workspace

> [!NOTE]
> **DOCUMENT ROLE CONTRACT: TACTICAL SESSION BRIDGE**
> This document serves as the tactical session handoff bridge for **rexgroundingct-data-profiling** (designed to onboard any AI assistant, e.g. Antigravity or Claude, in a new chat).
> It tracks active operational focus, experiment mappings, and immediate audit steps prior to re-executing scripts or compiling reports.
> For long-term progress matrix, consult `.agents/STATUS.md`. For model fine-tuning, consult sibling workspace `rexgroundingct-model-training`.

---

## 1. Operational Scope & Working Context

The active focus in this workspace is **Systematic Audit & Consolidation of the 5-Experiment Profiling Suite**:

* **Goal**: Conduct a rigorous, code-and-output audit of all 5 profiling experiments (`exp_001` through `exp_005`), consolidate output priors (`phase_1_priors_bundle.json`), and prepare the final Overleaf group technical report update.
* **Architecture**: Standalone decoupled workspace for data analysis. Resolves shared dataset paths (`../data/dataset.json` and `../data/raw/`) dynamically via `scripts/config.py`.
* **5 Core Experiments Scope**:
  1. `exp_001`: Dataset Disparity (14-category Train vs Val mask density), $14 \times 14$ Scan-Level Multi-Finding Co-Occurrence Matrix ($P(c_j \mid c_i)$), Patient Hierarchy & Cross-Split Leakage Audit.
  2. `exp_002`: Free-Text NLP Syntax Shift, Subword BPE Tokenization Dynamics, Truncation Rates (77 & 128 tokens), & Spatial Directives.
  3. `exp_003`: 3D RAS Spatial Coordinate Centroids & 4-Panel Density Prior Figures ($128 \times 128 \times 128$).
  4. `exp_004`: Hounsfield Unit (HU) Radiodensity Attenuation, Contrast Deltas ($\Delta \text{HU}$) & Category Windowing.
  5. `exp_005`: 3D Connected-Component Topology, Sphericity, Physical Bounding Box Extents ($\Delta X, \Delta Y, \Delta Z$ in mm) & Noise Pruning Size Thresholds.

---

## 2. Directory & Artifact Map

* `scripts/`: Execution scripts (`exp_001_...py` through `exp_005_...py`), path manager (`config.py`), local evaluator (`evaluate.py`).
* `logs/`: Individual experiment markdown reports (`exp_001_...md` to `exp_005_...md`) and LaTeX technical report source (`phase_1_report_overleaf/main.tex`).
* `../data/phase_1/`: Generated JSON summaries and figures (`analysis_experiment_001` to `005`).
* `.agents/`: Agent operating rules (`AGENTS.md`), macro status matrix (`STATUS.md`), and shared roadmap (`shared/MASTER_PLAN.md`).

---

## 3. Environment & Execution Setup

Virtual Environment:
```bash
source .venv/bin/activate  # or call ./.venv/bin/python
```

Run test check:
```bash
./.venv/bin/python -c "import scripts.config as cfg; print('DATA_DIR:', cfg.DATA_DIR)"
```

---

## 4. Tactical Agenda for New Session (Systematic 5-Experiment Audit)

The new AI session will execute a systematic, step-by-step audit of all 5 profiling experiments before final technical report compilation:

1. **Audit Exp 001 (Disparity, Co-Occurrence & Patient Leakage)** — **[COMPLETED & AUDITED]**:
   - Reviewed code logic in `scripts/exp_001_dataset_disparity_leakage.py` & findings in `logs/exp_001_dataset_disparity_leakage.md`.
   - Verified 14-category density disparity ($1.91\times$ overall, $3.20\times$ ground-glass peak), $14 \times 14$ co-occurrence matrix ($P(c_j \mid c_i)$), and patient ID leakage list (2 Train-Val, 4 Train-Test: `['302', '3357', '3675', '39']`, 5 Val-Test overlaps). Re-executed script, validated output JSON/heatmap PNG, and cleaned up legacy `heatmaps_raw.pkl` files in `../data/phase_1/`.

2. **Audit Exp 002 (NLP Syntax & Tokenization Shift)** — **[COMPLETED & AUDITED]**:
   - Reviewed code logic in `scripts/exp_002_nlp_prompt_syntax.py` & findings in `logs/exp_002_nlp_prompt_syntax.md`.
   - Verified free-text prompt syntax (8,650 total prompts), validation syntax shift (Cases 1–50 vs 51–200), subword BPE tokenization expansion factor (`1.346x`), 0% truncation rates at 77/128 tokens, spatial prepositions (`64.39%`), and aligned script entrypoint path references. Re-executed script and validated output JSON schema.

3. **Audit Exp 003 (3D RAS Spatial Density Priors)** — **[COMPLETED & AUDITED]**:
   - Reviewed code logic in `scripts/exp_003_spatial_density_priors.py` & findings in `logs/exp_003_spatial_density_priors.md`.
   - Verified 3D RAS spatial centroids $[RL, AP, IS] \in [0.0, 1.0]^3$, cosine similarities $S_{cos}$, centroid shifts $\Delta d$, 4-tier spatial prior taxonomy (Apical Dominant, Basal/Dependent, Hilar/Peribronchial, Isotropic/Parenchymal), 4-panel population prior figure (`exp003_population_spatial_priors_4panel.png`), and aligned script entrypoint path references. Initiated script re-execution.

4. **Audit Exp 004 (HU Radiodensity & Intensity Windowing)** — **[IMMEDIATE NEXT STEP FOR NEW SESSION]**:
   - Re-execute and verify `scripts/exp_004_hu_radiodensity.py` using `.venv/bin/python`.
   - Reconcile findings with `logs/exp_004_hu_radiodensity.md` and output summary `../data/phase_1/analysis_experiment_004/exp004_hu_radiodensity_summary.json`.
   - Verify HU contrast deltas ($\Delta \text{HU}$), tissue boundary dilation margins, and category intensity window bounds (`[min_HU, max_HU]`).
   - Fix script entrypoint header reference in `logs/exp_004_hu_radiodensity.md` to point to `scripts/exp_004_hu_radiodensity.py`.

5. **Audit Exp 005 (Topology & Morphological Noise Pruning)** — **[IMMEDIATE NEXT STEP FOR NEW SESSION]**:
   - Re-execute and verify `scripts/exp_005_morphology_noise_pruning.py` using `.venv/bin/python`.
   - Reconcile findings with `logs/exp_005_morphology_noise_pruning.md` and output summary `../data/phase_1/analysis_experiment_005/exp005_morphology_noise_pruning_summary.json`.
   - Verify 3D connected-component size distributions (33,058 blobs), sphericity metrics ($S$), physical bounding box extents ($\Delta X, \Delta Y, \Delta Z$ in mm), aspect ratios, and noise pruning thresholds (`recommended_min_size_voxels`).
   - Align script entrypoint path references in `logs/exp_005_morphology_noise_pruning.md` to `scripts/exp_005_morphology_noise_pruning.py`.

6. **Priors Bundle Export & Technical Report Compilation**:
   - Update exported priors bundle (`../data/phase_1/phase_1_priors_bundle.json`).
   - Finalize and compile Overleaf group technical report (`logs/phase_1_report_overleaf/main.tex`).
