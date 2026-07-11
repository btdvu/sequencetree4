---
name: sequencetree-agentic-coding
description: Automation guide and rules for editing, simulating, and compiling MRI pulse sequences within the SequenceTree workspace without GUI interaction.
---

# SequenceTree Agentic Coding Skill

Use this skill when modifying, compiling, or simulating MRI pulse sequences headlessly.

## Workflow Instructions

1. **Check guidelines**: Read [`agentic_coding/README.md`](file:///home/brian/sequencetree4/agentic_coding/README.md) and the rules in `/.agents/rules/` before starting.

2. **Modify Sequence**: Edit the target `.sts` file inside `/agentic_coding/sequences/`.
   - Modify parameter values or formulas in the `++++++ GLOBAL ++++++` block.
   - Modify C++ source/header blocks inside `++++++ USERCLASS [ClassName] ++++++` sections.

3. **Simulate**: Run the **mandatory wrapper script** — never call `bin/simulator` directly:
   ```bash
   bash agentic_coding/simulate.sh check agentic_coding/sequences/your_sequence.sts
   ```
   The wrapper enforces three steps automatically:
   - **Step 1** — Recompiles `bin/simulator` if the `.sts` has custom C++ classes.
   - **Step 2** — Converts NODES parameters → flat PARAM format via `convert_sts_to_params.py`.
     > ⚠️ **This step is non-negotiable.** Passing a raw `.sts` directly to the simulator
     > causes it to silently use C++ constructor defaults (wrong nShots, dwell_time, etc.),
     > producing completely wrong waveforms with no error and exit code 0.
   - **Step 3** — Runs the simulator via `run_in_docker.sh`.

   Check that the script prints `ret=true`. If `ret=false`, there is a timing constraint violation.

4. **Parse Waveforms** (optional, for `run` mode): Use the canonical parser:
   ```bash
   bash agentic_coding/simulate.sh run agentic_coding/sequences/your_sequence.sts 0 0
   python3 agentic_coding/parse_sim_dat.py agentic_coding/sequences/your_sequence_sim.dat
   ```
   See [`/.agents/context/mri_simulation_formats.md`](file:///home/brian/sequencetree4/.agents/context/mri_simulation_formats.md) for the binary layout reference.

5. **Read Static Parameters**: For reading event parameters (durations, N, Tacq, etc.) from a
   GUI-designed sequence, read the **`.sts` NODES section directly** — it is the authoritative
   source. These passive parameters are computed by the GUI's `prepare()` and serialized there.
   No simulation run is needed for static parameter inspection.
