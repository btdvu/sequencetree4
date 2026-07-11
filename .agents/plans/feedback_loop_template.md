# Closed Optimization Feedback Loop Template

Use this plan to automatically edit, compile, simulate, and verify MRI sequences.

---

## The Workflow Plan

### 1. Goal Specification
Define target timing constraint parameters, limits (e.g., maximum slew rate, physical gradient amplitude constraints), and sequence metrics (e.g., minimal TR, target TE range, target flip angles).

### 2. Synthesis (Modify `.sts` file)
* Read the target `.sts` file from `/sequences/`.
* Write changes (such as parameter adjustments in `++++++ GLOBAL` or C++ logic changes inside `++++++ USERCLASS`) directly to the `.sts` file.

### 3. Compilation
* If C++ custom classes were modified, run the compiler:
  ```bash
  python3 /agentic_coding/extract_and_build.py /sequences/your_sequence.sts
  ```
* If compile errors occur, capture stderr and return to **Step 2** to fix the syntax.

### 4. Headless Simulation
* Run the validation checks first:
  ```bash
  ./bin/simulator check /sequences/your_sequence.sts /tmp/out.sts /tmp/sim.dat /tmp/results_check.txt -1 -1
  ```
* Check for timing overlaps or parameter constraint failures in the console output or `/tmp/results_check.txt` (`ret=false`).

### 5. Waveform Analysis
* Run full Bloch simulations and extract output metrics:
  ```bash
  ./bin/simulator run /sequences/your_sequence.sts /tmp/out.sts /tmp/sim.dat /tmp/results_run.txt -1 -1
  ```
* Execute a parsing script to decode the gradient, RF, and ADC details from `/tmp/sim.dat`.
* Graph or calculate sequence correctness (e.g., verify that the net area of Z-gradients is zero for bSSFP).

### 6. Correction & Optimization Loop
* If timing checks failed or waveforms are physically invalid: adjust parameters or change class logic inside the `.sts` file and repeat the cycle.
* Once the sequence is validated (`ret=true`) and performance matches expectations: export the final validated `.sts` file.
