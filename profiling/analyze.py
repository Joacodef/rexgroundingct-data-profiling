"""
SCRIPT:         profiling/analyze.py
OBJECTIVE:      Every figure and every number of the Phase 1 chapter, derived from the tables written by
                profiling/extract.py and profiling/text.py. Nothing here opens a volume. Each analysis writes
                one or two PNG figures under figures/ and the numbers it plots as CSV under tables/summary/,
                so a figure can always be checked against its table.

USAGE:          .venv/bin/python -m profiling.analyze [splits sizes spatial hu text scans cooccurrence]   (default: all)

ANALYSES:
  splits        split composition; category share of findings per split; the annotation-density gap
                (instances per finding, train vs val, recomputed from the masks with 26-connectivity)
  sizes         lesion size: component volume per category (log scale), percentiles, fraction below the
                stage-1 27-voxel floor
  spatial       where each category sits in the lung box (population densities, train), centroid and lobe
                agreement between train and val
  hu            radiodensity inside the mask vs the 3 mm shell, per category, on correctly aligned arrays
  text          sentence length in words and real tokens per split and category, laterality and locator
                vocabulary, truncation at the encoder's 128-token limit
  scans         image geometry per split: spacing, slices, field of view, orientation, padding regime,
                lung volume
  cooccurrence  scan-level category co-occurrence P(column | row) and the cross-split patient overlap

STYLE:          three categorical slots for the splits (train blue, val orange, test aqua), one blue ramp for
                magnitude, thin marks, direct labels only where they help, gridlines recessive.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from profiling.io import CATEGORY_MAP, LOBE_NAMES, REPO, TABLES_DIR  # noqa: E402

import os
FIG = Path(os.getenv("FIGURES_DIR") or REPO / "figures"); SUM = TABLES_DIR / "summary"
SPLIT_COLOR = {"train": "#2a78d6", "val": "#eb6834", "test": "#1baf7a"}
SPLIT_LABEL = {"train": "train (Entity Protocol)", "val": "validation (exhaustive)", "test": "test"}
INK, INK2, GRID = "#0b0b0b", "#52514e", "#e6e5e1"
BLUE_RAMP = ["#cde2fb", "#9ec5f4", "#6da7ec", "#3987e5", "#256abf", "#184f95", "#0d366b"]
CATS = list(CATEGORY_MAP)                                           # 1a..2h, fixed order everywhere
CAT_LABEL = {c: CATEGORY_MAP[c] for c in CATS}                    # report rule 1: pathologies by name, never by code
CAT_SHORT = {"1a": "Bronchial wall thick.", "1b": "Bronchiectasis", "1c": "Emphysema", "1d": "Septal thickening",
             "1e": "Micronodules", "1f": "Other non-focal", "2a": "Linear opacities", "2b": "Atelectasis / consol.",
             "2c": "Ground-glass", "2d": "Nodules / masses", "2e": "Pleural effusion", "2f": "Honeycombing",
             "2g": "Pneumothorax", "2h": "Other focal"}                # panel titles

plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9, "axes.edgecolor": INK2, "axes.linewidth": 0.6,
                     "axes.titlesize": 10, "axes.titleweight": "normal", "axes.labelcolor": INK2, "xtick.color": INK2,
                     "ytick.color": INK2, "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.6, "axes.axisbelow": True,
                     "axes.spines.top": False, "axes.spines.right": False, "legend.frameon": False, "figure.dpi": 150})


def load() -> dict:
    t = {k: pd.read_csv(TABLES_DIR / f"{k}.csv") for k in ("scans", "findings", "components")}
    tx = TABLES_DIR / "text.csv"
    if tx.exists():
        t["text"] = pd.read_csv(tx)
        t["findings"] = t["findings"].merge(t["text"].drop(columns=["split", "n_words"]), on=["id", "finding_idx"], how="left")
    for k in ("findings", "components"):
        t[k]["category"] = pd.Categorical(t[k]["category"], categories=CATS)
    return t


def save(fig, name: str, dpi: int | None = None) -> None:
    FIG.mkdir(parents=True, exist_ok=True)
    fig.savefig(FIG / f"{name}.png", bbox_inches="tight", dpi=dpi); plt.close(fig)
    print(f"  figures/{name}.png", flush=True)


def table(df: pd.DataFrame, name: str) -> None:
    SUM.mkdir(parents=True, exist_ok=True)
    df.to_csv(SUM / f"{name}.csv", index=False, float_format="%.4g")
    print(f"  tables/summary/{name}.csv ({len(df)} rows)", flush=True)


def hbar_by_category(ax, values: pd.Series, color: str, label: str | None = None, offset: float = 0.0, height: float = 0.8):
    y = np.arange(len(CATS)) + offset
    ax.barh(y, [values.get(c, 0) for c in CATS], height=height, color=color, label=label, linewidth=0)
    ax.set_yticks(np.arange(len(CATS))); ax.set_yticklabels([CAT_LABEL[c] for c in CATS]); ax.invert_yaxis()


def patient_id(ids: pd.Series) -> pd.Series:
    """CT-RATE numbers patients independently per source partition, so the patient key is <partition>_<number>
    (train_302 and valid_302 are different people); a bare number would merge 114 unrelated pairs."""
    return ids.str.split("_").str[:2].str.join("_")


# ----------------------------------------------------------------------------------------------- analyses
def splits(t: dict) -> None:
    s, f = t["scans"], t["findings"]
    f = f.assign(patient=patient_id(f["id"]))
    rows = []
    for sp in ("train", "val", "test"):
        fs, ss = f[f.split == sp], s[s.split == sp]
        masked = fs.dropna(subset=["voxels"])
        rows.append(dict(split=sp, scans=len(ss), patients=patient_id(ss["id"]).nunique(), findings=len(fs),
                         findings_per_scan=len(fs) / max(len(ss), 1), findings_with_mask=len(masked),
                         instance_labels_per_finding_mean=masked["n_labels"].mean(), components_per_finding_mean=masked["n_instances_26"].mean(),
                         entity_count_json_mean=fs["entity_count_json"].mean(),
                         voxels_per_finding_median=masked["voxels"].median(), volume_ml_per_finding_median=masked["volume_mm3"].median() / 1000))
    table(pd.DataFrame(rows), "splits")
    # category share per split, and the instance gap
    SPLITS = ["train", "val", "test"]
    share = f.groupby(["split", "category"], observed=False).size().unstack(0).reindex(columns=SPLITS).fillna(0)
    share_pct = share / share.sum() * 100
    inst = f.dropna(subset=["n_labels"]).groupby(["split", "category"], observed=False)["n_labels"].agg(["mean", "median", "max", "count"]).unstack(0)
    inst = inst.reindex(columns=pd.MultiIndex.from_product([["mean", "median", "max", "count"], SPLITS]))
    comp = f.dropna(subset=["n_instances_26"]).groupby(["split", "category"], observed=False)["n_instances_26"].mean().unstack(0).reindex(columns=SPLITS)
    cat = pd.DataFrame({"category": CATS, "name": [CATEGORY_MAP[c] for c in CATS]})
    for sp in ("train", "val", "test"):
        cat[f"findings_{sp}"] = share[sp].reindex(CATS).values.astype(int); cat[f"share_pct_{sp}"] = share_pct[sp].reindex(CATS).values
    for sp in ("train", "val"):
        cat[f"instances_mean_{sp}"] = inst[("mean", sp)].reindex(CATS).values; cat[f"instances_max_{sp}"] = inst[("max", sp)].reindex(CATS).values
        cat[f"components_mean_{sp}"] = comp[sp].reindex(CATS).values
    cat["instance_gap_val_over_train"] = cat["instances_mean_val"] / cat["instances_mean_train"]
    cat["component_gap_val_over_train"] = cat["components_mean_val"] / cat["components_mean_train"]
    vol = f.dropna(subset=["volume_mm3"]).groupby(["split", "category"], observed=False)["volume_mm3"].median().unstack(0).reindex(columns=SPLITS)
    for sp in ("train", "val"):
        cat[f"volume_mm3_median_{sp}"] = vol[sp].reindex(CATS).values
    table(cat, "categories")
    def mean_of(col, sp):
        v = f[f.split == sp][col].dropna(); return float(v.mean()) if len(v) else float("nan")
    gap_all = mean_of("n_labels", "val") / mean_of("n_labels", "train")
    gap_comp = mean_of("n_instances_26", "val") / mean_of("n_instances_26", "train")
    json.dump({"instance_labels_per_finding_train": mean_of("n_labels", "train"), "instance_labels_per_finding_val": mean_of("n_labels", "val"),
               "gap_val_over_train_labels": gap_all, "components_per_finding_train": mean_of("n_instances_26", "train"),
               "components_per_finding_val": mean_of("n_instances_26", "val"), "gap_val_over_train_components": gap_comp,
               "entity_count_json_train": mean_of("entity_count_json", "train"), "entity_count_json_val": mean_of("entity_count_json", "val")},
              open(SUM / "annotation_gap.json", "w"), indent=2)
    print(f"  annotation gap, val / train: {gap_all:.2f}x by annotated instance labels, {gap_comp:.2f}x by 26-connected components", flush=True)

    fig, ax = plt.subplots(figsize=(7.2, 5.2))
    for i, sp in enumerate(("train", "val", "test")):
        hbar_by_category(ax, share_pct[sp], SPLIT_COLOR[sp], SPLIT_LABEL[sp], offset=(i - 1) * 0.27, height=0.25)
    ax.set_xlabel("share of the split's findings (%)"); ax.legend(loc="lower right"); ax.grid(axis="y", visible=False)
    save(fig, "fig_category_share")

    fig, ax = plt.subplots(figsize=(7.2, 5.2))
    y = np.arange(len(CATS))
    tr = cat["instances_mean_train"].values; va = cat["instances_mean_val"].values
    for yi, a, b in zip(y, tr, va):
        ax.plot([a, b], [yi, yi], color=GRID, linewidth=2, zorder=1)
    ax.scatter(tr, y, color=SPLIT_COLOR["train"], s=28, zorder=2, label="train (Entity Protocol, at most 3 instances)")
    ax.scatter(va, y, color=SPLIT_COLOR["val"], s=28, zorder=2, label="validation (exhaustive)")
    for yi, a, b in zip(y, tr, va):
        if np.isfinite(a) and np.isfinite(b) and b > 0:
            ax.text(max(a, b) + 0.15, yi, f"{b / a:.1f}x" if a > 0 else "", va="center", fontsize=8, color=INK2)
    ax.set_yticks(y); ax.set_yticklabels([CAT_LABEL[c] for c in CATS]); ax.invert_yaxis(); ax.grid(axis="y", visible=False)
    ax.set_xlabel("mean annotated instances per finding (distinct instance labels in the mask)"); ax.legend(loc="lower right")
    save(fig, "fig_annotation_gap")


def sizes(t: dict) -> None:
    c = t["components"]; c = c[c.split.isin(["train", "val"])]
    g = c.groupby("category", observed=False)["volume_mm3"]
    rows = pd.DataFrame({"category": CATS, "name": [CATEGORY_MAP[k] for k in CATS], "components": g.size().reindex(CATS).values,
                         "vol_mm3_p05": g.quantile(0.05).reindex(CATS).values, "vol_mm3_p50": g.median().reindex(CATS).values,
                         "vol_mm3_p95": g.quantile(0.95).reindex(CATS).values, "vol_mm3_max": g.max().reindex(CATS).values,
                         "voxels_p50": c.groupby("category", observed=False)["voxels"].median().reindex(CATS).values,
                         "below_27_voxels_pct": (c.groupby("category", observed=False)["voxels"].apply(lambda v: (v < 27).mean() * 100)).reindex(CATS).values,
                         "extent_max_mm_p50": c.assign(ext=c[["extent_x_mm", "extent_y_mm", "extent_z_mm"]].max(axis=1)).groupby("category", observed=False)["ext"].median().reindex(CATS).values,
                         "sphericity_p50": c.groupby("category", observed=False)["sphericity"].median().reindex(CATS).values})
    rows["range_orders_of_magnitude_p05_p95"] = np.log10(rows["vol_mm3_p95"] / rows["vol_mm3_p05"])
    table(rows, "sizes")
    fig, ax = plt.subplots(figsize=(7.2, 5.2))
    data = [np.log10(c[c.category == k]["volume_mm3"].clip(lower=0.1)) for k in CATS]
    bp = ax.boxplot(data, vert=False, widths=0.55, showfliers=False, patch_artist=True, medianprops=dict(color=INK, linewidth=1),
                    boxprops=dict(facecolor=BLUE_RAMP[1], edgecolor=BLUE_RAMP[4], linewidth=0.6), whiskerprops=dict(color=BLUE_RAMP[4], linewidth=0.6), capprops=dict(color=BLUE_RAMP[4], linewidth=0.6))
    ax.set_yticks(np.arange(1, len(CATS) + 1)); ax.set_yticklabels([CAT_LABEL[k] for k in CATS]); ax.invert_yaxis(); ax.grid(axis="y", visible=False)
    vox = float(t["scans"]["voxel_mm3"].median()); floor = np.log10(27 * vox)
    ax.axvline(floor, color=INK2, linewidth=0.8); ax.text(floor, len(CATS) + 0.9, f" 27 voxels at the median voxel ({vox:.2f} mm³)", fontsize=7.5, color=INK2, va="top")
    ax.set_ylim(len(CATS) + 1.2, 0.3)
    ticks = [0, 1, 2, 3, 4, 5, 6]; ax.set_xticks(ticks); ax.set_xticklabels(["1 mm³", "10", "100", "1 cm³", "10", "100", "1 L"])
    ax.set_xlabel("volume of one connected component (log scale); box = quartiles, whiskers = 1.5 IQR, outliers hidden")
    save(fig, "fig_sizes")


def spatial(t: dict) -> None:
    f = t["findings"].dropna(subset=["lung_x"]); c = t["components"].dropna(subset=["lung_x"])
    rows = []
    for k in CATS:
        tr, va = f[(f.category == k) & (f.split == "train")], f[(f.category == k) & (f.split == "val")]
        row = dict(category=k, name=CATEGORY_MAP[k], n_train=len(tr), n_val=len(va))
        for ax_ in "xyz":
            row[f"lung_{ax_}_mean_train"] = tr[f"lung_{ax_}"].mean(); row[f"lung_{ax_}_mean_val"] = va[f"lung_{ax_}"].mean()
            if len(tr) > 1 and len(va) > 1:
                from scipy.stats import ks_2samp
                row[f"ks_{ax_}"] = ks_2samp(tr[f"lung_{ax_}"], va[f"lung_{ax_}"]).statistic
        for l in LOBE_NAMES.values():
            row[f"lobe_{l}_pct_train"] = tr[f"lobe_frac_{l}"].mean() * 100
        row["in_lung_pct_train"] = tr["in_lung_fraction"].mean() * 100
        rows.append(row)
    table(pd.DataFrame(rows), "spatial")
    # population densities: coronal (x, z) per category, components of the train split, in lung-box coordinates
    ctr = c[c.split == "train"]
    from scipy.ndimage import gaussian_filter
    cmap = matplotlib.colors.LinearSegmentedColormap.from_list("b", ["#ffffff"] + BLUE_RAMP)

    def density_panels(xcol, xlabel, name, title):
        """One panel per category: a 64x64 histogram of component centroids in lung-box coordinates,
        smoothed with a 1-bin Gaussian so the map reads as a density; each panel on its own scale."""
        fig, axes = plt.subplots(2, 7, figsize=(14, 5.2), sharex=True, sharey=True)
        for ax, k in zip(axes.flat, CATS):
            d = ctr[ctr.category == k]
            h, _, _ = np.histogram2d(d[xcol].clip(0, 1), d["lung_z"].clip(0, 1), bins=64, range=[[0, 1], [0, 1]])
            h = gaussian_filter(h, sigma=1.0); h = h / max(h.max(), 1e-9)
            ax.imshow(h.T, origin="lower", extent=[0, 1, 0, 1], cmap=cmap, vmin=0, vmax=1, aspect="auto", interpolation="bilinear")
            ax.set_title(f"{CAT_SHORT[k]} ({len(d):,})", fontsize=8); ax.grid(False); ax.set_xticks([0, 0.5, 1]); ax.set_yticks([0, 0.5, 1])
        axes[1, 0].set_xlabel(xlabel, fontsize=8); axes[1, 0].set_ylabel("inferior ← z → superior", fontsize=8)
        save(fig, name, dpi=220)

    density_panels("lung_x", "left ← lung box x → right", "fig_spatial_coronal",
                   "Where each category sits: coronal density of train components in lung-box coordinates (per-panel scale, darker = more)")

    # train (Entity Protocol) against validation (exhaustive): the same coronal density, one row per split
    # for each block of seven categories, so the two annotation protocols can be compared category by category
    fig, axes = plt.subplots(4, 7, figsize=(14, 9.6), sharex=True, sharey=True)
    for block, cats in enumerate((CATS[:7], CATS[7:])):
        for col, k in enumerate(cats):
            for row, (split, color) in enumerate((("train", SPLIT_COLOR["train"]), ("val", SPLIT_COLOR["val"]))):
                ax = axes[2 * block + row, col]
                d = c[(c.split == split) & (c.category == k)]
                h, _, _ = np.histogram2d(d["lung_x"].clip(0, 1), d["lung_z"].clip(0, 1), bins=64, range=[[0, 1], [0, 1]])
                h = gaussian_filter(h, sigma=1.0); h = h / max(h.max(), 1e-9)
                cm = matplotlib.colors.LinearSegmentedColormap.from_list("s", ["#ffffff", color])
                ax.imshow(h.T, origin="lower", extent=[0, 1, 0, 1], cmap=cm, vmin=0, vmax=1, aspect="auto", interpolation="bilinear")
                ax.set_title(f"{CAT_SHORT[k]}, {'train' if split == 'train' else 'val'} ({len(d):,})", fontsize=7.5, color=INK)
                ax.grid(False); ax.set_xticks([0, 0.5, 1]); ax.set_yticks([0, 0.5, 1])
    axes[3, 0].set_xlabel("left ← lung box x → right", fontsize=8)
    for r in range(4):
        axes[r, 0].set_ylabel("inferior ← z → superior", fontsize=7.5)
    save(fig, "fig_spatial_train_vs_val", dpi=220)
    density_panels("lung_y", "posterior ← lung box y → anterior", "fig_spatial_sagittal",
                   "Sagittal density of train components in lung-box coordinates (per-panel scale)")


def hu(t: dict) -> None:
    f = t["findings"].dropna(subset=["hu_p50"])
    g = f.groupby("category", observed=False)
    rows = pd.DataFrame({"category": CATS, "name": [CATEGORY_MAP[k] for k in CATS], "findings": g.size().reindex(CATS).values,
                         "hu_p50_inside_median": g["hu_p50"].median().reindex(CATS).values, "hu_p05_inside_median": g["hu_p05"].median().reindex(CATS).values,
                         "hu_p95_inside_median": g["hu_p95"].median().reindex(CATS).values, "hu_shell_p50_median": g["hu_shell_p50"].median().reindex(CATS).values,
                         "hu_contrast_median": g["hu_contrast"].median().reindex(CATS).values, "hu_contrast_iqr": (g["hu_contrast"].quantile(0.75) - g["hu_contrast"].quantile(0.25)).reindex(CATS).values,
                         "findings_with_padding_in_mask": g["padding_voxels_in_mask"].apply(lambda v: (v > 0).sum()).reindex(CATS).values})
    table(rows, "hu")
    fig, ax = plt.subplots(figsize=(7.2, 5.2))
    y = np.arange(len(CATS))
    for ref, name in ((-1000, "air"), (-850, "aerated lung"), (0, "water")):
        ax.axvline(ref, color=GRID, linewidth=1); ax.text(ref, len(CATS) - 0.3, name, fontsize=7.5, color=INK2, ha="center", va="top")
    for yi, a, b in zip(y, rows["hu_shell_p50_median"], rows["hu_p50_inside_median"]):
        ax.plot([a, b], [yi, yi], color=GRID, linewidth=2, zorder=1)
    ax.scatter(rows["hu_shell_p50_median"], y, color=BLUE_RAMP[1], edgecolor=BLUE_RAMP[4], linewidth=0.6, s=30, zorder=2, label="3 mm shell around the mask")
    ax.scatter(rows["hu_p50_inside_median"], y, color=BLUE_RAMP[4], s=30, zorder=2, label="inside the mask")
    ax.set_yticks(y); ax.set_yticklabels([CAT_LABEL[k] for k in CATS]); ax.invert_yaxis(); ax.grid(axis="y", visible=False)
    ax.set_ylim(len(CATS) + 0.3, -0.7)
    ax.set_xlabel("median HU (median over findings of each finding's median)"); ax.legend(loc="upper right")
    save(fig, "fig_hu")


def text(t: dict) -> None:
    f = t["findings"]
    if "n_tokens" not in f.columns:
        print("  text: tables/text.csv missing, skipped", flush=True); return
    g = f.groupby("split")
    per_split = pd.DataFrame({"findings": g.size(), "words_median": g["n_words"].median(), "words_max": g["n_words"].max(),
                              "tokens_median": g["n_tokens"].median(), "tokens_p95": g["n_tokens"].quantile(0.95), "tokens_max": g["n_tokens"].max(),
                              "prompt_tokens_median": g["n_tokens_prompt"].median(), "prompt_tokens_max": g["n_tokens_prompt"].max(),
                              "over_128_prompt_tokens": g["n_tokens_prompt"].apply(lambda v: int((v > 128).sum())),
                              "laterality_bilateral_pct": g["laterality"].apply(lambda v: (v == "bilateral").mean() * 100),
                              "laterality_none_pct": g["laterality"].apply(lambda v: (v == "none").mean() * 100),
                              "mentions_lobe_pct": g["mentions_lobe"].mean() * 100, "mentions_segment_pct": g["mentions_segment"].mean() * 100,
                              "spatial_terms_mean": g["n_spatial_terms"].mean()}).reset_index()
    table(per_split, "text_splits")
    gc = f.groupby("category", observed=False)
    per_cat = pd.DataFrame({"category": CATS, "name": [CATEGORY_MAP[k] for k in CATS], "findings": gc.size().reindex(CATS).values,
                            "words_median": gc["n_words"].median().reindex(CATS).values, "tokens_median": gc["n_tokens"].median().reindex(CATS).values,
                            "bilateral_pct": gc["laterality"].apply(lambda v: (v == "bilateral").mean() * 100).reindex(CATS).values,
                            "no_laterality_pct": gc["laterality"].apply(lambda v: (v == "none").mean() * 100).reindex(CATS).values,
                            "mentions_lobe_pct": (gc["mentions_lobe"].mean() * 100).reindex(CATS).values,
                            "mentions_segment_pct": (gc["mentions_segment"].mean() * 100).reindex(CATS).values})
    table(per_cat, "text_categories")
    fig, ax = plt.subplots(figsize=(7.2, 3.4))
    bins = np.arange(0, f["n_tokens_prompt"].max() + 4, 3)
    for sp in ("train", "val", "test"):
        v = f[f.split == sp]["n_tokens_prompt"].dropna()
        if len(v):
            ax.hist(v, bins=bins, density=True, histtype="step", linewidth=1.6, color=SPLIT_COLOR[sp], label=f"{SPLIT_LABEL[sp]}, median {v.median():.0f}")
    ax.axvline(128, color=INK2, linewidth=0.8); ax.text(128, ax.get_ylim()[1] * 0.5, " encoder limit (128)", fontsize=7.5, color=INK2)
    ax.set_xlabel("tokens of the instruction prompt (Qwen3-Embedding tokenizer)"); ax.set_ylabel("density"); ax.legend(loc="upper right")
    save(fig, "fig_text_tokens")


def scans(t: dict) -> None:
    s = t["scans"]; g = s.groupby("split")
    rows = pd.DataFrame({"scans": g.size(), "spacing_xy_mm_median": g["spacing_x"].median(), "spacing_xy_mm_min": g["spacing_x"].min(), "spacing_xy_mm_max": g["spacing_x"].max(),
                         "spacing_z_mm_median": g["spacing_z"].median(), "spacing_z_mm_min": g["spacing_z"].min(), "spacing_z_mm_max": g["spacing_z"].max(),
                         "slices_median": g["shape_z"].median(), "slices_min": g["shape_z"].min(), "slices_max": g["shape_z"].max(),
                         "fov_z_mm_median": g["fov_z_mm"].median(), "padding_present_pct": g["padding_present"].mean() * 100,
                         "orientation_codes": g["orig_axcodes"].apply(lambda v: ",".join(f"{k}:{n}" for k, n in v.value_counts().items())),
                         "lobes_available_pct": g["lobes_available"].mean() * 100, "lung_volume_ml_median": g["lung_volume_ml"].median(),
                         "ct_min_median": g["ct_min"].median(), "body_p50_hu_median": g["body_p50_hu"].median()}).reset_index()
    table(rows, "scans")
    fig, axes = plt.subplots(1, 4, figsize=(12, 2.9))
    for ax, col, lab, bins in zip(axes, ["spacing_x", "spacing_z", "shape_z", "lung_volume_ml"],
                                  ["in-plane spacing (mm)", "slice spacing (mm)", "slices", "lung volume (ml)"],
                                  [np.linspace(0.4, 1.1, 29), np.linspace(0.4, 3.2, 29), np.linspace(50, 700, 27), np.linspace(1000, 9000, 33)]):
        for sp in ("train", "val", "test"):
            v = s[s.split == sp][col].dropna()
            if len(v):
                ax.hist(v, bins=bins, density=True, histtype="step", linewidth=1.4, color=SPLIT_COLOR[sp], label=sp)
        ax.set_xlabel(lab); ax.set_yticks([])
    axes[0].legend(loc="upper right")
    save(fig, "fig_scans")


def cooccurrence(t: dict) -> None:
    f = t["findings"]; s = t["scans"]
    pres = f.groupby(["id", "category"], observed=False).size().unstack(1).fillna(0) > 0
    pres = pres.reindex(columns=CATS)
    counts = pres.astype(int).T @ pres.astype(int)
    cond = counts.div(np.diag(counts.values), axis=0)
    table(counts.reset_index().rename(columns={"category": "row"}), "cooccurrence_counts")
    table(cond.reset_index().rename(columns={"category": "row"}), "cooccurrence_conditional")
    fig, ax = plt.subplots(figsize=(7.4, 6.4))
    im = ax.imshow(cond.values, cmap=matplotlib.colors.LinearSegmentedColormap.from_list("b", ["#ffffff"] + BLUE_RAMP), vmin=0, vmax=1)
    ax.set_xticks(range(len(CATS))); ax.set_xticklabels([CAT_SHORT[k] for k in CATS], rotation=45, ha="right", fontsize=7.5); ax.set_yticks(range(len(CATS))); ax.set_yticklabels([CAT_LABEL[k] for k in CATS]); ax.grid(False)
    for i in range(len(CATS)):
        for j in range(len(CATS)):
            v = cond.values[i, j]
            if i != j and v >= 0.15:
                ax.text(j, i, f"{v:.2f}", ha="center", va="center", fontsize=6.5, color="#ffffff" if v > 0.6 else INK)
    fig.colorbar(im, ax=ax, fraction=0.035, pad=0.02, label="P(column present | row present), scan level")
    save(fig, "fig_cooccurrence")
    pat = s.assign(patient=patient_id(s["id"])).groupby("split")["patient"].apply(set).reindex(["train", "val", "test"]).apply(lambda v: v if isinstance(v, set) else set())
    overlap = pd.DataFrame([{"pair": f"{a}-{b}", "shared_patients": len(pat[a] & pat[b])} for a, b in (("train", "val"), ("train", "test"), ("val", "test"))])
    table(overlap, "patient_overlap")


ANALYSES = {"splits": splits, "sizes": sizes, "spatial": spatial, "hu": hu, "text": text, "scans": scans, "cooccurrence": cooccurrence}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("which", nargs="*", default=list(ANALYSES))
    a = ap.parse_args()
    t = load()
    for name in a.which:
        print(f"== {name}", flush=True)
        ANALYSES[name](t)


if __name__ == "__main__":
    main()
