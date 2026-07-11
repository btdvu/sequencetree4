# Gradient Timing & Parameter Constraint Calculations

Notes on how global scanner limits (`maxamp`, `ramprate`) affect gradient durations, ramp-up times, and plateaus in simulations.

---

## 1. Calculating Minimum Ramp-Up Times
When gradients are simulated, the solver calculates the minimum time needed to reach a target area (moment) under the constraints of the scanner's maximum amplitude (`maxamp` in uT/mm) and maximum slew rate (`ramprate` in [uT/mm]/us):

* **Target Moment ($M$)**: The integral of the gradient amplitude over time:
  $$M = \int G(t) dt$$
* **Slew-Rate Constraint**: The slope of the gradient ramps cannot exceed `ramprate` ($S_r$):
  $$\frac{dG}{dt} \le S_r$$
* **Ramp Time ($T_{\text{ramp}}$)**: For a given amplitude ($A$), the ramp-up time is:
  $$T_{\text{ramp}} = \frac{A}{S_r}$$

---

## 2. Framework-Specific Rounding
The virtual scanner does not run on continuous time. All event durations are rounded up to the nearest multiple of the scanner's raster step time (typically $10\,\mu\text{s}$ or $50\,\mu\text{s}$):

* **Example (SPGR Prephase)**:
  * target amplitude: $23.1429\,\text{uT/mm}$
  * ramprate: $0.07\,\text{uT/mm/us}$
  * raw ramp time calculation:
    $$T_{\text{ramp}} = \frac{23.1429}{0.07} = 330.6\,\mu\text{s}$$
  * The simulator automatically rounds this up to the nearest raster step multiple, resulting in $T_{\text{ramp}} = 350\,\mu\text{s}$.

When optimizing parameters (like minimizing TR), agents must account for this rounding behavior to prevent timing gap overlaps or constraint errors.
