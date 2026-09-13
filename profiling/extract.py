"""
SCRIPT:         profiling/extract.py
OBJECTIVE:      The one extraction pass of Phase 1. Every scan of every split is opened once and measured
                into three tables; every figure and every number of the data-profiling chapter is derived
                from these tables afterwards, never from the volumes again.

                tables/scans.csv       one row per scan (3,492): split, geometry, intensity regime, lung box
                tables/findings.csv    one row per finding sentence (8,650): text, category, mask measurements
                tables/components.csv  one row per 26-connected component of every annotated finding

                Measurements are made on correctly aligned RAS arrays (profiling/io.py) with spacing from the
                CT header, so millimetres are millimetres and HU values come from the lesion, not its mirror
                image (the two defects of the old suite, AUDIT_2026-09-12.md).

USAGE:          python -m profiling.extract --workers 8                # everything, resumable
                python -m profiling.extract --start 0 --end 3          # a shard (smoke test)
                python -m profiling.extract --merge                    # parts/*.jsonl -> tables/*.csv
                Parts are written as JSON lines under tables/parts/ as each scan finishes, so an interrupted
                run resumes where it stopped (scans already in scans.jsonl are skipped).

COLUMNS:
  scans:      id, split, name_prefix, n_findings, orig_axcodes, shape_x/y/z (RAS voxels), spacing_x/y/z (mm),
              voxel_mm3, fov_x/y/z_mm, ct_dtype, ct_min, ct_max, padding_present (values <= -2048),
              padding_fraction, body_p50_hu (median of voxels > -2048), lobes_available, lung_voxels,
              lung_volume_ml, lung_lo_x/y/z, lung_hi_x/y/z (bounding box, RAS voxels, hi exclusive),
              has_mask, seconds
  findings:   id, split, finding_idx, category, category_name, focal, text, n_words, n_chars,
              entity_count_json (dataset.json's count, train/val only), pixels_json (dataset.json's voxel
              count), voxels, volume_mm3, n_instances_26 (26-connectivity components), n_instances_6,
              n_labels (distinct instance labels in the mask), extent_x/y/z_mm (bounding box), centroid_x/y/z_mm,
              lung_x/y/z (centroid in the lung bounding box, 0..1; x grows to the patient's right, y to
              anterior, z to superior), in_lung_fraction, lobe_frac_LUL/LLL/RUL/RML/RLL,
              hu_mean, hu_std, hu_p05, hu_p25, hu_p50, hu_p75, hu_p95 (inside the mask, padding excluded),
              hu_shell_mean, hu_shell_p50 (a 3 mm shell around the mask, padding excluded),
              hu_contrast (hu_mean - hu_shell_mean), padding_voxels_in_mask
  components: id, split, finding_idx, category, comp_idx (1 = largest), voxels, volume_mm3, extent_x/y/z_mm,
              elongation (longest / shortest extent), centroid_x/y/z_mm, lung_x/y/z, lobe (majority, name or
              "outside"), surface_mm2 (marching cubes), sphericity (pi^(1/3) (6V)^(2/3) / A), hu_mean
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
from scipy import ndimage as ndi

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from profiling.io import (CATEGORY_MAP, FOCAL, LOBE_NAMES, PADDING_HU, RAW_IMAGES_DIR, RAW_MASKS_DIR, TABLES_DIR,  # noqa: E402
                          dataset_entries, load_ct, load_lobes, mask_channels)

STRUCT26 = np.ones((3, 3, 3), dtype=bool)
SHELL_MM = 3.0
PARTS = TABLES_DIR / "parts"


def _hu_stats(values: np.ndarray, prefix: str) -> Dict[str, float]:
    v = values[values > PADDING_HU].astype(np.float32)
    if v.size == 0:
        return {f"{prefix}_mean": np.nan, f"{prefix}_std": np.nan, **{f"{prefix}_p{p:02d}": np.nan for p in (5, 25, 50, 75, 95)}}
    q = np.percentile(v, [5, 25, 50, 75, 95])
    return {f"{prefix}_mean": float(v.mean()), f"{prefix}_std": float(v.std()),
            f"{prefix}_p05": float(q[0]), f"{prefix}_p25": float(q[1]), f"{prefix}_p50": float(q[2]), f"{prefix}_p75": float(q[3]), f"{prefix}_p95": float(q[4])}


def _bbox(mask: np.ndarray, margin: np.ndarray, shape: Tuple[int, ...]) -> Tuple[slice, ...]:
    idx = np.argwhere(mask)
    lo = np.maximum(idx.min(0) - margin, 0); hi = np.minimum(idx.max(0) + 1 + margin, shape)
    return tuple(slice(int(a), int(b)) for a, b in zip(lo, hi))


def _lung_coords(centroid_vox: np.ndarray, lung_lo: Optional[np.ndarray], lung_hi: Optional[np.ndarray]) -> Dict[str, float]:
    if lung_lo is None:
        return {"lung_x": np.nan, "lung_y": np.nan, "lung_z": np.nan}
    rel = (centroid_vox - lung_lo) / np.maximum(lung_hi - lung_lo, 1)
    return {"lung_x": float(rel[0]), "lung_y": float(rel[1]), "lung_z": float(rel[2])}


def _surface_mm2(comp: np.ndarray, spacing: np.ndarray) -> float:
    """Surface area of a binary component from a marching-cubes mesh (padded so the surface closes)."""
    from skimage import measure
    try:
        verts, faces, _, _ = measure.marching_cubes(np.pad(comp, 1).astype(np.float32), 0.5, spacing=tuple(spacing))
        return float(measure.mesh_surface_area(verts, faces))
    except (ValueError, RuntimeError):
        return np.nan


def measure_scan(entry: dict) -> Tuple[dict, List[dict], List[dict]]:
    """
    Signature:
        measure_scan(entry: dict) -> tuple[dict, list[dict], list[dict]]
    Objective:
        Measure one scan: the scan row, one row per finding (with mask measurements when the split has
        masks), one row per connected component.
    Inputs:
        entry (dict): a dataset.json entry with "split" and "id" attached (profiling.io.dataset_entries).
    Outputs:
        tuple: (scan row, finding rows, component rows).
    """
    t0 = time.time()
    sid, split = entry["id"], entry["split"]
    ct_path = RAW_IMAGES_DIR / f"{sid}.nii.gz"; mask_path = RAW_MASKS_DIR / f"{sid}.nii.gz"
    ct, sp, axcodes, affine = load_ct(ct_path)
    voxel_mm3 = float(np.prod(sp))
    padding = ct <= PADDING_HU
    body = ct[~padding]
    scan = dict(id=sid, split=split, name_prefix=sid.split("_")[0], n_findings=len(entry.get("findings", {})),
                orig_axcodes=axcodes, shape_x=int(ct.shape[0]), shape_y=int(ct.shape[1]), shape_z=int(ct.shape[2]),
                spacing_x=float(sp[0]), spacing_y=float(sp[1]), spacing_z=float(sp[2]), voxel_mm3=voxel_mm3,
                fov_x_mm=float(ct.shape[0] * sp[0]), fov_y_mm=float(ct.shape[1] * sp[1]), fov_z_mm=float(ct.shape[2] * sp[2]),
                ct_dtype=str(ct.dtype), ct_min=float(ct.min()), ct_max=float(ct.max()),
                padding_present=bool(padding.any()), padding_fraction=float(padding.mean()),
                body_p50_hu=float(np.median(body)) if body.size else np.nan)
    lobes = load_lobes(sid, affine)
    lung_lo = lung_hi = None
    if lobes is not None:
        lung = lobes > 0
        idx = np.argwhere(lung)
        lung_lo, lung_hi = idx.min(0), idx.max(0) + 1
        scan.update(lobes_available=True, lung_voxels=int(lung.sum()), lung_volume_ml=float(lung.sum() * voxel_mm3 / 1000.0),
                    lung_lo_x=int(lung_lo[0]), lung_lo_y=int(lung_lo[1]), lung_lo_z=int(lung_lo[2]),
                    lung_hi_x=int(lung_hi[0]), lung_hi_y=int(lung_hi[1]), lung_hi_z=int(lung_hi[2]))
    else:
        scan.update(lobes_available=False, lung_voxels=np.nan, lung_volume_ml=np.nan,
                    **{f"lung_{k}_{a}": np.nan for k in ("lo", "hi") for a in "xyz"})
    scan["has_mask"] = mask_path.exists()

    findings: List[dict] = []; comps: List[dict] = []
    texts = entry.get("findings", {}); cats = entry.get("categories", {})
    ecounts = entry.get("entity_counts", {}); pixels = entry.get("pixels", {})
    base_rows = {}
    for k, text in texts.items():
        cat = cats.get(k, "")
        base_rows[int(k)] = dict(id=sid, split=split, finding_idx=int(k), category=cat, category_name=CATEGORY_MAP.get(cat, ""),
                                 focal=cat in FOCAL, text=text, n_words=len(text.split()), n_chars=len(text),
                                 entity_count_json=ecounts.get(k, np.nan), pixels_json=pixels.get(k, np.nan))
    margin = np.ceil(SHELL_MM / sp).astype(int) + 1
    if scan["has_mask"]:
        for f, m in mask_channels(mask_path, affine):
            row = base_rows.get(f)
            if row is None:
                continue
            binm = m > 0
            n_vox = int(binm.sum())
            if n_vox == 0:
                row.update(voxels=0, volume_mm3=0.0, n_instances_26=0, n_instances_6=0, n_labels=0)
                continue
            sl = _bbox(binm, margin, binm.shape)
            mc = binm[sl]; cc = ct[sl]
            lab26, n26 = ndi.label(mc, structure=STRUCT26)
            _, n6 = ndi.label(mc)
            idx = np.argwhere(mc)
            lo_v = idx.min(0); hi_v = idx.max(0) + 1
            off = np.array([s.start for s in sl])
            cen = idx.mean(0) + off
            row.update(voxels=n_vox, volume_mm3=n_vox * voxel_mm3, n_instances_26=int(n26), n_instances_6=int(n6),
                       n_labels=int(len(np.unique(m[binm]))),
                       extent_x_mm=float((hi_v[0] - lo_v[0]) * sp[0]), extent_y_mm=float((hi_v[1] - lo_v[1]) * sp[1]), extent_z_mm=float((hi_v[2] - lo_v[2]) * sp[2]),
                       centroid_x_mm=float(cen[0] * sp[0]), centroid_y_mm=float(cen[1] * sp[1]), centroid_z_mm=float(cen[2] * sp[2]),
                       **_lung_coords(cen, lung_lo, lung_hi))
            if lobes is not None:
                lv = lobes[sl][mc]
                row["in_lung_fraction"] = float((lv > 0).mean())
                for l, name in LOBE_NAMES.items():
                    row[f"lobe_frac_{name}"] = float((lv == l).mean())
            else:
                row["in_lung_fraction"] = np.nan
                for name in LOBE_NAMES.values():
                    row[f"lobe_frac_{name}"] = np.nan
            inside = cc[mc]
            row.update(_hu_stats(inside, "hu"))
            row["padding_voxels_in_mask"] = int((inside <= PADDING_HU).sum())
            dist = ndi.distance_transform_edt(~mc, sampling=sp)
            shell = (dist > 0) & (dist <= SHELL_MM)
            sh = _hu_stats(cc[shell], "hu_shell")
            row.update(hu_shell_mean=sh["hu_shell_mean"], hu_shell_p50=sh["hu_shell_p50"])
            row["hu_contrast"] = float(row["hu_mean"] - sh["hu_shell_mean"]) if np.isfinite(sh["hu_shell_mean"]) else np.nan
            # components, largest first
            sizes = ndi.sum(mc, lab26, range(1, n26 + 1))
            order = np.argsort(sizes)[::-1]
            objs = ndi.find_objects(lab26)
            for rank, i in enumerate(order, start=1):
                lab_id = int(i) + 1; csl = objs[lab_id - 1]
                comp = lab26[csl] == lab_id
                cvox = int(sizes[i])
                cidx = np.argwhere(comp); c_off = np.array([s.start for s in csl]) + off
                ccen = cidx.mean(0) + c_off
                ext = (cidx.max(0) - cidx.min(0) + 1) * sp
                area = _surface_mm2(comp, sp)
                vol = cvox * voxel_mm3
                sph = float((np.pi ** (1 / 3)) * (6 * vol) ** (2 / 3) / area) if np.isfinite(area) and area > 0 else np.nan
                lobe = "outside"
                if lobes is not None:
                    lv = lobes[sl][csl][comp]
                    counts = np.bincount(lv, minlength=6)
                    lobe = LOBE_NAMES[int(counts[1:].argmax()) + 1] if counts[1:].sum() > counts[0] else "outside"
                hu = cc[csl][comp]; hu = hu[hu > PADDING_HU]
                comps.append(dict(id=sid, split=split, finding_idx=f, category=row["category"], comp_idx=rank, voxels=cvox, volume_mm3=vol,
                                  extent_x_mm=float(ext[0]), extent_y_mm=float(ext[1]), extent_z_mm=float(ext[2]),
                                  elongation=float(ext.max() / max(ext.min(), 1e-6)),
                                  centroid_x_mm=float(ccen[0] * sp[0]), centroid_y_mm=float(ccen[1] * sp[1]), centroid_z_mm=float(ccen[2] * sp[2]),
                                  **_lung_coords(ccen, lung_lo, lung_hi), lobe=lobe, surface_mm2=area, sphericity=min(sph, 1.0) if np.isfinite(sph) else np.nan,
                                  hu_mean=float(hu.mean()) if hu.size else np.nan))
    findings = [base_rows[k] for k in sorted(base_rows)]
    scan["seconds"] = round(time.time() - t0, 2)
    return scan, findings, comps


def _done_ids() -> set:
    p = PARTS / "scans.jsonl"
    if not p.exists():
        return set()
    return {json.loads(line)["id"] for line in open(p) if line.strip()}


def run(start: int, end: Optional[int], workers: int) -> None:
    entries = dataset_entries()[start:end]
    done = _done_ids()
    todo = [e for e in entries if e["id"] not in done]
    PARTS.mkdir(parents=True, exist_ok=True)
    print(f"{len(entries)} scans in range, {len(todo)} to do, {workers} workers", flush=True)
    files = {k: open(PARTS / f"{k}.jsonl", "a") for k in ("scans", "findings", "components")}
    failures = 0
    with ProcessPoolExecutor(max_workers=workers) as ex:
        futs = {ex.submit(measure_scan, e): e["id"] for e in todo}
        for n, fut in enumerate(as_completed(futs), start=1):
            sid = futs[fut]
            try:
                scan, findings, comps = fut.result()
            except Exception as exc:                                       # a bad file must not kill the run
                failures += 1
                print(f"FAILED {sid}: {type(exc).__name__}: {exc}", flush=True)
                continue
            files["scans"].write(json.dumps(scan) + "\n")
            for r in findings:
                files["findings"].write(json.dumps(r) + "\n")
            for r in comps:
                files["components"].write(json.dumps(r) + "\n")
            for fh in files.values():
                fh.flush()
            if n % 50 == 0 or n == len(todo):
                print(f"  {n}/{len(todo)} done (last {sid}, {scan['seconds']} s)", flush=True)
    for fh in files.values():
        fh.close()
    print(f"finished: {len(todo) - failures} measured, {failures} failed", flush=True)
    if failures:
        sys.exit(1)


def merge() -> None:
    import pandas as pd
    TABLES_DIR.mkdir(parents=True, exist_ok=True)
    for k in ("scans", "findings", "components"):
        p = PARTS / f"{k}.jsonl"
        df = pd.read_json(p, lines=True)
        df = df.drop_duplicates(subset=[c for c in ("id", "finding_idx", "comp_idx") if c in df.columns], keep="last")
        sort_cols = [c for c in ("split", "id", "finding_idx", "comp_idx") if c in df.columns]
        df = df.sort_values(sort_cols).reset_index(drop=True)
        out = TABLES_DIR / f"{k}.csv"
        df.to_csv(out, index=False, float_format="%.6g")
        print(f"{out}: {len(df):,} rows x {df.shape[1]} columns", flush=True)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--start", type=int, default=0); ap.add_argument("--end", type=int, default=None)
    ap.add_argument("--workers", type=int, default=max(1, (os.cpu_count() or 2) - 1))
    ap.add_argument("--merge", action="store_true", help="concatenate tables/parts/*.jsonl into tables/*.csv")
    a = ap.parse_args()
    if a.merge:
        merge()
    else:
        run(a.start, a.end, a.workers)


if __name__ == "__main__":
    main()
