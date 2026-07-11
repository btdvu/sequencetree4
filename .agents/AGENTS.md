# Workspace Rules for SequenceTree AI Agents

When working in this SequenceTree workspace, you must adhere to the following rules:

1. **Knowledge & Context**: Refer to the subdirectories in `/.agents/` for specific task details:
   - `/.agents/rules/`: Coding, compile, and simulator guidelines.
   - `/.agents/context/`: Binary output format maps and copy-pasteable parsing scripts.
   - `/.agents/learnings/`: Post-mortems, solved bugs, and workarounds.
   - `/.agents/plans/`: Workflow templates and optimization roadmaps.
2. **Core Directory Immutability**: Under no circumstances should you edit `.cpp` or `.h` files inside:
   * `/code/`
   * `/simulator/`
   * `/src/`
   * `/templates/`
3. **Sequence Customization (Agent Space Only)**: Custom loops, blocks, parameters, and sequence trees must be written entirely inside `.sts` files. Agents must only create and modify sequence files within the `/agentic_coding/sequences/` directory. Agents are strictly prohibited from writing or editing files inside the main `/sequences/` directory (which is reserved for human manual development), though they are free to read or copy files from it.
4. **Headless Compilation**: If custom C++ class definitions in the `.sts` file are modified, `simulate.sh` (Rule 5) handles recompilation automatically. Do NOT call `extract_and_build.py` or `bin/simulator` directly.
5. **Headless Verification**: Always verify sequence changes using the mandatory simulation wrapper — never call `bin/simulator` directly:
   ```bash
   bash agentic_coding/simulate.sh <mode> agentic_coding/sequences/your_sequence.sts [min_block] [max_block]
   ```
   This wrapper enforces three required steps in order: (1) recompile custom classes, (2) convert NODES → PARAM format, (3) run simulator via Docker. Skipping any step — especially step 2 — causes silent parameter fallback to C++ constructor defaults, producing completely wrong waveforms with no error. Check `ret=true` in the results file printed by the script.
6. **File Write Constraints**: Agents should only create or write files (e.g. temporary scripts, plans, logs, results, and sequence `.sts` files) within the `/.agents/` or `/agentic_coding/` directories. Never write files directly to the root, `/code/`, `/src/`, or other repository folders.
7. **Workspace Root-Relative Paths**: Always refer to file paths and directory paths relative to the root of the project (e.g., use `/.agents/` or `/agentic_coding/` instead of absolute paths like `/home/brian/sequencetree4/.agents/`).
8. **Workspace Housekeeping**: Agents must proactively maintain, clean, and organize the `/.agents/` and `/agentic_coding/` directories. Keep documentation concise, readable, and non-redundant to ensure a smooth transition for concurrent or future agents starting with empty memory banks.
9. **Thinking Partner / Strategic Pushback**: Do not just blindly follow user instructions. You are a pair-programming thinking partner. If you identify a more efficient, mathematically correct, or performant strategy for pulse sequence design or C++ architecture, explain the trade-offs and push back on the user's proposed direction with a better alternative.
10. **Prioritize Docker Execution**: Whenever running compiled binaries (like `simulator`), agents must prioritize running those commands through the Docker container wrapper (`/agentic_coding/run_in_docker.sh`) to ensure execution stability, network safety, and independent dependencies.
