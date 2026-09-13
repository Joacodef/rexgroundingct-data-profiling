"""
MODULE:         profiling/io.py
OBJECTIVE:      Paths and the one correct way to load a ReXGroundingCT scan for measurement.

                The raw CT volumes are stored LPS with a real affine and real spacing; the 4D ground-truth
                masks (F, X, Y, Z) carry an IDENTITY affine and unit zooms. The old profiling suite measured
                HU on masks that were not reoriented with their CT and reported voxel units as millimetres
                (AUDIT_2026-09-12.md). The rule here, the same "Universal Mask Policy"
                the training repository uses: a mask takes its parent CT's affine BEFORE any reorientation,
                both are brought to RAS together, and spacing always comes from the CT header.

PATHS:          read from the environment (a .env file at the repository root is loaded if present):
                DATA_DIR (holds dataset.json, raw/images, raw/segmentations), LOBES_DIR (TotalSegmentator
                lobe masks named <scan>.nii.gz, labels 1-5; produced by the training repository's Phase 5
                stage 1a), TABLES_DIR (default: <repo>/tables).
"""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Dict, Iterator, List, Optional, Tuple

import nibabel as nib
import numpy as np

try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).resolve().parents[1] / ".env", override=False)
except ImportError:                                                   # dotenv is optional
    pass

REPO = Path(__file__).resolve().parents[1]
DATA_DIR = Path(os.getenv("DATA_DIR") or (REPO.parent / "data"))
DATASET_JSON = Path(os.getenv("DATASET_JSON") or (DATA_DIR / "dataset.json"))
RAW_IMAGES_DIR = Path(os.getenv("IMG_RAW_DIR") or (DATA_DIR / "raw" / "images"))
RAW_MASKS_DIR = Path(os.getenv("SEG_RAW_DIR") or (DATA_DIR / "raw" / "segmentations"))
LOBES_DIR = Path(os.getenv("LOBES_DIR") or (DATA_DIR / "lobes"))
TABLES_DIR = Path(os.getenv("TABLES_DIR") or (REPO / "tables"))

CATEGORY_MAP: Dict[str, str] = {
    "1a": "Bronchial wall thickening", "1b": "Bronchiectasis", "1c": "Emphysema", "1d": "Septal thickening",
    "1e": "Micronodules", "1f": "Other non-focal",
    "2a": "Linear opacities", "2b": "Atelectasis / consolidation", "2c": "Ground-glass opacity",
    "2d": "Pulmonary nodules / masses", "2e": "Pleural effusion / thickening", "2f": "Honeycombing",
    "2g": "Pneumothorax", "2h": "Other focal",
}
NON_FOCAL = {c for c in CATEGORY_MAP if c.startswith("1")}
FOCAL = {c for c in CATEGORY_MAP if c.startswith("2")}
LOBE_NAMES = {1: "LUL", 2: "LLL", 3: "RUL", 4: "RML", 5: "RLL"}   # TotalSegmentator lung_upper_lobe_left ... lung_lower_lobe_right
PADDING_HU = -2048.0                                                 # anything at or below this is out-of-FOV padding (the corrected volumes use -8192)


def dataset_entries() -> List[dict]:
    """Every entry of dataset.json with its split attached, in file order (train, val, test)."""
    with open(DATASET_JSON) as fh:
        ds = json.load(fh)
    out = []
    for split in ("train", "val", "test"):
        for e in ds.get(split, []):
            e = dict(e); e["split"] = split; e["id"] = e["name"].replace(".nii.gz", "")
            out.append(e)
    return out


def load_ct(path: Path) -> Tuple[np.ndarray, np.ndarray, str, np.ndarray]:
    """
    Signature:
        load_ct(path: Path) -> tuple[np.ndarray, np.ndarray, str, np.ndarray]
    Objective:
        Load a CT in RAS voxel order without converting it to float64.
    Inputs:
        path (Path): NIfTI file.
    Outputs:
        tuple: (volume in RAS (X, Y, Z), spacing in mm after reorientation, original axis codes such as
        "LPS", the original affine). Values are Hounsfield units; scl_slope/inter are applied by nibabel
        when present, otherwise the stored int16 is returned as is.
    """
    img = nib.load(str(path))
    axcodes = "".join(nib.aff2axcodes(img.affine))
    can = nib.as_closest_canonical(img)
    vol = np.asarray(can.dataobj)
    return vol, np.asarray(can.header.get_zooms()[:3], dtype=float), axcodes, img.affine


def mask_channels(path: Path, ct_affine: np.ndarray) -> Iterator[Tuple[int, np.ndarray]]:
    """
    Signature:
        mask_channels(path: Path, ct_affine: np.ndarray) -> Iterator[tuple[int, np.ndarray]]
    Objective:
        Yield each finding channel of a 4D ground-truth mask as a RAS uint8 array aligned with load_ct's
        output. The mask's own (identity) affine is ignored: the parent CT's affine is attached to every
        channel before canonicalization, which is what makes voxel (i, j, k) of the mask correspond to
        voxel (i, j, k) of the CT.
    Inputs:
        path (Path): 4D mask, (F, X, Y, Z), instance-labelled (0 = background, k = instance k).
        ct_affine (np.ndarray): the parent CT's affine, from load_ct.
    Outputs:
        Iterator of (finding index, RAS array (X, Y, Z) uint8).
    """
    img = nib.load(str(path))
    data = np.asarray(img.dataobj)
    if data.ndim == 3:
        data = data[None]
    for f in range(data.shape[0]):
        chan = nib.as_closest_canonical(nib.Nifti1Image(data[f].astype(np.uint8), ct_affine))
        yield f, np.asarray(chan.dataobj).astype(np.uint8)


def load_lobes(scan_id: str, ct_affine: Optional[np.ndarray] = None) -> Optional[np.ndarray]:
    """TotalSegmentator lobe labels (1-5) in RAS, or None when no mask is cached for the scan.
    The cached lobe files carry a real affine; if one ever carries an identity affine the CT's is used."""
    p = LOBES_DIR / f"{scan_id}.nii.gz"
    if not p.exists():
        return None
    img = nib.load(str(p))
    if ct_affine is not None and np.allclose(img.affine, np.eye(4)):
        img = nib.Nifti1Image(np.asarray(img.dataobj), ct_affine)
    return np.asarray(nib.as_closest_canonical(img).dataobj).astype(np.uint8)
