# Parameter Loading Gotchas & Fallbacks

Record of silent framework fallbacks when simulating sequences, and how to avoid them using parameter conversion.

---

## 1. Silent Parameter Fallbacks
When invoking the `simulator` executable:
```bash
# General CLI Syntax
./bin/simulator stat [input_params.sts] [output_params.sts] [sim_output.dat] [results.txt] -1 -1
```
* **Format Mismatch**: The `.sts` files store parameters under the `++++++ NODES ++++++` section using the `PARAMETER [Type] [Name] [Value]` syntax.
* **The Parser Bug**: The C++ simulator loader `loadParametersFromFile` specifically expects the flat runtime format `PARAM [Name] [Value]`. If you pass a raw `.sts` file directly as the input parameter file, the parser cannot parse it.
* **The Silent Failure**: Instead of throwing an error or exiting, the simulator silently falls back to the default values initialized in the C++ node class constructors (e.g. defaulting PE1 to `0:1:0` instead of `-128:1:127`).

---

## 2. Solution: Pre-conversion Script
To avoid running simulations with default C++ values, you must convert the `.sts` parameter layout to the `PARAM` format first using the utility script [/agentic_coding/convert_sts_to_params.py](file:///agentic_coding/convert_sts_to_params.py):

```bash
# 1. Convert the parameter tree to PARAM format
python3 /agentic_coding/convert_sts_to_params.py /sequences/your_sequence.sts /tmp/your_sequence_in.sts

# 2. Run simulation passing the converted file
/agentic_coding/run_in_docker.sh ./bin/simulator stat /tmp/your_sequence_in.sts /tmp/your_sequence_out.sts /tmp/your_sequence_sim.dat /tmp/your_sequence_results.txt -1 -1
```
This guarantees that loop iteration bounds, TE/TR settings, and spoiler moments are loaded correctly.

---

## 3. Do NOT Run the Simulator Without Param Conversion — Use the NODES Section Instead

For reading **static event parameters** (durations, amplitudes, N, dwell_time, Tacq, etc.) of a GUI-designed sequence, the **`.sts` NODES section is the authoritative source**. These passive parameters are computed by the GUI's `prepare()` and serialized directly into the NODES block. Reading them from the file is always correct and never requires a simulation run.

> **CRITICAL**: Running `simulator run` or `simulator check` on a raw `.sts` file (without prior param conversion) will silently use C++ constructor default values for all active parameters (e.g. `nShots=1`, `dwell_time=10`, `matrix_size=256`). This causes wildly wrong waveforms (e.g. spiral `Tacq` computing to 245 ms instead of 3.4 ms) while still succeeding with exit code 0.

**Correct strategy by use case:**

| Goal | Method |
|---|---|
| Read event parameters (duration, N, Tacq, etc.) | Parse `.sts` NODES section directly |
| Validate timing constraints (`ret=true/false`) | Convert params first, then run `simulator check` |
| Observe per-shot waveform variation | Convert params first, then run `simulator run` on target block |
| Compile custom C++ classes | Use `extract_and_build.py` (does not affect param loading) |
