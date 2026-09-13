#!/bin/bash
# ==============================================================================
# SLURM JOB:      profiling/extract.slurm   (CPU only)
# OBJECTIVE:      Phase 1 extraction pass: every scan into tables/parts/*.jsonl (profiling/extract.py).
#                 Resumable: rerunning skips scans already measured.
# USAGE:          sbatch profiling/extract.slurm                                  # all 3,492 scans
#                 sbatch --export=ALL,START=0,END=3,WORKERS=1 profiling/extract.slurm   # smoke test
#                 then: .venv/bin/python -m profiling.extract --merge
# MEMORY:         one worker holds one CT (int16) plus one mask channel (uint8) plus crops: < 1.5 GB each.
# ==============================================================================
#SBATCH --job-name=p1_extract
#SBATCH -p batch
#SBATCH -q batch
#SBATCH --cpus-per-task=8
#SBATCH --mem=32G
#SBATCH -t 06:00:00
#SBATCH -o logs/slurm/extract_%j.out
#SBATCH -e logs/slurm/extract_%j.err
set -euo pipefail
# SLURM runs a copy of this script from its spool directory, so the repository is the submission directory
cd "${SLURM_SUBMIT_DIR:?submit this script from the repository root with sbatch}"
[ -f pyproject.toml ] || { echo "ERROR: $PWD is not the repository root"; exit 1; }
mkdir -p logs/slurm
WORKERS="${WORKERS:-$SLURM_CPUS_PER_TASK}"
ARGS=(--workers "$WORKERS")
[ -n "${START:-}" ] && ARGS+=(--start "$START")
[ -n "${END:-}" ] && ARGS+=(--end "$END")
echo "=== PHASE 1 EXTRACT: job $SLURM_JOB_ID, args ${ARGS[*]} ==="
.venv/bin/python -u -m profiling.extract "${ARGS[@]}"
echo "=== EXTRACT COMPLETE (exit $?) ==="
