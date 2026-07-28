# ReXGroundingCT Challenge 2026 — Data Profiling & Analysis Workspace

Dedicated research workspace for **Phase 1 Data Profiling & Spatial-Text Analysis** for the **ReXGrounding Challenge @ MICCAI 2026** (3D radiological finding grounding in thoracic CT scans from free-text descriptions).

> [!IMPORTANT]
> **Repository Scope & Governance**:
> This repository is dedicated exclusively to **Data Profiling, Spatial Density Prior Mapping, HU Radiodensity Analysis, NLP Syntax Shift Profiling, 3D Component Topology, Multi-Finding Co-Occurrence Profiling, and Group Technical Report Generation**.
> Model fine-tuning pipelines consume the empirical priors exported in `data/phase_1/phase_1_priors_bundle.json`.

---

## 📂 Project Structure

```text
rexgroundingct-data-profiling/
├── .agents/                    # Agentic rules, host setup docs, and governance
│   ├── shared/                 # Server-agnostic master plan and technical digests
│   ├── AGENTS.md               # Repository operating rules & governance
│   ├── STATUS.md               # Local active macro progress matrix
│   ├── HANDSHAKE.md            # Tactical session bridge & transition handoff
│   └── server_documentation.txt# Host server hardware setup & guides
├── logs/                       # Data profiling experiment logs & technical report
│   ├── exp_001_dataset_disparity_leakage.md
│   ├── exp_002_nlp_prompt_syntax.md
│   ├── exp_003_spatial_density_priors.md
│   ├── exp_004_hu_radiodensity.md
│   ├── exp_005_morphology_noise_pruning.md
│   ├── phase_1_report_overleaf/ # Consolidated LaTeX group technical report
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
│   └── exp_005_morphology_noise_pruning.py
└── README.md                   # Primary repository documentation
```

---

## 🔬 Consolidated 5-Experiment Profiling Suite

Run any experiment using the shared Python environment:

```bash
# 1. Dataset Disparity (14-Category Breakdown), Scan-Level Co-Occurrence Matrix ($14 \times 14$) & Patient Leakage Audit
python scripts/exp_001_dataset_disparity_leakage.py

# 2. Free-Text NLP Syntax Shift, Subword BPE Tokenization & Truncation Thresholds (77/128 tokens)
python scripts/exp_002_nlp_prompt_syntax.py

# 3. 3D RAS Spatial Coordinate Centroids, Density Maps & 4-Panel Figure
python scripts/exp_003_spatial_density_priors.py

# 4. Hounsfield Unit (HU) Radiodensity, Contrast Deltas & Windowing Bounds
python scripts/exp_004_hu_radiodensity.py

# 5. 3D Connected-Component Morphology, Sphericity, Physical Extents (mm) & Noise Pruning Thresholds
python scripts/exp_005_morphology_noise_pruning.py
```

---

## 📄 Key Deliverables & Outputs

1. **Empirical Data Priors Bundle** (`../data/phase_1/phase_1_priors_bundle.json`):
   - Categorical HU attenuation windowing bounds (`[min_HU, max_HU]`)
   - 3D morphology noise size pruning thresholds (`recommended_min_size_voxels`)
   - Physical 3D bounding box dimensions $(\Delta X, \Delta Y, \Delta Z)$ & aspect ratios
   - $14 \times 14$ Scan-Level Multi-Finding Co-Occurrence Matrix ($P(c_j \mid c_i)$) & heatmap (`exp001_cooccurrence_heatmap.png`)
   - 4-Tier Spatial Prior Taxonomy mapping
   - Patient ID cross-split leakage audit lists

2. **Overleaf LaTeX Group Technical Report**:
   - Source code located in [`logs/phase_1_report_overleaf/main.tex`](file://logs/phase_1_report_overleaf/main.tex) and packaged in `logs/phase_1_report_overleaf.zip`.

---

## 📝 Governance & Epistemic Modesty Guidelines

* **Epistemic Modesty**: All preliminary empirical observations use calibrated, modest phrasing (*"initial evidence suggests"*, *"preliminary tests indicate"*).
* **Server-Agnostic Rules**: Repository-wide code and documentation in git remain strictly server-agnostic using relative paths.
