# Phase 1 findings — ReXGroundingCT, measured 2026-09-12

Every number below is read from `tables/summary/*.csv`, which `profiling/analyze.py` derives from the three
tables of the extraction pass (`tables/scans.csv`, `findings.csv`, `components.csv`) and the token table
(`tables/text.csv`). The tables are not tracked by git; `profiling/extract.slurm`, `profiling/text.py` and
`profiling/analyze.py` regenerate them (about 2.5 h of CPU for the extraction). Dataset: the MICCAI release as deployed on `ih-condor`, 3,492 scans, `dataset.json` of
2026-09-05. Masks were measured with the correct policy (parent-CT affine before reorientation, spacing from
the CT header), so millimetres, Hounsfield units and positions are those of the lesions themselves; the
previous suite's mask-based numbers were not (`AUDIT_2026-09-12.md`).

## 1. Composition

| split | scans | patients | findings | findings / scan | masks |
|---|---|---|---|---|---|
| train | 2,992 | 2,717 | 7,687 | 2.57 | yes |
| val | 200 | 190 | 381 | 1.91 | yes |
| test | 300 | 281 | 582 | 1.94 | no |

Patients are keyed as `<partition>_<number>` because CT-RATE numbers its `train_` and `valid_` partitions
independently (414 train scans carry the `valid_` prefix; a bare number would merge 114 unrelated pairs).
Cross-split patient overlap: train–val 2, train–test 3, val–test 5, matching the training repository's
`DATASET_FACTS.md` §4. Category share by split: `fig_category_share.png`, `tables/summary/categories.csv`.
Pulmonary nodules (2d) are 23 % of train findings but 35 % of val and 33 % of test; ground-glass (2c) and
consolidation (2b) go the other way (20 % and 18 % of train, 16 % and 13 % of val).

## 2. The annotation-density gap (`fig_annotation_gap.png`)

Training findings were annotated under the Entity Protocol (at most three representative instances);
validation findings exhaustively. Three ways to count it, all from this pass:

| definition | train | val | val / train |
|---|---|---|---|
| `entity_counts` stored in dataset.json (the number the technical report quotes) | 1.95 | 3.71 | **1.91×** |
| distinct instance labels actually present in the mask | 1.89 | 3.56 | **1.88×** |
| 26-connected components of the mask | 2.84 | 4.91 | **1.73×** |

The report's 1.91× reproduces exactly. The mask-label count is slightly lower because dataset.json disagrees
with the mask for 400 train and 40 val findings (a stored count that the mask does not contain); the
component count is higher because annotated instances often break into several pieces, above all for the
diffuse categories. Per category the gap runs from 3.0× (ground-glass), 2.4× (septal thickening,
micronodules) and 2.0× (nodules, bronchial wall thickening) down to below 1× for pneumothorax and "other
focal", which are single objects in both protocols. As a loader check, the voxel count of every one of the
7,687 train findings equals the `pixels` field of dataset.json.

## 3. Lesion size (`fig_sizes.png`, `tables/summary/sizes.csv`)

Components of train and validation (23,739): the 5th–95th percentile spans 4.8 orders of magnitude,
0.24 mm³ to 4.1 L over all categories. Pulmonary nodules are the tightest category (median 93 mm³, 199
voxels, 7.5 mm largest extent, p5–p95 within 2.1 orders) and the roundest (median sphericity 0.79 against
0.43–0.44 for linear opacities and effusions). Effusions span 5.6 orders (median 8.7 cm³). Of all
components, 11.0 % are below the 27-voxel floor used by the two-stage grounder's candidate stage; by
category that is 4.5 % of nodules but 27 % of bronchial wall thickening, 33 % of honeycombing and 38 % of
pneumothorax fragments. Per finding, the median annotated volume is 4.1 cm³ in train and 1.6 cm³ in val.

## 4. Where findings sit (`fig_spatial_coronal.png`, `fig_spatial_sagittal.png`, `tables/summary/spatial.csv`)

Positions are centroids in lung-box coordinates (0..1 across the lung bounding box from the TotalSegmentator
lobes, available for every scan). The old "four-tier taxonomy" becomes a measurement: emphysema is apical
(mean z 0.66 in train, 0.82 in val; 60 % of its voxels in the upper lobes), effusions basal (z 0.40, and
49 % of their voxels outside the lung mask, as pleural fluid should be), bronchial wall thickening and
bronchiectasis central and peribronchial, nodules and ground-glass spread through the parenchyma. Train and
validation agree where the validation count is large: for nodules the Kolmogorov–Smirnov distance between
splits is ≤ 0.07 on every axis; the larger distances (0.3–0.6) belong to categories with 3–11 validation
findings and mean nothing. 428 findings have less than half their voxels inside the lung mask: 120
effusions, 93 consolidations (juxta-diaphragmatic), 76 nodules, 54 linear opacities.

