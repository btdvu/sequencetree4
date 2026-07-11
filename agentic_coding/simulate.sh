#!/bin/bash
# =============================================================================
# simulate.sh — Mandatory simulation pipeline for SequenceTree sequences.
#
# NEVER call bin/simulator directly. ALWAYS use this script.
# It enforces three required steps in order:
#   1. Recompile simulator for custom C++ classes (if ++++++ CLASS blocks present)
#   2. Convert NODES parameters → PARAM format  (prevents silent default fallback)
#   3. Run the simulator via Docker wrapper
#
# WHY step 2 is non-negotiable:
#   The simulator's loadParametersFromFile() does NOT understand the NODES section
#   PARAMETER syntax. Passing a raw .sts file causes it to silently use C++
#   constructor defaults (e.g. nShots=1, dwell_time=10us) — producing completely
#   wrong waveforms with exit code 0 and no error message.
#
# Usage:
#   agentic_coding/simulate.sh <mode> <path/to/sequence.sts> [min_block] [max_block]
#
# Arguments:
#   mode        : check | stat | run | raw_template
#   sequence    : path to .sts file (relative to workspace root)
#   min_block   : first block to simulate (default: -1 = all)
#   max_block   : last block to simulate  (default: -1 = all)
#
# Output files (written alongside the input .sts, never to /tmp):
#   <basename>_params.sts   — converted PARAM-format parameter file
#   <basename>_out.sts      — simulator output parameter snapshot
#   <basename>_results.txt  — results file (check ret=true here)
#   <basename>_sim.dat      — binary waveform data (mode=run)
#   <basename>_sim_raw.dat  — binary template data  (mode=raw_template)
#
# Parse sim.dat output:
#   python3 agentic_coding/parse_sim_dat.py <basename>_sim.dat
# =============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# --- Argument validation ---
if [ $# -lt 2 ]; then
    echo ""
    echo "Usage: agentic_coding/simulate.sh <mode> <path/to/sequence.sts> [min_block] [max_block]"
    echo "Modes: check | stat | run | raw_template"
    echo ""
    exit 1
fi

MODE="$1"
STS_FILE="$2"
MIN_BLOCK="${3:--1}"
MAX_BLOCK="${4:--1}"

if [[ ! "$MODE" =~ ^(check|stat|run|raw_template)$ ]]; then
    echo "ERROR: Unknown mode '$MODE'. Must be one of: check, stat, run, raw_template"
    exit 1
fi

cd "$WORKSPACE_ROOT"

if [ ! -f "$STS_FILE" ]; then
    echo "ERROR: Sequence file not found: $STS_FILE"
    exit 1
fi

# Derive output file paths from the input basename (all workspace-relative)
STS_BASENAME="${STS_FILE%.sts}"
PARAMS_FILE="${STS_BASENAME}_params.sts"
OUT_STS="${STS_BASENAME}_out.sts"
RESULTS_FILE="${STS_BASENAME}_results.txt"

if [ "$MODE" = "raw_template" ]; then
    SIM_DAT="${STS_BASENAME}_sim_raw.dat"
else
    SIM_DAT="${STS_BASENAME}_sim.dat"
fi

echo ""
echo "============================================================"
echo "  simulate.sh | mode=$MODE | blocks=$MIN_BLOCK:$MAX_BLOCK"
echo "  input : $STS_FILE"
echo "============================================================"

# --- Step 1: Recompile simulator if custom classes are present ---
echo ""
echo "--- Step 1/3: Check for custom C++ classes ---"
if grep -q "++++++.*CLASS" "$STS_FILE" 2>/dev/null; then
    echo "  Custom classes detected — recompiling simulator..."
    "$SCRIPT_DIR/run_in_docker.sh" python3 agentic_coding/extract_and_build.py "$STS_FILE"
    echo "  Recompile complete."
else
    echo "  No custom classes found — skipping recompile."
fi

# --- Step 2: Convert NODES parameters to PARAM format ---
echo ""
echo "--- Step 2/3: Convert NODES → PARAM format ---"
echo "  Input  : $STS_FILE"
echo "  Output : $PARAMS_FILE"
python3 agentic_coding/convert_sts_to_params.py "$STS_FILE" "$PARAMS_FILE"

# --- Step 3: Run simulator via Docker ---
echo ""
echo "--- Step 3/3: Run simulator ---"
"$SCRIPT_DIR/run_in_docker.sh" ./bin/simulator "$MODE" \
    "$PARAMS_FILE" "$OUT_STS" "$SIM_DAT" "$RESULTS_FILE" \
    "$MIN_BLOCK" "$MAX_BLOCK"

# --- Print results ---
echo ""
echo "============================================================"
echo "  Results"
echo "============================================================"
if [ -f "$RESULTS_FILE" ]; then
    cat "$RESULTS_FILE"
else
    echo "  WARNING: Results file not found: $RESULTS_FILE"
fi

echo ""
echo "Output files:"
echo "  Results : $RESULTS_FILE"
echo "  Params  : $PARAMS_FILE"
if [ "$MODE" = "run" ] || [ "$MODE" = "raw_template" ]; then
    echo "  Sim dat : $SIM_DAT"
    echo ""
    echo "Parse waveform data:"
    echo "  python3 agentic_coding/parse_sim_dat.py $SIM_DAT"
fi
echo ""
