# Experiment Log 002: [Phase 1] NLP Clinical Text Syntax, Prompt Shift & Spatial Alignment Analysis

**Date**: July 2026 (Consolidated July 27, 2026)  
**Status**: Completed & Audited  
**Execution Script**: [scripts/exp_002_nlp_prompt_syntax.py](file://scripts/exp_002_nlp_prompt_syntax.py)  
**Primary Output**: [../data/phase_1/analysis_experiment_002/exp002_nlp_prompt_syntax_summary.json](file://../data/phase_1/analysis_experiment_002/exp002_nlp_prompt_syntax_summary.json)  

---

## 1. Executive Summary & Objective

Experiment 002 consolidates NLP clinical text profiling across all 8,650 finding prompts in ReXGroundingCT. The analysis evaluates free-text prompt syntax, text distribution shift between the original 50-scan paper validation split and the 150-scan new MICCAI split, subword BPE tokenization dynamics, and spatial preposition directives. Diagnostic hedging language was quantified at `0.38%` (33 prompts) and pruned from downstream modeling considerations due to negligibility.

---

## 2. Validation Prompt Text Syntax & Shift Matrix

| Metric / Parameter | Cases 1–50 (Paper Split) | Cases 51–200 (New MICCAI Split) | Shift / Factor | Combined 200 Val Scans |
|---|---|---|---|---|
| **Total Finding Prompts** | 115 | 266 | `2.31x` | **381** |
| **Total Word Tokens** | 1,263 | 3,193 | `2.53x` | **4,456** |
| **Mean Word Count per Prompt** | 10.98 words | 12.00 words | `+9.3%` | 11.70 words |
| **Max Word Count in Prompt** | 21 words | **35 words** | **`1.67x` spike** | 35 words |
| **Mean Character Length** | 70.0 chars | 80.0 chars | `+14.3%` | 76.98 chars |
| **Prompts with Comma Punctuation** | 11.30% | **23.68%** | **`+12.38%` (More than 2x)** | 19.95% |
| **Type-Token Ratio (TTR, Naive)** | 0.1544 | 0.0817 | `-47.1%` | 0.0741 |
| **LN-TTR (1,000 Tokens Monte Carlo)** | 0.1740 | 0.1651 | `-5.11%` | 0.1746 |

> [!NOTE]
> **Phase 1 Decoupling Principle**: Phase 1 data profiling scripts measure intrinsic dataset properties directly from source files (`dataset.json`). Model evaluation performance benchmarks (e.g. zero-shot Dice scores and Hit Rates) belong exclusively to Phase 2 inference audits (`logs/phase_2_inference_audit/exp_003_voxtell_baseline_full_val.md`).

---

## 3. Subword BPE Tokenization & Qualitative Syntax Dynamics

1. **Subword BPE Encoder Expansion**:
   * Naive whitespace splitting measures a modest `+9.3%` word count increase ($10.98 \rightarrow 12.00$ words).
   * However, compound clinical jargon introduced in Cases 51–200 (e.g. *"peribronchovascular"*, *"posterobasal"*, or *"paramediastinal"*) is split into multiple subwords under BERT/CLIP Byte-Pair Encoding (BPE) tokenizers, expanding effective input sequence length by up to `+34.2%`.
2. **Length-Normalized Type-Token Ratio (LN-TTR)**:
   * Naive TTR drops from `0.1544` to `0.0817` due to sample-size repetition (Heaps' Law). Monte Carlo sub-sampling at 1,000 tokens reveals an actual vocabulary richness shift of `-5.11%` ($0.1740 \rightarrow 0.1651$).
3. **Compound Report Sentences & Clause Complexity**:
   * Prompts in Cases 51–200 frequently feature multi-clause clinical descriptions with stacked non-diagnostic modifiers (e.g. *"Subcentimeter, minimal, nonspecific focal ground-glass opacities..."*).

---

## 4. Text Prompt Spatial Directive Frequencies

* **Total Finding Prompts Analyzed**: `8,650`
* **Prompts with Explicit Spatial Locators**: `5,570` (`64.39%`)

| Anatomical Spatial Keyword | Occurrences | Percentage of Prompts |
|---|---|---|
| **right** | 2,616 | `30.24%` |
| **left** | 1,897 | `21.93%` |
| **lower lobe** | 1,735 | `20.06%` |
| **upper lobe** | 1,255 | `14.51%` |
| **middle lobe** | 798 | `9.23%` |
| **subpleural** | 714 | `8.25%` |
| **peripheral** | 487 | `5.63%` |
| **posterobasal** | 458 | `5.29%` |
| **bilateral** | 452 | `5.23%` |
| **basal** | 319 | `3.69%` |
| **apical** | 203 | `2.35%` |
| **lingula** | 124 | `1.43%` |
| **anterobasal** | 80 | `0.92%` |
| **apex** | 55 | `0.64%` |
| **paramediastinal** | 24 | `0.28%` |

---

## 5. Category-Level Clinical Text Profiling Matrix

| Cat Code | Category Name | Findings | Median Word Count | Compound Prompts (%) | Spatial Locators (%) |
|---|---|---|---|---|---|
| `1a` | **Bronchial wall thickening** | 245 | `7.0` | `10.20%` | `40.41%` |
| `1b` | **Bronchiectasis** | 304 | `9.0` | `17.43%` | `47.04%` |
| `1c` | **Emphysema** | 490 | `6.0` | `5.71%` | `21.22%` |
| `1d` | **Septal thickening** | 209 | `9.0` | `20.57%` | `35.41%` |
| `1e` | **Micronodules** | 341 | `10.0` | `17.30%` | `52.20%` |
| `1f` | **Other non-focal** | 158 | `7.0` | `10.76%` | `32.28%` |
| `2a` | **Linear opacities** | 1302 | `10.0` | `18.97%` | `70.05%` |
| `2b` | **Atelectasis / consolidation** | 1505 | `11.0` | `30.83%` | `75.48%` |
| `2c` | **Ground-glass opacity** | 1654 | `12.0` | `26.90%` | `75.51%` |
| `2d` | **Pulmonary nodules / masses** | 2065 | `11.0` | `9.35%` | `63.73%` |
| `2e` | **Pleural effusion / thickening** | 275 | `9.0` | `12.00%` | `87.27%` |
| `2f` | **Honeycombing** | 16 | `11.0` | `18.75%` | `68.75%` |
| `2g` | **Pneumothorax** | 20 | `8.0` | `15.00%` | `95.00%` |
| `2h` | **Other focal** | 66 | `8.5` | `16.67%` | `57.58%` |

> [!NOTE]
> **Hedging Language Pruning Directive**: Diagnostic hedging/uncertainty language (e.g. *"probable"*, *"versus"*, *"rule out"*) was detected in only 33 out of 8,650 prompts (`0.38%`). Due to its statistical insignificance, hedging parsing was pruned from downstream model loss formulations.

---

## 6. Artifact & Script References

* **Summary Output JSON**: [../data/phase_1/analysis_experiment_002/exp002_nlp_prompt_syntax_summary.json](file://../data/phase_1/analysis_experiment_002/exp002_nlp_prompt_syntax_summary.json)
* **Execution Script**: [scripts/exp_002_nlp_prompt_syntax.py](file://scripts/exp_002_nlp_prompt_syntax.py)

