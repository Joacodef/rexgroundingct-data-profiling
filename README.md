# ReXGroundingCT — Phase 1: data profiling

Phase 1 of the ReXGroundingCT Challenge 2026 (MICCAI): what the dataset is, measured once and correctly,
so that every number in the data-profiling chapter of the technical report can be regenerated from a table.
The model phases live in the sibling repository `rexgroundingct-model-training`.

**Rebuilt on 2026-09-12.** The previous suite (five scripts, now under `legacy/`) measured Hounsfield units
on masks that were mirrored relative to their CT and reported voxel units as millimetres; nothing mask-based
from it should be quoted. The findings and the reasons are in
[`AUDIT_2026-09-12.md`](AUDIT_2026-09-12.md).

## Design

One extraction pass over every scan writes three tables; everything else reads the tables.

| Table | One row per | Rows | What it holds |
|---|---|---|---|
| `tables/scans.csv` | scan | 3,492 | split, original orientation, shape, spacing, field of view, intensity regime (out-of-FOV padding), lung volume and bounding box from the TotalSegmentator lobes |
| `tables/findings.csv` | finding sentence | 8,650 | text and category; for train and val (which have masks): voxels, mm³, instances (26-connectivity), extent, centroid in millimetres and in lung-box coordinates, lobe fractions, HU inside the mask and in a 3 mm shell |
| `tables/components.csv` | connected component | ~35,000 | voxels, mm³, extent, elongation, centroid, lobe, marching-cubes surface, sphericity, HU |

The column dictionary is the docstring of [`profiling/extract.py`](profiling/extract.py).

Measurement rules (`profiling/io.py`): the raw CTs are stored LPS with real spacing; the masks carry an
identity affine. A mask takes its parent CT's affine before any reorientation, both are brought to RAS
together, spacing always comes from the CT header, and voxels at or below −2048 HU are out-of-FOV padding
(the corrected volumes use −8192) and are excluded from every intensity statistic. Lung-box coordinates run
0..1 across the lung bounding box, x towards the patient's right, y anterior, z superior.

## Running

```bash
cp .env.example .env            # DATA_DIR, LOBES_DIR (optional), TABLES_DIR (optional)
uv sync                         # creates .venv from pyproject.toml
sbatch profiling/extract.slurm  # CPU job, ~1 h with 8 workers, resumable; parts land in tables/parts/
.venv/bin/python -m profiling.extract --merge   # tables/parts/*.jsonl -> tables/*.csv (tracked)
```

A shard for testing: `sbatch --export=ALL,START=0,END=3,WORKERS=1 profiling/extract.slurm`. The job never
runs on the login node: one worker holds one CT (int16) and one mask channel (uint8) plus crops.

## Layout

```
profiling/          io.py (paths, loader), extract.py (the pass), extract.slurm (launcher), text.py, analyze.py
figures/            the figures of FINDINGS.md (tracked)
tables/             all generated tables (ignored by git; regenerate with the commands above)
logs/               SLURM job output only (ignored)
legacy/             the 2026-07 suite and its experiment logs, kept for reference, superseded
.agents/            the old governance and digests; the training repository's .agents/shared/ is authoritative
```

## Results

[`FINDINGS.md`](FINDINGS.md) states what the tables show, section by section, with the figure and the summary
table behind every number. `profiling/analyze.py` produces `figures/*.png` and `tables/summary/*.csv`;
`profiling/text.py` produces `tables/text.csv` (real token counts with the VoxTell text encoder's tokenizer).

```bash
.venv/bin/python -m profiling.text        # tokens, laterality, locator vocabulary -> tables/text.csv
.venv/bin/python -m profiling.analyze     # all analyses; or a subset: analyze splits sizes hu
```
