# Handshake: ReXGroundingCT Data Profiling Workspace

> [!NOTE]
> **DOCUMENT ROLE CONTRACT: TACTICAL SESSION BRIDGE**
> This document serves as the tactical session handoff bridge for **rexgroundingct-data-profiling** (designed to onboard any AI assistant, e.g. Antigravity or Claude, in a new chat).
> It tracks active operational focus, experiment mappings, and immediate handoff steps for LaTeX report compilation.
> For long-term progress matrix, consult `.agents/STATUS.md`. For model fine-tuning, consult sibling workspace `rexgroundingct-model-training`.

---

## 1. Operational Scope & Working Context

The active focus in this workspace is **Iterative Revision & Polish of Phase 1 Overleaf Group Technical Report**:

* **Current Baseline State**: Initial quantitative synchronization of all 5 Phase 1 data profiling experiments (`exp_001` through `exp_005`) into [logs/phase_1_report_overleaf/main.tex](file://logs/phase_1_report_overleaf/main.tex) and [logs/phase_1_report_overleaf/fig/](file://logs/phase_1_report_overleaf/fig/) is **100% completed**.
* **Multi-Session Revision Protocol**: The report will undergo several iterative revision rounds across new AI chat sessions. In each iteration, the user may provide feedback, structural suggestions, or external review notes (e.g. from Claude or peer reviewers).
* **Primary Objective**: Incrementally refine, expand, re-format, and polish `main.tex` based on incoming feedback while maintaining strict fidelity with the ground-truth empirical data in `logs/` and `../data/phase_1/`.

---

## 2. Completed 5-Experiment Audit Baseline

1. **Exp 001 (Disparity, Co-Occurrence & Leakage)** — **[AUDITED & RECONCILED]**:
   - [logs/exp_001_dataset_disparity_leakage.md](file://logs/exp_001_dataset_disparity_leakage.md) & [../data/phase_1/analysis_experiment_001/exp001_disparity_leakage_summary.json](file://../data/phase_1/analysis_experiment_001/exp001_disparity_leakage_summary.json).
   - 3,063 unique patients (2,603 Train / 190 Val / 281 Test); 1.91x overall Train vs Val disparity; 4 Train-Test leakage patient IDs (`['302', '3357', '3675', '39']`); 5 Val-Test leakage patient IDs; $14 \times 14$ co-occurrence matrix ($P(c_j \mid c_i)$).
2. **Exp 002 (NLP Syntax & Tokenization Shift)** — **[AUDITED & RECONCILED]**:
   - [logs/exp_002_nlp_prompt_syntax.md](file://logs/exp_002_nlp_prompt_syntax.md) & [../data/phase_1/analysis_experiment_002/exp002_nlp_prompt_syntax_summary.json](file://../data/phase_1/analysis_experiment_002/exp002_nlp_prompt_syntax_summary.json).
   - 8,650 prompts; subword BPE expansion factor `1.346x`; 0.0% truncation at 77/128 tokens; 64.39% spatial preposition locators.
3. **Exp 003 (3D RAS Spatial Density Priors)** — **[AUDITED & RECONCILED]**:
   - [logs/exp_003_spatial_density_priors.md](file://logs/exp_003_spatial_density_priors.md) & [../data/phase_1/analysis_experiment_003/exp003_spatial_density_priors_summary.json](file://../data/phase_1/analysis_experiment_003/exp003_spatial_density_priors_summary.json).
   - 3D RAS spatial centroids $[RL, AP, IS] \in [0.0, 1.0]^3$; cosine similarity $S_{cos}$ & shift $\Delta d$; 4-tier spatial prior taxonomy (Apical, Basal, Hilar, Isotropic).
4. **Exp 004 (HU Radiodensity & Intensity Windowing)** — **[AUDITED & RECONCILED]**:
   - [logs/exp_004_hu_radiodensity.md](file://logs/exp_004_hu_radiodensity.md) & [../data/phase_1/analysis_experiment_004/exp004_hu_radiodensity_summary.json](file://../data/phase_1/analysis_experiment_004/exp004_hu_radiodensity_summary.json).
   - HU spectrum (Bronchial Wall Thickening `-486.35 HU` to Emphysema `-307.95 HU`); contrast deltas $\Delta \text{HU}$; category window bounds `[min_HU, max_HU]`.
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
* `.agents/`: Operating constraints ([AGENTS.md](file://.agents/AGENTS.md)), status matrix ([STATUS.md](file://.agents/STATUS.md)), and tactical handoff ([HANDSHAKE.md](file://.agents/HANDSHAKE.md)).

---

## 4. Tactical Agenda for Iterative Report Revisions (New AI Sessions)

Any incoming AI assistant starting a new session to revise the report MUST follow this protocol:

1. **Read Active Context & Feedback**:
   - Consult `.agents/AGENTS.md`, `.agents/STATUS.md`, and `.agents/HANDSHAKE.md`.
   - Read the user's prompt containing feedback or revision requests (e.g., external edits from Claude or peer reviewers).

2. **Inspect Current LaTeX Source**:
   - Read [logs/phase_1_report_overleaf/main.tex](file://logs/phase_1_report_overleaf/main.tex).
   - Verify environment balance, table formatting, figure inclusions, and citations.

3. **Apply Targeted Report Edits**:
   - Modify [logs/phase_1_report_overleaf/main.tex](file://logs/phase_1_report_overleaf/main.tex) to integrate requested structural, stylistic, or content refinements.
   - Maintain strict factual alignment with the ground-truth experiment logs (`logs/exp_001_...` to `exp_005_...`).

4. **Update Handshake State**:
   - Document key changes made during the session in `.agents/HANDSHAKE.md` to bridge state to subsequent revision rounds.

---

## 5. Recent Revisions Log

* **July 27, 2026**: Resolved table width page overflow across all five tables in [logs/phase_1_report_overleaf/main.tex](file://logs/phase_1_report_overleaf/main.tex):
  * Added `adjustbox` and `makecell` packages to preamble.
  * Wrapped all table environments in `\begin{adjustbox}{max width=\linewidth}`.
  * Multi-line column headers using `\makecell` and tightened column separation (`\tabcolsep`).



