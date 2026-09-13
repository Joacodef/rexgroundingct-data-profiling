"""
MODULE:         profiling/examples.py
OBJECTIVE:      Pick one representative annotated finding per category for the report's example figure,
                and say in numbers why it is representative. Candidates come from the validation split
                (exhaustive annotation); a category with too few validation findings (honeycombing: none;
                pneumothorax: one, an extreme 1.1 L case) takes a training-split example, flagged as such.
                Two hard gates, then a distance to the category's medians:
                  gate 1  the sentence names the pathology in its own words (keyword per category), so a
                          finding the index mislabelled cannot be chosen as an example of the label;
                  gate 2  the sentence's laterality agrees with where the mask sits (lobe fractions);
                  score   sum over volume, component count, largest-component sphericity and elongation,
                          height in the lung box, and median HU inside the mask of |percentile - 50|,
                          percentiles taken within the category's own candidate pool.
USAGE:          python -m profiling.examples          -> prints the picks, writes tables/summary/examples.csv
                                                        and a CASES literal for the render recipe.
"""
from __future__ import annotations

import re
import numpy as np
import pandas as pd
from profiling.analyze import load, table, CATS
from profiling.io import CATEGORY_MAP

KEYWORD = {"1a": r"bronchial wall|peribronchial", "1b": r"bronchiectas", "1c": r"emphysema", "1d": r"septal",
           "1e": r"micronodul|centrilobular nodul|tree.in.bud", "1f": r"mosaic|attenuation", "2a": r"linear|band|fibrotic|fibrosis|sequel",
           "2b": r"atelecta|consolidat", "2c": r"ground.glass", "2d": r"\bnodul|\bmass", "2e": r"effusion|pleural thickening",
           "2f": r"honeycomb", "2g": r"pneumothorax", "2h": r"cyst|bleb|cavit|halo|crazy|distortion"}
TRAIN_ONLY = {"2f", "2g"}                                          # no or one validation finding
NUMERIC = ["volume_mm3", "n_components", "sphericity", "elongation", "lung_z", "hu_p50"]


def pick() -> pd.DataFrame:
    t = load(); f = t["findings"].copy(); c = t["components"]
    largest = c.sort_values("voxels", ascending=False).drop_duplicates(["id", "finding_idx"])[["id", "finding_idx", "sphericity", "elongation"]]
    ncomp = c.groupby(["id", "finding_idx"]).size().rename("n_components").reset_index()
    f = f.merge(largest, on=["id", "finding_idx"], how="left").merge(ncomp, on=["id", "finding_idx"], how="left")
    f["left_frac"] = f["lobe_frac_LUL"].fillna(0) + f["lobe_frac_LLL"].fillna(0)
    f["right_frac"] = f["lobe_frac_RUL"].fillna(0) + f["lobe_frac_RML"].fillna(0) + f["lobe_frac_RLL"].fillna(0)
    rows = []
    for cat in CATS:
        if cat in ("1f", "2h"):
            continue                                                   # the two "other" classes have no single picture
        split = "train" if cat in TRAIN_ONLY else "val"
        d = f[(f.split == split) & (f.category == cat) & (f.voxels > 0)].copy()
        d = d[d.text.str.contains(KEYWORD[cat], case=False, regex=True, na=False)]           # gate 1
        lat = d.laterality.fillna("none")
        inlung = d.left_frac + d.right_frac                          # pleural findings sit mostly outside the lobes
        share_l = np.where(inlung > 0.05, d.left_frac / inlung.clip(lower=1e-9), np.nan)
        share_r = np.where(inlung > 0.05, d.right_frac / inlung.clip(lower=1e-9), np.nan)
        unjudgeable = inlung <= 0.05                                 # too little of the mask in the lungs to place it
        agree = unjudgeable | (lat == "none") | ((lat == "left") & (share_l >= 0.8)) | ((lat == "right") & (share_r >= 0.8)) | \
                ((lat == "bilateral") & (share_l >= 0.2) & (share_r >= 0.2))
        d = d[agree]                                                                          # gate 2
        d = d.dropna(subset=NUMERIC)
        pct = d[NUMERIC].rank(pct=True) * 100
        d["score"] = (pct - 50).abs().sum(axis=1)
        for col in NUMERIC:
            d[f"pct_{col}"] = pct[col].round(0)
        best = d.sort_values("score").iloc[0]
        rows.append({"category": cat, "name": CATEGORY_MAP[cat], "split": split, "candidates": len(d), "id": best.id,
                     "finding_idx": int(best.finding_idx), "text": best.text, "volume_cm3": round(best.volume_mm3 / 1000, 2),
                     "n_components": int(best.n_components), "sphericity": round(best.sphericity, 2), "lung_z": round(best.lung_z, 2),
                     "hu_p50": int(best.hu_p50), **{f"pct_{k}": int(best[f"pct_{k}"]) for k in NUMERIC}, "score": round(best.score, 0)})
    out = pd.DataFrame(rows); table(out, "examples")
    return out


if __name__ == "__main__":
    out = pick()
    pd.set_option("display.width", 250); pd.set_option("display.max_colwidth", 70)
    print(out[["category", "name", "split", "candidates", "id", "finding_idx", "volume_cm3", "n_components"] + [f"pct_{k}" for k in NUMERIC] + ["score"]].to_string(index=False))
    print("\nsentences:")
    for r in out.itertuples():
        print(f"  {r.category} {r.name}: \"{r.text}\"")
    print("\nCASES = [" + ",\n         ".join(f'("{r.name}{" (training split)" if r.split == "train" else ""}", "{r.id}", {r.finding_idx})' for r in out.itertuples()) + "]")
