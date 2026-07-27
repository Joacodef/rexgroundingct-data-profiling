"""
Centralized Configuration & Path Management for ReXGroundingCT.

This module provides a single source of truth for all dataset, model,
and log directories. Paths are dynamically computed relative to the project root,
with priority given to environment variable overrides (e.g., from local .env or cluster environments).
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# 1. Load local .env environment variables if present
load_dotenv(override=True)

# 2. Determine Repository Root Directory dynamically
# scripts/config.py -> parent is scripts/ -> parent is project root
ROOT_DIR = Path(__file__).resolve().parent.parent

# 3. Base Directory Definitions
DATA_DIR = ROOT_DIR / "data"
MODELS_DIR = ROOT_DIR / "models"
LOGS_DIR = ROOT_DIR / "logs"
SCRATCH_DIR = ROOT_DIR / "scratch"

# 4. Core Dataset & Asset Paths (Env Override -> Fallback to project relative default)
DATASET_JSON = Path(os.getenv("DATASET_JSON") or (DATA_DIR / "dataset.json"))
RAW_IMAGES_DIR = Path(os.getenv("IMG_RAW_DIR") or (DATA_DIR / "raw" / "images"))
RAW_MASKS_DIR = Path(os.getenv("SEG_RAW_DIR") or (DATA_DIR / "raw" / "segmentations"))
PREPROCESSED_DIR = Path(os.getenv("DATA_PREP_DIR") or (DATA_DIR / "preprocessed"))
PREDICTIONS_DIR = Path(os.getenv("DATA_PRED_DIR") or (DATA_DIR / "predictions"))
TEXT_CACHE_DIR = Path(os.getenv("TEXT_CACHE_DIR") or (DATA_DIR / "text_cache"))

# 5. Model & Checkpoint Paths
MODEL_DIR = Path(os.getenv("MODEL_DIR") or (MODELS_DIR / "voxtell_v1.1"))
CHECKPOINTS_DIR = Path(os.getenv("CHECKPOINTS_DIR") or (MODELS_DIR / "checkpoints"))

# 6. Temporary / Fast SSD Storage (Fallback to system /tmp)
TMP_PREP_DIR = Path(os.getenv("TMP_PREP_DIR") or "/tmp/rexgroundingct_preprocessed")

# 7. Hardware & Hardware Isolation Settings
DEFAULT_DEVICE = os.getenv("DEFAULT_DEVICE", "cuda:0")
CUDA_VISIBLE_DEVICES = os.getenv("CUDA_VISIBLE_DEVICES", "0")

# 8. Challenge 14-Category Definitions & Taxonomy
CATEGORY_MAP = {
    '1a': 'Bronchial wall thickening',
    '1b': 'Bronchiectasis',
    '1c': 'Emphysema',
    '1d': 'Septal thickening',
    '1e': 'Micronodules',
    '1f': 'Other non-focal',
    '2a': 'Linear opacities',
    '2b': 'Atelectasis / consolidation',
    '2c': 'Ground-glass opacity',
    '2d': 'Pulmonary nodules / masses',
    '2e': 'Pleural effusion / thickening',
    '2f': 'Honeycombing',
    '2g': 'Pneumothorax',
    '2h': 'Other focal'
}

NON_FOCAL_CATEGORIES = {'1a', '1b', '1c', '1d', '1e', '1f'}
FOCAL_CATEGORIES = {'2a', '2b', '2c', '2d', '2e', '2f', '2g', '2h'}
REVERSE_CATEGORY_MAP = {v: k for k, v in CATEGORY_MAP.items()}

