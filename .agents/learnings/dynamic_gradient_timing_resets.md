# Dynamic Gradient Timing Resets & Discretization

This document explains the dynamic recalculation behavior of `STGradientMom` and how timing discretization affects gradient amplitudes in headless simulations.

---

## 1. Reset Behavior of `STGradientMom`

In theory, the `STGradientMom` class allows keeping a previously defined gradient shape if `always_min_dur` is set to `0`:
```cpp
double hold = ramp_times_1 / 2 + plateau_times + ramp_times_2 / 2;
if ((hold > 0) && (fabs(mom) / hold <= maxamp) && (!always_min_dur)) {
    amplitude = mom / hold; // Maintain shape
}
```

### The Catch
When the simulator runs a sequence, it recursively calls `initialize()` on all nodes. In `STGradientMom::initialize()`, the passive timing parameters are explicitly reset to zero:
```cpp
ramp_times_1 = Vector3(0,0,0);
plateau_times = Vector3(0,0,0);
ramp_times_2 = Vector3(0,0,0);
amplitude = Vector3(0,0,0);
```
Consequently, **any pre-computed passive times serialized in the `.sts` file's `NODES` section are ignored**. The simulator *always* falls back to recalculating the minimum-duration shape from scratch based on active `ramprate` and `maxamp` constraints.

---

## 2. Scanner Timing Discretization

When the minimum duration of a gradient (e.g., a triangular shim pulse) is calculated from the target moment and slew rate:
$$\text{ramp\_time} = \sqrt{\frac{\text{moment}}{\text{slew\_rate}}}$$

The simulator does not use this raw float value directly. It calls `scanner()->rounduptime(ramp_time)`, which rounds up the duration to the scanner hardware's time grid step (typically a multiple of $10\text{ }\mu\text{s}$ or $20\text{ }\mu\text{s}$):
* **Example (slew = 0.125):** 
  Target moment = $3914.53\text{ }\mu\text{T/mm}\cdot\mu\text{s}$
  Raw $\text{ramp\_time} = \sqrt{3914.53 / 0.125} \approx 176.96\text{ }\mu\text{s}$
  Scanner rounds up to **$180\text{ }\mu\text{s}$**.
  The final amplitude is then computed using the rounded ramp time:
  $$\text{amplitude} = \frac{3914.53}{180} = 21.7474\text{ }\mu\text{T/mm}$$

---

## 3. Best Practice: Targeted Waveform Auditing

For large sequences (e.g. 16,000 blocks), running a full simulation and parsing `sim.dat` will overflow the terminal stdout and truncate results. 

Instead of trying to dump everything, write a brief python wrapper in the agent workspace importing `parse_simulation_dat` from `agentic_coding/parse_sim_dat.py` and filtering for the specific block number and axes:
```python
from parse_sim_dat import parse_simulation_dat
blocks = parse_simulation_dat("sim.dat", verbose=False)
target_block = [b for b in blocks if b['block_num'] == 15999][0]
# Inspect event lists programmatically
```
