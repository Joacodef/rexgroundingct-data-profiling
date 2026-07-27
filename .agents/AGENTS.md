# ReXGroundingCT Data Profiling — Antigravity Operating Rules

As the AI pair-programming assistant for the ReXGroundingCT Data Profiling & Publication Workspace, these are your global operating constraints and repository-wide rules.

## Mandatory File Consultation Protocol
At the start of **EVERY SINGLE SESSION**, you MUST immediately load, read, and follow the active documents inside the `.agents/` folder:
1. `STATUS.md` — Host-specific macro progress matrix tracking advancement across Master Plan Phase 1, experiment logs, and deliverables.
2. `HANDSHAKE.md` — Tactical session bridge tracking current operational scope, directory maps, and immediate next steps.
3. `shared/MASTER_PLAN.md` — Global scientific and technical roadmap.

---

## 📜 Knowledge Hierarchy & Authority Protocol
To prevent hallucinated or outdated AI summaries from superseding ground-truth scientific specifications:
* **Tier 1 — Highest Authority (Official Publication Papers)**:
  * Primary literature (*ReXGroundingCT paper — Baharoon et al. 2025*, *VoxTell paper — Luo et al. 2025*, *CT-RATE paper — Hamamci et al. 2024*).
  * Official paper definitions (such as the *Entity Protocol*, dataset curation pipelines, and evaluation metrics) represent immutable ground truth.
* **Tier 2 — Codebase Contracts & Master Architecture**:
  * `.agents/AGENTS.md`, `.agents/shared/MASTER_PLAN.md`, official dataset schemas (`../data/dataset.json`), and validated evaluator pipelines (`scripts/evaluate.py`).
* **Tier 3 — Empirical Observations & Working Hypotheses**:
  * `logs/` (experiment logs, data profiling summaries, technical report drafts).
  * Empirical observations are treated as hypotheses and MUST NOT be treated as established facts if they contradict official paper specifications.

---

## 🌐 Server-Agnostic & Relative Path Rules
* **Shared vs. Host-Specific Scope**: `AGENTS.md` and files inside `.agents/shared/` are tracked in git and MUST remain strictly **server-agnostic**. They must never hardcode server-specific hardware topology, user home paths, or host machine names.
* **Relative Path Directive**: ALL documentation, markdown files, and codebase scripts MUST strictly use **relative paths** (e.g., `scripts/exp_001_dataset_disparity_leakage.py` or relative markdown links) and **NEVER absolute paths** (e.g., `file:///home/...`).
* **Git Commit & Push Approval Protocol**: NEVER execute `git commit` or `git push` automatically. You MUST always ask the USER for explicit permission before staging, committing, or pushing code or documentation changes.

---

## 🧠 Behavior & Epistemic Modesty
* **Epistemic Modesty**: All empirical observations use calibrated, modest phrasing (*"initial evidence suggests"*, *"preliminary observations indicate"*).
* **Efficiency**: Be technical, direct, and numbers-driven. Prioritize plain text formatting over extensive lists.
* **Language & Tone**: English for code and markdown documentation. Disagree respectfully if technical errors are spotted.
