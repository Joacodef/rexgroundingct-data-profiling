"""
SCRIPT:         profiling/text.py
OBJECTIVE:      Token counts of every finding sentence with the tokenizer VoxTell's text encoder actually
                uses (Qwen/Qwen3-Embedding-4B), both for the bare sentence and for the instruction prompt the
                model is given. The old suite estimated tokens with a word-length heuristic; these are the
                real counts. Needs no volume and no GPU.

USAGE:          .venv/bin/python -m profiling.text            -> tables/text.csv (id, split, finding_idx, ...)
                The tokenizer is read from the local Hugging Face cache (HF_HOME, or the default
                ~/.cache/huggingface); pass --tokenizer-json to point at a tokenizer.json directly.

COLUMNS:        id, split, finding_idx, n_words, n_tokens (sentence alone), n_tokens_prompt (sentence inside
                VoxTell's instruction template), laterality (left / right / bilateral / none), mentions_lobe,
                mentions_segment, n_spatial_terms (count of anatomical locator words matched)
"""
from __future__ import annotations

import argparse
import csv
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from profiling.io import TABLES_DIR, dataset_entries  # noqa: E402

# The template VoxTell wraps every finding in (technical report, Phase 2B; scripts/common/precompute_text_embeddings.py
# of the training repository).
PROMPT = "Instruct: Given an anatomical term query, retrieve the precise anatomical entity and location it represents\n Query: {text}"
MODEL = "Qwen/Qwen3-Embedding-4B"
SPATIAL = [r"right", r"left", r"bilateral", r"upper lobe", r"lower lobe", r"middle lobe", r"lingula", r"apical", r"apex",
           r"basal", r"posterobasal", r"anterobasal", r"laterobasal", r"mediobasal", r"superior segment", r"medial segment",
           r"lateral segment", r"anterior segment", r"posterior segment", r"subpleural", r"peripheral", r"perihilar", r"hilar",
           r"paramediastinal", r"peribronchovascular", r"central", r"pleural", r"diaphragm", r"costophrenic", r"fissure"]
SPATIAL_RE = re.compile(r"\b(" + "|".join(SPATIAL) + r")\b", re.IGNORECASE)
LOBE_RE = re.compile(r"\b(upper|lower|middle) lobe\b|\blingula\b", re.IGNORECASE)
SEGMENT_RE = re.compile(r"\bsegment(s|al)?\b", re.IGNORECASE)


def find_tokenizer_json() -> Path | None:
    home = Path(os.getenv("HF_HOME") or Path.home() / ".cache" / "huggingface")
    snaps = home / "hub" / ("models--" + MODEL.replace("/", "--")) / "snapshots"
    if snaps.exists():
        for s in sorted(snaps.iterdir()):
            if (s / "tokenizer.json").exists():
                return s / "tokenizer.json"
    return None


def laterality(text: str) -> str:
    t = text.lower()
    if "bilateral" in t or "both lungs" in t or "both lung" in t:
        return "bilateral"
    left, right = bool(re.search(r"\bleft\b", t)), bool(re.search(r"\bright\b", t))
    if left and right:
        return "bilateral"
    return "left" if left else ("right" if right else "none")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--tokenizer-json", default=None)
    a = ap.parse_args()
    tok_path = Path(a.tokenizer_json) if a.tokenizer_json else find_tokenizer_json()
    tok = None
    if tok_path is not None:
        from tokenizers import Tokenizer
        tok = Tokenizer.from_file(str(tok_path))
        print(f"tokenizer: {tok_path}", flush=True)
    else:
        print("WARNING: tokenizer not found; n_tokens columns will be empty", flush=True)

    TABLES_DIR.mkdir(parents=True, exist_ok=True)
    out = TABLES_DIR / "text.csv"
    n = 0
    with open(out, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["id", "split", "finding_idx", "n_words", "n_tokens", "n_tokens_prompt", "laterality", "mentions_lobe", "mentions_segment", "n_spatial_terms"])
        for e in dataset_entries():
            for k, text in sorted(e.get("findings", {}).items(), key=lambda kv: int(kv[0])):
                nt = len(tok.encode(text, add_special_tokens=False).ids) if tok else ""
                npx = len(tok.encode(PROMPT.format(text=text), add_special_tokens=True).ids) if tok else ""
                w.writerow([e["id"], e["split"], int(k), len(text.split()), nt, npx, laterality(text),
                            int(bool(LOBE_RE.search(text))), int(bool(SEGMENT_RE.search(text))), len(SPATIAL_RE.findall(text))])
                n += 1
    print(f"{out}: {n:,} findings", flush=True)


if __name__ == "__main__":
    main()
