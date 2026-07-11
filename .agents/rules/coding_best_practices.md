# Coding Best Practices & C++ Build Rules

Guidelines to follow when writing C++ code inside `.sts` files.

## 1. Class Naming Constraints
* SequenceTree compiles custom classes dynamically by extracting them from the active `.sts` file and building them under `/simulator/`.
* **Rule**: Because the base framework code pulls implementations from the core directories, **do not overwrite classes built into the base installation** (such as `SPGRLoop`). Doing so will cause compile collisions.
* **Solution**: Always define uniquely named classes (e.g. `bSSFPPrepLoop`, `bSSFPLoop`, `bSSFP3EchoBlock`) inside the `.sts` file.

## 2. Stateful Methods and Resets
* **Rule**: Do not perform stateful resets or index increments inside the `prepare()` method.
* **Why**: `prepare()` is invoked recursively down the tree before every step and may be executed multiple times for sequence validation. Stateful logic must only reside inside:
  * `loopInitialize()`: Invoked exactly once when the loop starts (reset counters here).
  * `loopRun()`: Executes the block execution and updates iterative parameters.
