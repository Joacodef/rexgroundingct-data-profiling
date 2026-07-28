# Handshake: ReXGroundingCT Data Profiling Workspace

> [!NOTE]
> **DOCUMENT ROLE CONTRACT: TACTICAL SESSION BRIDGE**
> This document serves as the tactical session handoff bridge for **rexgroundingct-data-profiling** (designed to onboard any AI assistant, e.g. Antigravity or Claude, in a new chat).
> It tracks active operational focus, experiment mappings, and immediate handoff steps for LaTeX report compilation.
> For long-term progress matrix, consult `.agents/STATUS.md`. For model fine-tuning, consult sibling workspace `rexgroundingct-model-training`.

---

## 1. Operational Scope & Working Context

The active focus in this workspace is **Phase 1 Overleaf Group Technical Report Compilation & Priors Export**:

* **Current Baseline State**: All 5 Phase 1 data profiling experiments (`exp_001` through `exp_005`) are **100% completed, audited, and reconciled** with their raw JSON summaries in `../data/phase_1/` and markdown logs in `logs/`.
* **Primary Handoff Goal**: Update and compile the group LaTeX technical report in [logs/phase_1_report_overleaf/main.tex](file://logs/phase_1_report_overleaf/main.tex), incorporating all 5-experiment quantitative tables, figures, and empirical priors export.
* **Architecture**: Standalone decoupled workspace for data analysis. LaTeX manuscript resides in `logs/phase_1_report_overleaf/`.

---

## 2. Completed 5-Experiment Audit Baseline

1. **Exp 001 (Disparity, Co-Occurrence & Leakage)** — **[AUDITED & RECONCILED]**:
   - [logs/exp_001_dataset_disparity_leakage.md](file://logs/exp_001_dataset_disparity_leakage.md) & [../data/phase_1/analysis_experiment_001/exp001_disparity_leakage_summary.json](file://../data/phase_1/analysis_experiment_001/exp001_disparity_leakage_summary.json).
   - 3,063 unique patients (2,603 Train / 190 Val / 281 Test); 1.91x overall Train vs Val disparity; 4 Train-Test leakage patient IDs (`['302', '3357', '3675', '39']`); $14 \times 14$ co-occurrence matrix ($P(c_j \mid c_i)$).
2. **Exp 002 (NLP Syntax & Tokenization Shift)** — **[AUDITED & RECONCILED]**:
   - [logs/exp_002_nlp_prompt_syntax.md](file://logs/exp_002_nlp_prompt_syntax.md) & [../data/phase_1/analysis_experiment_002/exp002_nlp_prompt_syntax_summary.json](file://../data/phase_1/analysis_experiment_002/exp002_nlp_prompt_syntax_summary.json).
   - 8,650 prompts; subword BPE expansion factor `1.346x`; 0.0% truncation at 77/128 tokens; 64.39% spatial preposition locators.
3. **Exp 003 (3D RAS Spatial Density Priors)** — **[AUDITED & RECONCILED]**:
   - [logs/exp_003_spatial_density_priors.md](file://logs/exp_003_spatial_density_priors.md) & [../data/phase_1/analysis_experiment_003/exp003_spatial_density_priors_summary.json](file://../data/phase_1/analysis_experiment_003/exp003_spatial_density_priors_summary.json).
   - 3D RAS spatial centroids $[RL, AP, IS] \in [0.0, 1.0]^3$; cosine similarity $S_{cos}$ & shift $\Delta d$; 4-tier spatial prior taxonomy (Apical, Basal, Hilar, Isotropic).
4. **Exp 004 (HU Radiodensity & Intensity Windowing)** — **[AUDITED & RECONCILED]**:
   - [logs/exp_004_hu_radiodensity.md](file://logs/exp_004_hu_radiodensity.md) & [../data/phase_1/analysis_experiment_004/exp004_hu_radiodensity_summary.json](file://../data/phase_1/analysis_experiment_004/exp004_hu_radiodensity_summary.json).
   - HU spectrum (Emphysema `-307.95 HU` to Bronchial Wall Thickening `-486.35 HU`); contrast deltas $\Delta \text{HU}$; category window bounds `[min_HU, max_HU]`.
5. **Exp 005 (Topology & Morphological Noise Pruning)** — **[AUDITED & RECONCILED]**:
   - [logs/exp_005_morphology_noise_pruning.md](file://logs/exp_005_morphology_noise_pruning.md) & [../data/phase_1/analysis_experiment_005/exp005_morphology_noise_pruning_summary.json](file://../data/phase_1/analysis_experiment_005/exp005_morphology_noise_pruning_summary.json).
   - 33,058 blobs; sphericity index $S$ ($S=0.9416$ for Nodules vs $S=0.5434$ for Septal Thickening); physical bounding box extents ($\Delta X, \Delta Y, \Delta Z$ in mm); empirical noise pruning thresholds (`recommended_min_size_voxels`).

---

## 3. Directory & Artifact Map for Technical Report

* `logs/phase_1_report_overleaf/`: Main Overleaf LaTeX manuscript source ([main.tex](file://logs/phase_1_report_overleaf/main.tex)) and figure directory (`fig/`).
* `../data/phase_1/`:
  * `phase_1_priors_bundle.json`: Consolidated empirical priors export for Phase 2/3 downstream pipelines.
  * `analysis_experiment_001/` to `005/`: Individual raw JSON summaries and high-resolution figures.
* `logs/`: Reconciled markdown logs ([exp_001](file://logs/exp_001_dataset_disparity_leakage.md) to [exp_005](file://logs/exp_005_morphology_noise_pruning.md)).
* `.agents/`: Operating constraints ([AGENTS.md](file://.agents/AGENTS.md)), status matrix ([STATUS.md](file://.agents/STATUS.md)), and master plan ([shared/MASTER_PLAN.md](file://.agents/shared/MASTER_PLAN.md)).

---

## 4. Tactical Agenda for New Session (Overleaf Technical Report Compilation)

The new AI session will execute the following steps to finalize the Overleaf group technical report:

1. **Priors Bundle Export**:
   - Verify/update `../data/phase_1/phase_1_priors_bundle.json` incorporating all category disparity ratios, $14 \times 14$ co-occurrence probabilities, spatial centroids, HU windowing bounds, and physical 3D extents.

2. **Inspect Overleaf LaTeX Source**:
   - Read [logs/phase_1_report_overleaf/main.tex](file://logs/phase_1_report_overleaf/main.tex).
   - Verify document class, preamble packages, section structure, table schemas, figure environments, and references.

3. **Integrate 5-Experiment Findings into LaTeX Sections**:
   - Update text, mathematical formulations, and LaTeX tables across all sections to reflect the exact reconciled numbers from `exp_001` through `exp_005`.
   - Ensure all figure paths in `main.tex` properly reference graphics from `fig/` or `../data/phase_1/`.

4. **Compile & Validate LaTeX Manuscript**:
   - Compile [logs/phase_1_report_overleaf/main.tex](file://logs/phase_1_report_overleaf/main.tex) using `pdflatex` or `latexmk`.
   - Inspect output log for any compilation warnings, missing citations, broken reference keys, or layout errors.


