#!/bin/bash

# Pipeline orchestrator to sequentially run Phase 1 experiments once current task PID 2097800 completes.

TARGET_PID=2097800
PYTHON_BIN=".venv-voxtell/bin/python"
LOG_FILE="logs/execution_raw/phase1_pipeline.log"

mkdir -p logs/execution_raw

echo "[$(date)] Waiting for process PID ${TARGET_PID} (HU profiling exp_004) to complete..." >> "${LOG_FILE}"

while kill -0 ${TARGET_PID} 2>/dev/null; do
    sleep 15
done

echo "[$(date)] PID ${TARGET_PID} finished. Starting automated Phase 1 sequence..." >> "${LOG_FILE}"

# Step 1: Run experiment_005 (Structural Spacing & Co-occurrence)
echo "[$(date)] Launching experiment_005_structural_cooccurrence.py..." >> "${LOG_FILE}"
${PYTHON_BIN} scripts/data_analysis/experiment_005_structural_cooccurrence.py >> "${LOG_FILE}" 2>&1

# Step 2: Run experiment_006 (PU Noise & Inter-Class Overlap)
echo "[$(date)] Launching experiment_006_pu_overlap.py..." >> "${LOG_FILE}"
${PYTHON_BIN} scripts/data_analysis/experiment_006_pu_overlap.py >> "${LOG_FILE}" 2>&1

# Step 3: Run experiment_007 (Text-Spatial Alignment)
echo "[$(date)] Launching experiment_007_text_spatial_alignment.py..." >> "${LOG_FILE}"
${PYTHON_BIN} scripts/data_analysis/experiment_007_text_spatial_alignment.py >> "${LOG_FILE}" 2>&1

# Step 4: Run experiment_008 (Morphology & FOV)
echo "[$(date)] Launching experiment_008_morphology_fov.py..." >> "${LOG_FILE}"
${PYTHON_BIN} scripts/data_analysis/experiment_008_morphology_fov.py >> "${LOG_FILE}" 2>&1

echo "[$(date)] Phase 1 automated profiling sequence completed successfully!" >> "${LOG_FILE}"
