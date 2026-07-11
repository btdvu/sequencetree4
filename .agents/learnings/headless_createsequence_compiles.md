# Headless compilation & Simulator Build Issues

Post-mortem record detailing compilation failures when generating simulator files headlessly, and the implemented solution.

---

## 1. The Problem
When the SequenceTree graphical IDE (`st4`) builds custom classes from a `.sts` file, it automatically parses the node declarations and writes sequence-specific overrides to:
* `/simulator/createsequence.cpp`
* `/simulator/loadparametersfile.cpp`

If you attempt to compile a sequence containing custom classes (e.g. `/sequences/triple_echo_bssfp_gemini_ai.sts`) headlessly by only generating `customclasses.cpp` and `customclasses.h`, the compilation fails because `createsequence.cpp` contains static node promotions (e.g., `STGaussianRF`) or structural layouts from previous sequences that the new sequence does not define.

---

## 2. The Solution
To bypass the need to run the GUI code generator headlessly, the builder script [/agentic_coding/extract_and_build.py](file:///agentic_coding/extract_and_build.py) has been updated to overwrite these files with clean stub files before building:

### Stub `createsequence.cpp`
* Creates a clean sequence instanced as `Root = new STRoot` (since the sequence root is universally named `STRoot` in SequenceTree).
* Removes all hardcoded node promotion paths (e.g. `Root->Loop1->Block->Excite`).
* Simply loads parameters from the input command-line file path (`parameter_fname`).

### Stub `loadparametersfile.cpp`
* Replaces the binary parameter array with a dummy function that returns an empty string (`ret = ""`).
* Since the CLI simulator always receives `parameter_fname` via `argv[2]`, the static default loading branch is never executed, making the stub completely safe.

## 3. How to Use
Always use the wrapper script to compile any custom classes defined in a sequence `.sts` file:
```bash
python3 /agentic_coding/extract_and_build.py /sequences/your_sequence.sts
```
This guarantees a clean, compile-ready `/simulator/` directory and generates a fresh sequence-specific `/bin/simulator` executable.
