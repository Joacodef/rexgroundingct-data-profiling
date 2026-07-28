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

* **July 27, 2026**: Resolved table width page overflow across all five tables in [logs/phase_1_report_overleaf/main.tex](file://logs/phase_1_report_overleaf/main.tex).
* **July 28, 2026**: Comprehensive side-by-side audit resolution in [logs/phase_1_report_overleaf/main.tex](file://logs/phase_1_report_overleaf/main.tex):
  * Reconciled headline 3D connected component total to **27,138** across Abstract, Section 2, and Section 7.
  * Corrected Table 4 Row `2h` (*Other focal*) HU window bound to `[-915.0, +201.0]`.
  * Clarified Tier 1 physical scans (3,078) vs Tier 2 `dataset.json` records (3,192), exhaustive validation scope, and test mask withholding.
  * Corrected Honeycombing (`2f`) co-occurrence citation to Atelectasis (`2b`, $P=0.467$) and Pulmonary nodules (`2d`, $P=0.467$).
  * Formulated exact 3D grid Frobenius inner product equation for $S_{\text{cos}}$ matching `exp_003_spatial_density_priors.py`, softened spatial stability claims, and defined spatial prior taxonomy rules.
  * Added `P5 Vol (mm³)` column to Table 5 (`47.6 mm³` for `1f`, `15.0 mm³` for `2d`), sample counts ($N_{\text{masks}}$) to Table 4, and exact 3-decimal BPE token dynamics (`1.347x` / `+34.7%`) to Section 4.
  * Added in-text `\cite{hamamci2024ctrate}` citation in Section 1.1, replaced Markdown `---` lines with `\bigskip`, formatted itemize/enumerate lists, and added `\begin{thebibliography}` section with citations.
* **July 28, 2026**: Peer-review typesetting & technical clarity refinement in [logs/phase_1_report_overleaf/main.tex](file://logs/phase_1_report_overleaf/main.tex):
  * **Math & Units**: Re-rendered coordinate axes `$(\text{RL}, \text{AP}, \text{IS})$` and operators (`\max`, `\text{SA}/\text{V}`) with explicit text mode; converted tall inline fractions (`7,687 / 2,992`) to slash notation; added `siunitx` package with non-breaking spaces `~` for units (`\text{HU}`, `\text{mm}^3`).
  * **Layout & Tables**: Replaced rigid `adjustbox` table scaling with `tabularx` and uniform font size across all 5 tables; applied explicit `>{\raggedright\arraybackslash}X` auto-wrapping columns to resolve column overlap in Table 5 (`Category Name` vs `Blobs`); tightened padding (`\tabcolsep{2.2pt}`) to guarantee zero page margin overflow; replaced `[H]` float specifiers with flexible `[htbp]`; removed hardcoded `\bigskip` overrides.
  * **Code Listing**: Added explicit `json` language definition (`\lstdefinelanguage{json}{...}`) to preamble.
  * **Authentic Bibliography & Technical Clarity**: Updated bibliography in `main.tex` with exact user-provided BibTeX entries for **ReXGroundingCT** (*Baharoon et al., NEJM AI 2026, 3(7):AIdbp2501220*), **VoxTell** (*Rokuss et al., IEEE/CVF CVPR 2026, pp. 37538--37557*), **CT-RATE / Generalist Models** (*Hamamci et al., Nature Biomedical Engineering 2026*), and **SPOCO** (*Wolny et al., arXiv:2103.14572*); explicitly defined MPR and PU acronyms; added zero-count validation methodology note for Honeycombing (`2f`); expanded Table 1 footnote clarifying test split placeholder instance metadata ($1.000 \pm 0.000$).
  * **Experiment 001 Figure Refinement**: Unified validation cases into a single "Validation" split, integrated the Test set distribution (300 scans, 582 findings), converted category frequency Y-axis from raw count to split proportion (%), and updated findings per scan distribution figure to include the Test split.





