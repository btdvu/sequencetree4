# Sequence Coding Troubleshooting & Tips

A log of general debugging tips and gotchas discovered in SequenceTree C++ sequence development.

---

## 1. Vector3 Operations
* The `Vector3` class has `operator*` defined for `double` but **not** for `int`.
* **Issue**: Reversing a readout gradient vector or multiplying by a scalar integer (e.g. `Vector3 * -1`) fails at compile time with type matching errors.
* **Fix**: Always multiply by a double literal: `Vector3 * (-1.0)`.

## 2. ADC Index Assignment
* SequenceTree assigns ADC channels (`ADC1.mda`, `ADC2.mda`, etc.) by recursively traversing the tree hierarchy.
* **Tip**: Adding three `STAcquire` nodes in a chain automatically maps raw data to `ADC1.mda`, `ADC2.mda`, and `ADC3.mda` sequentially in the viewer.

## 3. GUI Synchronization
* **Issue**: If you modify the `.sts` file externally (in a text editor or headlessly via python scripts), the Qt5 GUI application (`st4`) may fail to detect parameter changes if it is currently open.
* **Fix**: Close the SequenceTree GUI before making file edits, then reopen it to force a full XML/parameter synchronization.
