# Sequence Compilation & Simulation Rules

Guidelines for compiling and simulating sequences headlessly.

---

## ⛔ THE ONE RULE: Never Call `bin/simulator` Directly

Always use the mandatory wrapper script instead:

```bash
bash agentic_coding/simulate.sh <mode> agentic_coding/sequences/your_sequence.sts [min_block] [max_block]
```

### Choosing the right mode

| Goal | Mode | Output to check |
|---|---|---|
| Validate timing (does sequence fit in TR?) | `check` | `ret=true` in results file |
| Get total duration, SAR, block count | `stat` | `duration=`, `SAR=`, `num_blocks=` in results file |
| Inspect RF/gradient/ADC waveforms | `run` | Parse `_sim.dat` with `parse_sim_dat.py` |
| Debug loop iteration / ADC index logic | `raw_template` | Parse `_sim_raw.dat` with `parse_sim_dat.py raw` |

> For **reading static parameters** (durations, N, Tacq) from a GUI-designed sequence,
> read the `.sts` NODES section directly — no simulation mode is needed.

The wrapper enforces three steps automatically and writes all output files to the workspace
(never to `/tmp`, which is ephemeral inside Docker). See below for what each step does.

---

## Step 1 — Recompile Custom Classes (if needed)

The wrapper detects whether the `.sts` file contains `++++++ CLASS` blocks. If so, it runs:

```bash
python3 agentic_coding/extract_and_build.py agentic_coding/sequences/your_sequence.sts
```

This regenerates `simulator/customclasses.h`, `simulator/customclasses.cpp`, and clean stubs
for `createsequence.cpp` / `loadparametersfile.cpp`, then recompiles `bin/simulator`.

> If the sequence uses only built-in foundation classes, this step is skipped automatically.

---

## Step 2 — Convert NODES Parameters to PARAM Format

> **CRITICAL — Never skip this step.**

The simulator's `loadParametersFromFile()` does **not** understand the NODES section's
`PARAMETER Type Name Value` syntax. It expects a flat `PARAM Name Value` format.

**If a raw `.sts` file is passed directly**, the simulator silently falls back to C++ constructor
defaults for all parameters — wrong `nShots`, wrong `dwell_time`, wrong `TR` — while
still exiting with code 0 and printing no error. This is the most dangerous failure mode
in the headless workflow.

The wrapper converts automatically:

```bash
python3 agentic_coding/convert_sts_to_params.py \
    agentic_coding/sequences/your_sequence.sts \
    agentic_coding/sequences/your_sequence_params.sts
```

---

## Step 3 — Run Simulator via Docker

The wrapper passes the **converted** `_params.sts` file (never the raw `.sts`) to the simulator:

```bash
agentic_coding/run_in_docker.sh ./bin/simulator <mode> \
    agentic_coding/sequences/your_sequence_params.sts \
    agentic_coding/sequences/your_sequence_out.sts \
    agentic_coding/sequences/your_sequence_sim.dat \
    agentic_coding/sequences/your_sequence_results.txt \
    <min_block> <max_block>
```

> All output files are written to the same directory as the input `.sts` — never to `/tmp`.
> Files written to `/tmp` inside Docker are lost when the container exits.

---

## Reading Results

The wrapper automatically prints the results file. Look for:
- `ret=true` — sequence passes all timing constraint checks ✅
- `ret=false` — timing constraint violation; inspect overlapping events ❌

---

## Parsing Waveform Output (`run` mode)

```bash
bash agentic_coding/simulate.sh run agentic_coding/sequences/your_sequence.sts 0 0
python3 agentic_coding/parse_sim_dat.py agentic_coding/sequences/your_sequence_sim.dat
```

See [`/.agents/context/mri_simulation_formats.md`](file:///home/brian/sequencetree4/.agents/context/mri_simulation_formats.md)
for the full binary layout reference and the `parse_simulation_dat()` / `parse_raw_template()` API.

---

## Static Parameter Inspection (No Simulation Needed)

For reading event parameters (durations, amplitudes, N, Tacq, dwell_time) from a GUI-designed
sequence, **read the `.sts` NODES section directly**. The passive parameters stored there are
the authoritative values computed by the GUI's `prepare()`. No simulation run is needed.
