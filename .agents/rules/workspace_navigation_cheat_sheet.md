# Workspace Navigation & Framework Landmarks Cheat Sheet

This document serves as a quick-orientation map for AI agents newly spawned in this workspace. It highlights key landmarks in the codebase and covers common friction points that are not immediately obvious.

---

## 🔍 Where is the Code? (Core vs. Custom)

1. **Custom C++ Loops and Blocks**:
   * Custom sequence logic (e.g., `STRadialLoop_1`, `STGradientEchoBlock_4`) is **not** stored in the main `/code/` repository folders.
   * Instead, they are defined **inline** inside the active `.sts` sequence file under `++++++ CLASS [ClassName] ++++++` delimiters (containing both `++++++ HEADER` and `++++++ SOURCE` sub-blocks).
   * During compilation, the automated builder extracts these into `simulator/customclasses.h` and `simulator/customclasses.cpp` and compiles `bin/simulator`.
2. **Parameter Mappings**:
   * Relationships between global parameter names (seen in the GUI/header) and the target child variables in the sequence tree are defined in the `++++++ GLOBAL ++++++` section of the `.sts` file using `->` arrows.

---

## 🗺️ C++ Framework Landmarks

When analyzing timing, moments, or sequence logic, refer directly to these framework implementations:

* **[stnode.h](file:///home/brian/sequencetree4/code/framework/stnode.h) / [stnode.cpp](file:///home/brian/sequencetree4/code/framework/stnode.cpp)**:
  * Defines the core tree node structure.
  * Look here for basic node state, `prepare()`, `run()`, `initialMoment()`, and `terminalMoment()` ($=\text{initialMoment} + \text{totalGradientMoment}$).
* **[stsequence.h](file:///home/brian/sequencetree4/code/framework/stsequence.h) / [stsequence.cpp](file:///home/brian/sequencetree4/code/framework/stsequence.cpp)**:
  * Defines the tree root (`STSequence`).
  * Look here for `kspace2moment()` which converts k-space coordinates ($k_x, k_y, k_z$) to physical gradient moments ($u\text{T/mm}\cdot\mu\text{s}$) using the FOV and $\gamma$.
* **[stchain.h](file:///home/brian/sequencetree4/code/nodetypes/foundation/stchain.h) / [stchain.cpp](file:///home/brian/sequencetree4/code/nodetypes/foundation/stchain.cpp)**:
  * Base class for sequential chains of blocks (e.g. TR blocks).
  * Look here to see how start times are calculated via `ST_ALIGN` macros and how initial moments propagate sequentially down the chain from child `j` to `j+1`.
* **[stgradientmom.cpp](file:///home/brian/sequencetree4/code/nodetypes/foundation/stgradientmom.cpp)**:
  * Contains the math of trapezoidal and triangular shape computations in `setMoment()`.

---

## ⚠️ Common Pitfalls

1. **C++ Compilation Diagnostics**:
   * If `simulate.sh` re-compiles `bin/simulator` and fails, you can inspect the compilation logs or view the extracted stubs in `simulator/customclasses.h` and `simulator/customclasses.cpp` to locate syntax errors or missing class headers.
2. **Determining Block Index to Run**:
   * The simulator's block index parameter is a 0-indexed cumulative execution counter.
   * In multi-TR loops, calculate the absolute block index by tracing loop nest hierarchies. Running the wrong block index will produce incorrect waveform diagnostics in `sim.dat`.
