# agentic_coding Directory

Welcome, AI Agent!

> ⚠️ **Before running any simulation: use `simulate.sh`, never `bin/simulator` directly.**
> See the rules in `/.agents/rules/compilation_and_simulation.md` for why this matters.

This directory is a visible execution hub containing automation scripts and utilities:

* **[simulate.sh](file:///home/brian/sequencetree4/agentic_coding/simulate.sh)**: **Mandatory simulation wrapper.** Enforces all three required pre-simulation steps (recompile → param convert → Docker run) in the correct order. Always use this instead of calling `bin/simulator` directly.
* **[extract_and_build.py](file:///home/brian/sequencetree4/agentic_coding/extract_and_build.py)**: Headless parser and compiler for custom C++ classes inside `.sts` files. Called automatically by `simulate.sh` — only invoke directly if you need to recompile without running a simulation.
* **[convert_sts_to_params.py](file:///home/brian/sequencetree4/agentic_coding/convert_sts_to_params.py)**: Converts `.sts` NODES section parameters to the flat `PARAM` format the simulator loader requires. Called automatically by `simulate.sh` — never pass a raw `.sts` file directly to the simulator.
* **[parse_sim_dat.py](file:///home/brian/sequencetree4/agentic_coding/parse_sim_dat.py)**: Canonical parser for `sim.dat` and `sim_raw.dat` binary output files. Import or run directly. See `/.agents/context/mri_simulation_formats.md` for the binary layout reference.
* **[clean_unused_classes.py](file:///home/brian/sequencetree4/agentic_coding/clean_unused_classes.py)**: Recursive reachability analyzer that prunes unused C++ class definitions from `.sts` files.
* **[run_in_docker.sh](file:///home/brian/sequencetree4/agentic_coding/run_in_docker.sh)**: Low-level Docker container wrapper. Called automatically by `simulate.sh` — prefer the wrapper over calling this directly for simulation tasks.

Refer to `/.agents/` for rules, context definitions, learnings, and plan templates.

## Rule Reminder:
You are only allowed to edit/write files within the `/.agents/` or `/agentic_coding/` directories (except for modifying sequence definitions under `/sequences/`).
