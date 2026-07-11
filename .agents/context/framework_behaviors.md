# Hidden C++ Framework Behaviors

Technical details regarding the C++ execution engine and base classes.

## 1. Loop Execution Order
The execution lifecycle of an `STLoop` subclass:
1. **`loopInitialize()`**: Invoked exactly once when the loop starts.
2. **`prepare()`**: Invoked recursively down the tree before every step.
3. **`loopRun()`**: Executes the child block (e.g., `Block->run()`) and updates iterative state.

## 2. Automatic Moment Balancing
* The foundation class `STEncode` (commonly named `Rewind`) balances gradient moments to zero.
* Its C++ implementation computes:
  $$\text{Gradient Moment} = -\mathbf{k}_{\text{accumulated}} + \mathbf{M}_{\text{target}}$$
* If the target parameter `moment` ($\mathbf{M}_{\text{target}}$) is set to `(0, 0, 0)`, `STEncode` automatically calculates the exact negative of the accumulated gradient area up to that point. This balances all three axes (X, Y, and Z) to zero, satisfying the bSSFP requirement.

## 3. Parameter Modification Propagation
* Assigning directly to node parameters (e.g., `Block->Excite->RF->flip_angle = value;`) invokes the `operator=` on `STReal`.
* This automatically sets a `m_is_modified = true` flag. The modification flag propagates recursively up to the root, prompting the simulator to run `prepare()` and re-generate the underlying RF/gradient shapes on the next TR step.

## 4. Alignment in `STChain`
* A block class that inherits from `STChain` aligns its children sequentially.
* The alignment macro `ST_ALIGN(ChildNode, AlignmentType, TimeOffset, RelativeIndex)` registers the timing:
  * `ST_ALIGN_LEFT` (1): Align relative to the start of the chain (or the end of the previous sibling).
  * `ST_ALIGN_RELATIVE` (4): Align relative to another child's reference time. The `RelativeIndex` corresponds to the child's index in the constructor array (e.g., `0` for `Excite` if it is the first registered child).
* **Multiple Readouts**: When designing a multi-echo sequence with $N$ readouts, they must all be aligned relative to the excitation pulse (`Excite`) using `ST_ALIGN_RELATIVE` with their respective echo times (`TE1`, `TE2`, `TE3`...).

---

## 5. Block Index Numbering

The simulator's block index is **cumulative across all loop iterations in the entire sequence**,
not per-loop. Blocks are numbered in the order they execute:

```
Block 0          → PrepLoop, iteration 1
Block 1          → PrepLoop, iteration 2
...
Block nPreps-1   → PrepLoop, last iteration
Block nPreps     → MainLoop, shot 0   ← first imaging TR
Block nPreps+1   → MainLoop, shot 1
...
```

To simulate a specific shot type, calculate its absolute block index from the loop structure.
Example: for a sequence with `nPreps=200` prep TRs and `nShots=64` spiral shots:
* First spiral shot = block **200**
* Last spiral shot  = block **263**
* CLI: `bash agentic_coding/simulate.sh run seq.sts 200 200`

---

## 6. Diagnosing `ret=false`

`ret=false` in the results file means one or more events violate timing constraints within their
parent block (TR). Common root causes, identifiable from `sim.dat` parse output:

| Symptom in `sim.dat` | Likely cause |
|---|---|
| `start_time` is large negative (e.g. −115,000 µs) | Acquire block overflows TR — readout is longer than `TR - TE` |
| Two events with identical or overlapping time ranges | Gradient overlap — concurrent events on the same axis |
| `duration` >> `TR` | A parameter (e.g. `Tacq`, `plateau_time`) was computed with wrong inputs — check param conversion was done |

If `ret=false` appears on the very first run with a sequence that previously worked in the GUI,
the most likely cause is missing param conversion (step 2 of `simulate.sh`).

---

## 7. `Gradient` vs `ArbGradient` in `sim.dat` — Binary Format Difference

Both event types write a gradient segment to `sim.dat` using the same byte structure
(`direction` + `num_times` + time/amp pairs). The **content** is different:

| Event type | What the time/amp pairs represent | Typical point count |
|---|---|---|
| `Gradient` (type 3) | Trapezoid **breakpoints** only | 4 pts (ramp-up, plateau ×2, ramp-down) |
| `ArbGradient` (type 4) | **Every waveform sample** at `timestep` intervals across the full gradient | `(ramp1 + plateau + ramp2) / timestep` |

For a spiral gradient with `plateau_time=3380 µs` and `timestep=10 µs`, expect
`(100 + 3380 + 200) / 10 = 368` points per axis — not 4. If you see 24,000+ points,
check whether param conversion was skipped (wrong `Tacq` → wrong `plateau_time`).
