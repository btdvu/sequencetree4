# learnings Directory

Welcome, AI Agent!

This directory acts as our long-term memory bank, documenting post-mortems of solved compilation bugs, logic issues, and workarounds:
* Check [headless_createsequence_compiles.md](file:///home/brian/sequencetree4/.agents/learnings/headless_createsequence_compiles.md) for how the simulator compilation errors were solved headlessly using createsequence and loadparameters stubs.
* Check [parameter_file_conversions.md](file:///home/brian/sequencetree4/.agents/learnings/parameter_file_conversions.md) for details on silent parameter fallbacks and how to convert `.sts` nodes to valid `PARAM` files.
* Check [gradient_timing_calculations.md](file:///home/brian/sequencetree4/.agents/learnings/gradient_timing_calculations.md) for notes on how maximum amplitudes and slew rates calculate gradient ramps and plateau constraints.
* Check [dynamic_gradient_timing_resets.md](file:///home/brian/sequencetree4/.agents/learnings/dynamic_gradient_timing_resets.md) for notes on `STGradientMom` timing resets and timing discretization.
* Check [parse_blocks.py](file:///home/brian/sequencetree4/agentic_coding/parse_blocks.py) for a CLI utility that parses and isolates event waveforms for specific blocks or axes.

If you solve a new bug or discover a new workaround during your execution, document it in a new file in this directory to persist the knowledge for future agents.

## Rule Reminder:
You are only allowed to edit/write files within the `/.agents/` or `/agentic_coding/` directories (except for modifying sequence definitions under `/sequences/`).
