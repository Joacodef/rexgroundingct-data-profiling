# ReXGroundingCT Challenge 2026 — Data Profiling & Analysis Workspace

Dedicated research workspace for **Phase 1 Data Profiling & Spatial-Text Analysis** for the **ReXGrounding Challenge @ MICCAI 2026** (3D radiological finding grounding in thoracic CT scans from free-text descriptions).

> [!IMPORTANT]
> **Repository Scope & Governance**:
> This repository is dedicated exclusively to **Data Profiling, Spatial Density Prior Mapping, HU Radiodensity Analysis, NLP Syntax Shift Profiling, 3D Component Topology, Positive-Unlabeled Overlap Analysis, and Paper Manuscript Generation**.
> Model fine-tuning pipelines consume the empirical priors exported in `data/phase_1/phase_1_priors_bundle.json`.

---

## 📂 Project Structure

```text
rexgroundingct-data-profiling/
├── .agents/                    # Agentic rules, host setup docs, and governance
│   ├── shared/                 # Server-agnostic master plan and paper digests
│   ├── AGENTS.md               # Repository operating rules & governance
│   ├── STATUS.md               # Local active macro progress matrix
│   ├── HANDSHAKE.md            # Tactical session bridge & transition handoff
│   └── server_documentation.txt# Host server hardware setup & guides
├── logs/                       # Data profiling experiment logs & paper manuscript
│   ├── exp_001_dataset_disparity_leakage.md
│   ├── exp_002_nlp_prompt_syntax.md
│   ├── exp_003_spatial_density_priors.md
│   ├── exp_004_hu_radiodensity.md
│   ├── exp_005_morphology_noise_pruning.md
│   ├── phase_1_report_overleaf/ # Consolidated LaTeX paper manuscript
│   └── phase_1_report_overleaf.zip
├── scratch/                    # One-off exploratory analysis scripts & ITK-SNAP test masks
│   ├── export_itksnap_mask.py
│   ├── text_shift_analysis.py
│   └── train_1935_a_1_itksnap_*.nii.gz
├── scripts/                    # Flat profiling experiment suite & core utilities
│   ├── config.py               # Dynamic path & category configuration manager (shared ../data/)
│   ├── evaluate.py             # Challenge evaluation metric calculator
│   ├── exp_001_dataset_disparity_leakage.py
│   ├── exp_002_nlp_prompt_syntax.py
│   ├── exp_003_spatial_density_priors.py
│   ├── exp_004_hu_radiodensity.py
│   ├── exp_005_morphology_noise_pruning.py
│   └── exp_006_pu_overlap.py
└── README.md                   # Primary repository documentation
```

---

## 🔬 Consolidated 6-Experiment Profiling Suite

Run any experiment using the shared Python environment:

```bash
# 1. Dataset Disparity, Patient Hierarchy & Cross-Split Leakage Audit
python scripts/exp_001_dataset_disparity_leakage.py

# 2. Free-Text NLP Syntax Shift, Tokenization Dynamics & Spatial Locators
python scripts/exp_002_nlp_prompt_syntax.py

# 3. 3D RAS Spatial Coordinate Centroids, Density Maps & 4-Panel Figure
python scripts/exp_003_spatial_density_priors.py

# 4. Hounsfield Unit (HU) Radiodensity, Contrast Deltas & Windowing Bounds
python scripts/exp_004_hu_radiodensity.py

# 5. 3D Connected-Component Morphology, Sphericity & Noise Pruning Thresholds
python scripts/exp_005_morphology_noise_pruning.py

# 6. Positive-Unlabeled (PU) Inter-Class Voxel Overlap Profiling
python scripts/exp_006_pu_overlap.py
```

---

## 📄 Key Deliverables & Outputs

1. **Empirical Data Priors Bundle** (`../data/phase_1/phase_1_priors_bundle.json`):
   - Categorical HU attenuation windowing bounds (`[min_HU, max_HU]`)
   - 3D morphology noise size pruning thresholds (`recommended_min_size_voxels`)
   - 4-Tier Spatial Prior Taxonomy mapping
   - Patient ID cross-split leakage blacklist

2. **Overleaf LaTeX Manuscript**:
   - Source code located in [`logs/phase_1_report_overleaf/main.tex`](file:///home/jdeferrari/rex_project/rexgroundingct-data-profiling/logs/phase_1_report_overleaf/main.tex) and packaged in `logs/phase_1_report_overleaf.zip`.

---

## 📝 Governance & Epistemic Modesty Guidelines

* **Epistemic Modesty**: All preliminary empirical observations use calibrated, modest phrasing (*"initial evidence suggests"*, *"preliminary tests indicate"*).
* **Server-Agnostic Rules**: Repository-wide code and documentation in git remain strictly server-agnostic using relative paths.