## 5. Radiodensity (`fig_hu.png`, `tables/summary/hu.csv`)

Median HU inside the annotation against a 3 mm shell around it (padding excluded), medians over findings:

| category | inside | shell | contrast |
|---|---|---|---|
| 2g pneumothorax | −963 | −337 | −393 |
| 1c emphysema | −849 | −779 | −160 |
| 2e pleural effusion | −1 | −30 | +71 |
| 2b atelectasis / consolidation | −419 | −620 | +74 |
| 2d pulmonary nodules | −624 | −824 | +159 |
| 2c ground-glass | −653 | −743 | −2 |

Pneumothorax reads as air and effusion as water, which is the direct check that mask and CT are aligned.
Two things matter for modelling: nodule masks are dominated by partial volume (median −624 HU inside a
7.5 mm object), and 28 % of all findings have an inside-vs-shell contrast below 50 HU (41 % of ground-glass,
44 % of bronchiectasis), so a large share of the targets is not separable from its surroundings by intensity.

## 6. Text (`fig_text_tokens.png`, `tables/summary/text_*.csv`)

With the tokenizer VoxTell's text encoder uses (Qwen3-Embedding-4B): median 10 words, 15 tokens, 39 tokens
for the full instruction prompt; the longest prompt is 85 tokens against the encoder's 128-token limit, so
nothing is truncated (the old 77/128-token "truncation rates" were estimates from a word-length rule).
41 % of sentences are bilateral, 12 % carry no laterality, 42–50 % name a lobe and 32–39 % a segment.
Validation sentences are slightly longer and more localised than training ones (50 % name a lobe against 42 %).

## 7. Images (`fig_scans.png`, `tables/summary/scans.csv`)

All 3,492 volumes are stored LPS. In-plane spacing: median 0.70 mm (0.30–0.98). Slice spacing takes a few
discrete values: 0.75 mm (44 %), 1.5 mm (22 %), 1.0 mm (21 %), 1.25 mm (11 %). Slices: median 332
(104–1,005). Median lung volume 4.2 L. Out-of-field padding: 870 scans (24.9 %) contain voxels at or below
−2048 HU, 732 of them with a minimum of exactly −8192; `DATASET_FACTS.md` §8's 365 counts scans whose first
slice holds a padding block (median 2.7 % of the volume), a stricter definition that excludes the scans where
only isolated stray voxels reach the sentinel. The splits do not differ in any of these distributions.

## 8. Co-occurrence (`fig_cooccurrence.png`, `tables/summary/cooccurrence_*.csv`)

Scan-level conditional probabilities P(column | row). Nodules are the most frequent companion of every
non-focal category (0.41–0.51); consolidation accompanies effusion (0.60) and pneumothorax (0.53);
ground-glass accompanies "other focal" (0.59) and septal thickening (0.51). Honeycombing (16 train findings,
none in val or test) never co-occurs with effusion or pneumothorax.

## 9. What this changes with respect to the old suite

* The 1.91× annotation gap, the split counts, the co-occurrence matrix and the patient overlap stand.
* Every HU figure and every millimetre figure of the old suite is replaced; the old HU numbers came from
  mirrored masks and the old volumes were voxel counts labelled as mm³.
* The spatial prior is now measured in lung coordinates rather than voxel-grid fractions.
* Token counts are real; there is no truncation.
* New: the three definitions of "instances per finding" and their disagreement with dataset.json; the
  27-voxel floor statistics; the low-contrast share; the out-of-lung findings; the padding census.

Open questions worth a look: the 440 findings whose stored instance count does not match the mask; whether
the 76 nodule findings mostly outside the lung mask are pleural, juxta-diaphragmatic or lobe-mask misses.

## Figures

| file | shows |
|---|---|
| `figures/fig_category_share.png` | share of findings per category, train / val / test |
| `figures/fig_annotation_gap.png` | annotated instances per finding, train vs val, per category |
| `figures/fig_sizes.png` | component volume per category on a log scale, with the 27-voxel floor |
| `figures/fig_spatial_coronal.png`, `fig_spatial_sagittal.png` | density of train components in lung-box coordinates, per category |
| `figures/fig_hu.png` | median HU inside the annotation vs its 3 mm shell, per category |
| `figures/fig_text_tokens.png` | prompt length in tokens per split, with the 128-token limit |
| `figures/fig_scans.png` | spacing, slices and lung volume per split |
| `figures/fig_cooccurrence.png` | P(column present given row present) at scan level |
