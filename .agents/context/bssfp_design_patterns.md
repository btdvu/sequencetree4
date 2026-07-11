# Advanced bSSFP Sequence Design Patterns

Details on the implementation strategies used in the triple-echo bSSFP sequence:

## 1. Phase Alternation
* bSSFP requires the RF excitation phase to alternate by $180^\circ$ on successive repetition times (TRs).
* **Implementation**:
  1. Add a global tracking integer (e.g., `global_tr_count`) inside `STRoot`.
  2. Reset it in `STRoot::loopInitialize()`.
  3. In both the prep loop and main loop's `loopRun()`, update the sequence phase shift:
     ```cpp
     sequence()->phase_shift = (seq->global_tr_count % 2) * 180;
     seq->global_tr_count++;
     ```
  4. The framework automatically applies `sequence()->phase_shift` to both the transmit RF pulses and the receiver ADC channels in lockstep.

## 2. Catalyzation / Linear Ramp Preparation
* To speed up convergence to the steady state, include a preparatory loop (`bSSFPPrepLoop`) with $N$ steps (typically 10) before the imaging loop.
* Linearly scale the flip angle from $0^\circ$ to the target flip angle:
  ```cpp
  double fraction = (double)(PE1.stepNumber() + 1) / (double)PE1.numSteps();
  Block->Excite->RF->flip_angle = m_target_flip_angle * fraction;
  ```

## 3. Minimizing TR (Gradient Combination)
* To achieve the shortest possible TR in bSSFP, the slice-selection refocusing gradient at the start of a TR can be combined with the rewind gradient at the end of the TR.
* **Steps**:
  1. Disable the excitation refocusing gradient in the custom block:
     ```cpp
     Excite->prephase = 0; // Reduces Prephase node duration to 0
     ```
  2. Calculate the required Z refocusing moment:
     $$M_z = -G_{z,\text{excite}} \cdot \left(\frac{T_{\text{ramp}}}{2} + T_{\text{ref\_RF}}\right)$$
  3. Assign this target moment directly to the TR-ending `Rewind` block:
     ```cpp
     double effective_time_before_excite = Excite->SliceGradient->ramp_time_1 * 0.5 + Excite->RF->referenceTime();
     double z_excite_prephase_moment = -Excite->SliceGradient->amplitude.z() * effective_time_before_excite;
     Rewind->moment = Vector3(0.0, 0.0, z_excite_prephase_moment);
     ```
  * **Result**: The rewind gradient will now balance X and Y to `0`, but balance Z to the negative moment required for the next TR's excitation. This eliminates the dead time of a separate refocusing gradient and shortens the TR.
