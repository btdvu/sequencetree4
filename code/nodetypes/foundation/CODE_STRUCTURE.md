# SequenceTree Foundation Nodetypes Documentation

## Overview
The foundation nodetypes library provides pre-built, reusable MRI pulse sequence building blocks. These classes inherit from the SequenceTree framework and implement common MRI sequence components like RF pulses, gradients, readouts, and complete imaging blocks. They handle the complex timing, gradient moment calculations, and k-space navigation required for MRI sequences.

## Architecture

Foundation nodetypes are organized into several categories:

- **RF Pulses**: `STRF`, `STSincRF`, `STSampledRF` - RF excitation and refocusing
- **Gradient Primitives**: `STGradientMom`, `STGradientAmp`, `STArbGradient` - Gradient waveforms
- **Readout Components**: `STReadout`, `STAcquire`, `STArbAcquire`, `STMultiAcquire` - Data acquisition
- **Composite Blocks**: `STExcite`, `STRefocus`, `STEncode` - Multi-component building blocks
- **Sequence Blocks**: `STGradientEchoBlock`, `STSpinEchoBlock` - Complete imaging blocks
- **Loop Structures**: `STCartesianLoop`, `STRadialLoop` - k-space trajectory loops
- **Timing Control**: `STChain` - Flexible child alignment and timing

---

## RF Pulse Classes

### STRF (`strf.h`, `strf.cpp`)
**Base class for RF pulses with arbitrary pulse shapes.**

#### Parameters:
- `flip_angle` (STReal) - Flip angle in degrees, default 90°
- `pulse_duration` (STReal) - Total pulse duration in µs, default 1000
- `reference_fraction` (STReal) - Reference point within pulse (0-1), default 0.5
- `bandwidth` (STReal) - Pulse bandwidth in Hz, default 1000
- `time_step` (STReal) - Sample spacing in µs, default 10
- `phase` (STReal) - RF phase in degrees, default 0
- `frequency` (STReal) - RF frequency offset in Hz, default 0
- `pulse_type` (STInteger) - 1=excitation, 2=refocusing, 0=neither
- `gradient_amplitude` (STVector3) - Slice-select gradient amplitude (internal)
- `slice_thickness` (STReal) - Slice thickness in mm (internal)

#### Events:
- `RF` (STScannerRFPulse*) - The RF pulse event

#### Key Functions:
- `pulseShape(double cycles, double &re, double &im)` - Virtual function defining pulse shape
  - `cycles` = (time - reference_time) × bandwidth
  - Returns complex amplitude (re, im) at given time
  - Override in subclasses to define custom shapes
- `initialize()` - Allocates RF event
- `prepare()` - Computes pulse waveform from shape function
  - Samples `pulseShape()` at `time_step` intervals
  - Normalizes to achieve desired flip angle
  - Scales by gyromagnetic ratio γ
- `run()` - Adds RF event to scanner with phase/frequency adjustments
- `duration()` - Returns pulse duration
- `referenceTime()` - Returns reference point within pulse
- `terminalMoment()` - Returns k-space position after pulse
  - Excitation (type=1): returns (0,0,0)
  - Refocusing (type=2): returns -initialMoment (phase reversal)
- `SAR()` - Returns specific absorption rate
- `setGradientAmplitude(Vector3)` - Set slice-select gradient (for internal use)

#### Usage:
Base class for all RF pulses. Override `pulseShape()` to create custom pulse shapes.

---

### STSincRF (`stsincrf.h`, `stsincrf.cpp`)
**Sinc-shaped RF pulse for slice-selective excitation/refocusing.**

Inherits from `STRF`.

#### Additional Parameters:
- `num_lobes_left` (STReal) - Number of sinc lobes before center, default varies
- `num_lobes_right` (STReal) - Number of sinc lobes after center, default varies

#### Key Functions:
- `pulseShape(double cycles, double &re, double &im)` - Implements sinc function
  - Shape: sin(π·cycles) / (π·cycles)
  - Windowed by number of lobes

#### Usage:
Standard slice-selective pulse with sinc envelope for sharp slice profile.

---

### STSampledRF (`stsampledrf.h`, `stsampledrf.cpp`)
**RF pulse defined by sampled waveform data.**

Inherits from `STRF`.

#### Additional Parameters:
- `pulse_shape` (STString) - Name/identifier for pulse shape

#### Key Functions:
- `setSamples(N, data_real, data_imag, ref_center_time, ref_timestep, ref_bandwidth)` - Load pulse waveform
  - `N` - Number of samples
  - `data_real`, `data_imag` - Complex waveform data
  - `ref_center_time` - Reference center time in µs
  - `ref_timestep` - Original sample spacing in µs
  - `ref_bandwidth` - Design bandwidth in Hz
- `pulseShape(double cycles, double &re, double &im)` - Interpolates sampled data

#### Usage:
Use pre-computed pulse shapes (e.g., SLR, VERSE, adiabatic pulses) loaded from files or resources.

---

## Gradient Primitive Classes

### STGradientMom (`stgradientmom.h`, `stgradientmom.cpp`)
**Trapezoid gradient specified by desired k-space moment.**

Automatically calculates gradient amplitude and timing to achieve target moment while respecting hardware limits.

#### Parameters:
- `ramp_times_1` (STVector3) - Ramp-up times per axis in µs
- `plateau_times` (STVector3) - Plateau times per axis in µs
- `ramp_times_2` (STVector3) - Ramp-down times per axis in µs
- `start_times` (STVector3) - Start time offset per axis in µs
- `amplitude` (STVector3) - Gradient amplitudes in mT/m
- `alignment` (STInteger) - Gradient alignment: 0=left, 1=right, 2=center
- `always_min_dur` (STInteger) - Force minimum duration (0 or 1)
- `maxamp` (STReal) - Maximum amplitude override (0 = use sequence default)
- `ramprate` (STReal) - Ramp rate override (0 = use sequence default)

#### Events:
- `GX`, `GY`, `GZ` (STScannerGradient*) - Gradient events per axis

#### Key Functions:
- `setMoment(Vector3 mom)` - **Primary function**: Set desired gradient moment
  - Automatically designs optimal trapezoid or triangle waveform
  - Respects `maxamp` and `ramprate` constraints
  - Chooses triangle if moment is small, trapezoid otherwise
  - Maintains existing shape if `always_min_dur=0` and moment fits
- `initialize()` - Allocates gradient events
- `prepare()` - Configures gradient events, applies alignment
- `run()` - Adds gradient events to scanner
- `duration()` - Returns maximum duration across all axes
- `totalGradientMoment()` - Returns actual gradient moment applied
- `terminalMoment()` - Returns k-space position after gradient

#### Alignment Modes:
- **0 (left)**: All gradients start at same time
- **1 (right)**: All gradients end at same time
- **2 (center)**: All gradients centered on same time

#### Usage:
Primary gradient class for k-space navigation. Specify desired moment; class handles hardware constraints automatically.

---

### STGradientAmp (`stgradientamp.h`, `stgradientamp.cpp`)
**Trapezoid gradient specified by amplitude and timing.**

Direct control over gradient waveform shape.

#### Parameters:
- `ramp_time_1` (STReal) - Ramp-up time in µs
- `plateau_time` (STReal) - Plateau time in µs
- `ramp_time_2` (STReal) - Ramp-down time in µs
- `amplitude` (STVector3) - Gradient amplitudes per axis in mT/m

#### Events:
- `GX`, `GY`, `GZ` (STScannerGradient*) - Gradient events per axis

#### Key Functions:
- `initialize()` - Allocates gradient events
- `prepare()` - Configures gradient events
- `run()` - Adds gradient events to scanner
- `duration()` - Returns total duration (ramp1 + plateau + ramp2)
- `totalGradientMoment()` - Calculates moment from amplitude × time

#### Usage:
Use when you need explicit control over gradient timing (e.g., matching RF pulse duration).

---

### STArbGradient (`starbgradient.h`, `starbgradient.cpp`)
**Arbitrary gradient waveform with user-defined k-space trajectory.**

Base class for non-Cartesian gradients (spirals, radial, etc.).

#### Parameters:
- `ramp_time_1` (STReal) - Pre-waveform ramp time in µs
- `plateau_time` (STReal) - Waveform duration in µs
- `ramp_time_2` (STReal) - Post-waveform ramp time in µs
- `kspace_offset` (STVector3) - k-space offset for trajectory
- `peakamp` (STReal) - Peak gradient amplitude in mT/m
- `peakslew` (STReal) - Peak slew rate in (mT/m)/µs

#### Events:
- `GX`, `GY`, `GZ` (STScannerArbGradient*) - Arbitrary gradient events

#### Key Functions:
- `gradientShape(double t)` - **Virtual function**: Define k-space trajectory
  - `t` ranges from 0 to 1 across plateau
  - Returns k-space position Vector3
  - Override in subclasses to define trajectory
- `momentAt(double t)` - k-space position at time t (0-1)
- `ramp1Moment()` - Moment accumulated during first ramp
- `initialize()` - Allocates arbitrary gradient events
- `prepare()` - Samples trajectory, creates gradient waveforms
- `run()` - Adds gradient events to scanner
- `duration()` - Returns total duration
- `totalGradientMoment()` - Returns total moment along trajectory

#### Usage:
Base class for non-Cartesian trajectories. Override `gradientShape()` to define custom k-space paths.

---

### STCircleGradient (`stcirclegradient.h`, `stcirclegradient.cpp`)
**Circular/elliptical k-space trajectory.**

Inherits from `STArbGradient`.

#### Additional Parameters:
- `kspace_radius_1` (STReal) - Radius along first direction
- `kspace_radius_2` (STReal) - Radius along second direction
- `num_cycles` (STReal) - Number of circular cycles
- `kspace_direction_1` (STVector3) - First k-space direction vector
- `kspace_direction_2` (STVector3) - Second k-space direction vector
- `kspace_offset` (STVector3) - Center offset in k-space

#### Key Functions:
- `gradientShape(double t)` - Implements circular trajectory
  - Returns: offset + radius1·dir1·cos(2π·cycles·t) + radius2·dir2·sin(2π·cycles·t)

#### Usage:
For circular or elliptical k-space sampling (e.g., PROPELLER, circular EPI).

---

## Readout Classes

### STReadout (`streadout.h`, `streadout.cpp`)
**ADC readout event for data acquisition.**

#### Parameters:
- `enabled` (STInteger) - Enable/disable readout (0 or 1), default 1
- `dwell_time` (STReal) - Time between ADC samples in µs, default 30
- `N` (STInteger) - Number of readout points, default 256
- `reference_fraction` (STReal) - Echo position (0-1), default 0.5
- `actual_reference_fraction` (STReal) - Actual echo position after rounding (read-only)
- `reference_sample` (STReal) - Echo sample number (read-only)
- `phase` (STReal) - Readout phase in degrees, default 0
- `frequency` (STReal) - Readout frequency offset in Hz, default 0
- `gradient_amplitude` (STVector3) - Readout gradient amplitude (internal)
- `round_up_reference_time` (STInteger) - Round reference time up (1) or down (0)

#### Events:
- `Readout` (STScannerReadout*) - The readout event

#### Key Functions:
- `initialize()` - Allocates readout event
- `prepare()` - Configures readout timing and reference point
- `run()` - Adds readout event with phase/frequency corrections
- `duration()` - Returns N × dwell_time
- `referenceTime()` - Returns echo center time
- `setGradientAmplitude(Vector3)` - Set readout gradient (internal)
- `setADCIndices(int &indx)` - Assign ADC index
- `setReadoutIndex(int iterator_index, int indx)` - Set readout index for iterator

#### k-space Indexing Functions:
Set current acquisition indices for image reconstruction:
- `setCurrentLine(long)`, `setCurrentPartition(long)` - Phase encoding
- `setCurrentSlice(long)`, `setCurrentEcho(long)` - Slice and echo
- `setCurrentAverage(long)`, `setCurrentRepetition(long)` - Averaging
- `setCurrentPhase(long)`, `setCurrentSet(long)` - Cardiac, multi-set
- `setCurrentSegment(long)` - Segmented acquisition
- `setCurrentIda/b/c/d/e(long)` - Custom indices

#### Scan Flags:
- `setFirstScanInSlice(bool)`, `setLastScanInSlice(bool)`
- `setLastScanInConcatenation(bool)`, `setLastScanInMeasurement(bool)`

#### Usage:
Core readout class. Handles ADC timing, phase/frequency adjustments, and k-space indexing.

---

### STAcquire (`stacquire.h`, `stacquire.cpp`)
**Complete readout block with encoding and readout gradient.**

Combines gradient encoding, readout gradient, and ADC into single unit.

#### Parameters:
- `echo_moment` (STVector3) - Desired k-space position at echo in (mT/m)·µs
- `moment_per_point` (STVector3) - k-space step per readout point in (mT/m)·µs

#### Children:
- `Encode` (STGradientMom*) - Pre-readout encoding gradient
- `ReadoutGradient` (STGradientAmp*) - Readout gradient
- `Readout` (STReadout*) - ADC readout

#### Key Functions:
- `prepare()` - Configures encoding and readout gradients
  - Sets readout gradient amplitude from `moment_per_point / dwell_time`
  - Calculates encoding moment to reach `echo_moment` at echo center
  - Accounts for readout gradient ramp
- `duration()` - Returns total duration

#### Usage:
Standard Cartesian readout. Specify echo position and k-space sampling density; class handles gradient calculations.

---

### STArbAcquire (`starbacquire.h`, `starbacquire.cpp`)
**Readout with arbitrary gradient trajectory.**

Combines encoding, arbitrary gradient, and readout.

#### Parameters:
- `kspace_offset` (STVector3) - k-space offset for trajectory

#### Children:
- `Encode` (STGradientMom*) - Pre-readout encoding
- `ReadoutGradient` (STArbGradient*) - Arbitrary readout gradient
- `Readout` (STReadout*) - ADC readout

#### Key Functions:
- `prepare()` - Configures encoding for arbitrary trajectory
- `duration()` - Returns total duration

#### Usage:
For non-Cartesian readouts (spiral, radial, etc.). Use with `STCircleGradient` or custom `STArbGradient` subclass.

---

### STMultiAcquire (`stmultiacquire.h`, `stmultiacquire.cpp`)
**Multi-echo readout train (e.g., for EPI, GRASE).**

Creates multiple readout blocks with alternating gradients.

#### Parameters:
- `num_echoes` (STInteger) - Number of echoes
- `echo_spacing` (STReal) - Time between echo centers in µs
- `reference_echo` (STInteger) - Which echo is the reference (k-space center)
- `alternating` (STInteger) - Alternate gradient polarity (1) or not (0)
- `num_readout_points` (STInteger) - Points per readout
- `dwell_time` (STReal) - ADC dwell time in µs
- `ramp_time` (STReal) - Gradient ramp time in µs
- `echo_moment` (STVector3) - k-space position at reference echo
- `moment_per_point` (STVector3) - k-space step per point
- `step_moment` (STVector3) - k-space step between echoes
- `maxamp` (STReal) - Maximum gradient amplitude
- `ramprate` (STReal) - Gradient ramp rate

#### Key Functions:
- `prepare()` - Creates and configures multiple `STAcquire` children
  - Calculates gradient moments for each echo
  - Handles alternating gradient polarity
  - Sets timing to achieve desired echo spacing
- `duration()` - Returns total duration of echo train
- `setMDHOnline()` - Configure online reconstruction flags

#### Usage:
For multi-echo sequences like EPI, GRASE, multi-echo spin echo. Automatically handles gradient switching and k-space indexing.

---

## Composite Block Classes

### STExcite (`stexcite.h`, `stexcite.cpp`)
**Slice-selective excitation with prephasing.**

Complete excitation block with slice-select gradient and optional prephasing.

#### Parameters:
- `gradient_amplitude` (STVector3) - Slice-select gradient amplitude in mT/m
- `slice_thickness` (STReal) - Slice thickness in mm
- `bandwidth` (STReal) - RF bandwidth in Hz
- `prephase` (STInteger) - Enable prephasing gradient (0 or 1), default 1

#### Children:
- `Prephase` (STGradientMom*) - Slice-select prephasing gradient
- `SliceGradient` (STGradientAmp*) - Slice-select gradient during RF
- `RF` (STRF*) - RF pulse

#### Key Functions:
- `prepare()` - Configures slice selection
  - Calculates RF bandwidth from gradient and slice thickness: BW = G·thickness·γ
  - Sets slice gradient to match RF duration
  - Calculates prephase moment to null slice-select gradient before excitation
  - Accounts for gradient ramps
- `terminalMoment()` - Returns k-space position after excitation
  - Accounts for slice-select gradient after RF center
- `duration()` - Returns total duration

#### Usage:
Standard slice-selective excitation. Set `gradient_amplitude` and `slice_thickness`; class handles bandwidth and prephasing.

---

### STRefocus (`strefocus.h`, `strefocus.cpp`)
**Slice-selective refocusing with crusher gradients.**

Complete refocusing block with crushers for unwanted coherences.

#### Parameters:
- `gradient_amplitude` (STVector3) - Slice-select gradient amplitude in mT/m
- `slice_thickness` (STReal) - Slice thickness in mm
- `bandwidth` (STReal) - RF bandwidth in Hz
- `crusher_moment` (STVector3) - Crusher gradient moment in (mT/m)·µs
- `flip_angle` (STReal) - Refocusing flip angle in degrees

#### Children:
- `Crusher1` (STGradientMom*) - Pre-RF crusher gradient
- `SliceGradient` (STGradientAmp*) - Slice-select gradient during RF
- `RF` (STRF*) - Refocusing RF pulse
- `Crusher2` (STGradientMom*) - Post-RF crusher gradient

#### Key Functions:
- `prepare()` - Configures refocusing
  - Sets RF bandwidth from gradient and slice thickness
  - Configures symmetric crusher gradients
  - Sets RF pulse type to refocusing (type=2)
- `terminalMoment()` - Returns k-space position after refocusing
- `duration()` - Returns total duration

#### Usage:
Standard spin-echo refocusing. Crushers suppress unwanted signals (FID, stimulated echoes).

---

### STEncode (`stencode.h`, `stencode.cpp`)
**Phase encoding gradient with optional rewinder.**

Simple encoding block for phase encoding or rewinding.

#### Parameters:
- `moment` (STVector3) - Encoding moment in (mT/m)·µs
- `do_rewind` (STInteger) - Apply rewinder after (0 or 1)

#### Children:
- `Gradient` (STGradientMom*) - Encoding gradient

#### Key Functions:
- `prepare()` - Sets gradient moment
- `duration()` - Returns gradient duration

#### Usage:
For phase encoding steps or gradient rewinders at end of block.

---

## Sequence Block Classes

### STGradientEchoBlock (`stgradientechoblock.h`, `stgradientechoblock.cpp`)
**Complete gradient echo imaging block.**

Inherits from `STChain`. Implements full gradient echo with excitation, encoding, and readout.

#### Parameters:
- `TE` (STReal) - Echo time in µs
- `TR` (STReal) - Repetition time in µs
- `kspace_dir` (STVector3) - k-space encoding direction
- `kspace_echo` (STVector3) - k-space position at echo
- `excite_time` (STReal) - Time of excitation within TR

#### Children:
- `Excite` (STExcite*) - Excitation block
- `Acquire` (STAcquire*) - Readout block
- `Rewind` (STEncode*) - Gradient rewinder

#### Key Functions:
- `initialize()` - Sets up block structure
- `prepare()` - Configures timing and k-space trajectory
  - Aligns echo at TE relative to excitation
  - Sets encoding to reach `kspace_echo` at echo center
  - Configures rewinder to return to k-space origin
  - Sets block duration to TR

#### Usage:
Standard gradient echo sequence block. Set TE, TR, and k-space position; class handles all timing and gradients.

---

### STSpinEchoBlock (`stspinechoblock.h`, `stspinechoblock.cpp`)
**Complete spin echo imaging block.**

Inherits from `STChain`. Implements full spin echo with excitation, refocusing, and readout.

#### Parameters:
- `TE` (STReal) - Echo time in µs
- `TR` (STReal) - Repetition time in µs
- `kspace_dir` (STVector3) - k-space encoding direction
- `kspace_echo` (STVector3) - k-space position at echo

#### Children:
- `Excite` (STExcite*) - Excitation block
- `Refocus` (STRefocus*) - Refocusing block
- `Acquire` (STAcquire*) - Readout block
- `Rewind` (STEncode*) - Gradient rewinder

#### Key Functions:
- `initialize()` - Sets up block structure
- `prepare()` - Configures timing and k-space trajectory
  - Positions refocusing at TE/2
  - Aligns echo at TE
  - Handles phase encoding and rewinding

#### Usage:
Standard spin echo sequence block. Set TE, TR, and k-space position; class handles all timing and gradients.

---

## Loop Structure Classes

### STCartesianLoop (`stcartesianloop.h`, `stcartesianloop.cpp`)
**Cartesian k-space sampling loop.**

Inherits from `STLoop`. Iterates over 2D/3D Cartesian k-space grid.

#### Parameters:
- `PE1` (STIterator) - First phase encode iterator (e.g., ky)
- `PE2` (STIterator) - Second phase encode iterator (e.g., kz)
- `readout_dir` (STVector3) - Readout direction in k-space
- `PE1_dir` (STVector3) - First phase encode direction
- `PE2_dir` (STVector3) - Second phase encode direction

#### Children:
- `Block` (STGradientEchoBlock*) - Imaging block to repeat

#### Key Functions:
- `prepare()` - Configures loop
- `loopRun()` - Executes one iteration
  - Calculates k-space position from iterator values
  - Sets `Block->kspace_echo` for current phase encode
  - Updates readout k-space indexing

#### Usage:
Standard Cartesian imaging loop. Iterators define phase encode steps; class handles k-space navigation.

---

### STRadialLoop (`stradialloop.h`, `stradialloop.cpp`)
**Radial k-space sampling loop.**

Inherits from `STLoop`. Iterates over radial spokes in k-space.

#### Parameters:
- `angle` (STIterator) - Spoke angle iterator (degrees)
- `PE` (STIterator) - Partition/slice iterator
- `readout_dir1` (STVector3) - First readout direction (rotated by angle)
- `readout_dir2` (STVector3) - Second readout direction (rotated by angle)
- `PE_dir` (STVector3) - Partition direction

#### Children:
- `Block` (STGradientEchoBlock*) - Imaging block to repeat

#### Key Functions:
- `prepare()` - Configures loop
- `loopRun()` - Executes one iteration
  - Rotates readout direction by current angle
  - Sets `Block->kspace_dir` for current spoke
  - Updates k-space indexing

#### Usage:
Radial/projection imaging. Angle iterator defines spoke angles; class handles rotation and k-space navigation.

---

## Timing Control Classes

### STChain (`stchain.h`, `stchain.cpp`)
**Flexible timing and alignment of child nodes.**

Inherits from `STNode`. Provides sophisticated alignment control for positioning children relative to each other or absolute times.

#### Alignment Constants:
- `ST_ALIGN_LEFT` (1) - Align to end of previous child (no gradient overlap)
- `ST_ALIGN_CENTER` (2) - Center child within block
- `ST_ALIGN_RIGHT` (3) - Align to end of block
- `ST_ALIGN_RELATIVE` (4) - Align relative to another child's reference time
- `ST_ALIGN_ABSOLUTE` (5) - Align to absolute time within block

#### Key Functions:
- `addChild(STNode*)` - Add child with default left alignment
- `setAlignment(int index, int alignment, double timing, int relative_index)` - Set child alignment
  - `index` - Child index
  - `alignment` - Alignment mode (see constants)
  - `timing` - Timing offset in µs
  - `relative_index` - Reference child index (for RELATIVE mode)
- `alignChild(STNode* child, int alignment, double timing, int relative_index)` - Align by pointer
- `setDuration(double)` - Set block duration explicitly
- `duration()` - Get block duration
- `prepare()` - Calculates child positions
  - Propagates k-space moments through chain
  - Resolves alignment constraints
  - Checks for gradient overlaps

#### Helper Functions:
- `overlaps(STNode* C1, STNode* C2)` - Check if gradients overlap

#### Usage:
Base class for complex timing blocks. Use alignment modes to position RF pulses, gradients, and readouts precisely.

**Example Alignments:**
- **LEFT**: Gradients play sequentially without overlap
- **RELATIVE**: Align echo center to excitation center (TE timing)
- **ABSOLUTE**: Position event at specific time in TR
- **CENTER**: Center crusher gradients around refocusing pulse

---

## Key Concepts for MRI Scientists

### Gradient Moment Calculations
All gradient classes automatically handle moment calculations:
- **Moment** = ∫ G(t) dt = Area under gradient waveform
- **Units**: (mT/m)·µs or (µT/mm)·µs
- **k-space**: Moment determines k-space position via γ

### Automatic Gradient Design
`STGradientMom` automatically designs optimal waveforms:
1. **Triangle**: Used when moment is small (< maxamp²/ramprate)
2. **Trapezoid**: Used for larger moments
3. **Shape preservation**: Maintains existing shape if `always_min_dur=0`

### Phase and Frequency Corrections
RF and readout classes automatically apply:
- **Phase correction**: Accounts for FOV shifts and accumulated gradient moments
- **Frequency correction**: Adjusts for gradient-induced frequency shifts
- Formula: Δf = G·shift·γ, Δφ = ∫(G·shift)·γ·360°

### k-space Navigation
Composite blocks handle k-space automatically:
- **Initial moment**: k-space position at block start
- **Terminal moment**: k-space position at block end
- **Echo positioning**: Encoding gradients calculated to reach target k-space at echo

### Timing Hierarchy
1. **STChain** resolves child alignment constraints
2. **Reference times** define alignment points (e.g., echo center, RF center)
3. **Gradient overlaps** detected and prevented
4. **Hardware rounding** ensures 10µs timing grid

### Slice Selection
Excitation and refocusing blocks automatically calculate:
- **Bandwidth**: BW = G·thickness·γ
- **Prephasing**: Nulls slice-select gradient moment before excitation
- **Crusher moments**: Suppress unwanted coherences

---

## File Organization

| File | Class | Purpose |
|------|-------|---------|
| `strf.h/cpp` | STRF | Base RF pulse class |
| `stsincrf.h/cpp` | STSincRF | Sinc-shaped RF pulse |
| `stsampledrf.h/cpp` | STSampledRF | Sampled RF waveform |
| `stgradientmom.h/cpp` | STGradientMom | Moment-specified gradient |
| `stgradientamp.h/cpp` | STGradientAmp | Amplitude-specified gradient |
| `starbgradient.h/cpp` | STArbGradient | Arbitrary gradient trajectory |
| `stcirclegradient.h/cpp` | STCircleGradient | Circular k-space trajectory |
| `streadout.h/cpp` | STReadout | ADC readout |
| `stacquire.h/cpp` | STAcquire | Cartesian readout block |
| `starbacquire.h/cpp` | STArbAcquire | Arbitrary trajectory readout |
| `stmultiacquire.h/cpp` | STMultiAcquire | Multi-echo readout train |
| `stexcite.h/cpp` | STExcite | Slice-selective excitation |
| `strefocus.h/cpp` | STRefocus | Slice-selective refocusing |
| `stencode.h/cpp` | STEncode | Phase encoding gradient |
| `stgradientechoblock.h/cpp` | STGradientEchoBlock | Gradient echo block |
| `stspinechoblock.h/cpp` | STSpinEchoBlock | Spin echo block |
| `stcartesianloop.h/cpp` | STCartesianLoop | Cartesian k-space loop |
| `stradialloop.h/cpp` | STRadialLoop | Radial k-space loop |
| `stchain.h/cpp` | STChain | Timing and alignment |

---

## Usage for AI Coding Tools

When building MRI sequences with foundation nodetypes:

1. **Use composite blocks** (`STExcite`, `STRefocus`, `STAcquire`) for standard components
2. **Use `STGradientMom`** for k-space navigation - specify moment, not amplitude
3. **Use sequence blocks** (`STGradientEchoBlock`, `STSpinEchoBlock`) for complete imaging
4. **Use loops** (`STCartesianLoop`, `STRadialLoop`) for k-space sampling
5. **Override `pulseShape()`** in STRF subclasses for custom RF pulses
6. **Override `gradientShape()`** in STArbGradient subclasses for custom trajectories
7. **Use `STChain`** for complex timing (align echoes, crushers, etc.)
8. **Set `kspace_echo`** in imaging blocks to define phase encoding
9. **Phase/frequency corrections** are automatic - trust the framework
10. **All timing in µs**, **gradients in mT/m**, **moments in (mT/m)·µs**

### Typical Gradient Echo Sequence:
```cpp
class MyGradientEcho : public STSequence {
public:
    void setup() {
        ST_CHILD(STCartesianLoop, Loop)
        // Loop automatically handles k-space navigation
        // Block automatically handles TE/TR timing
    }
};
```

### Typical Spin Echo Sequence:
```cpp
class MySpinEcho : public STSequence {
public:
    void setup() {
        ST_CHILD(STCartesianLoop, Loop)
        // Loop contains STSpinEchoBlock
        // Refocusing and crushers handled automatically
    }
};
```

### Custom RF Pulse:
```cpp
class MyCustomRF : public STRF {
public:
    void pulseShape(double cycles, double &re, double &im) {
        // Define custom shape
        // cycles = (t - t_ref) * bandwidth
        re = /* your function */;
        im = /* your function */;
    }
};
```

### Custom Trajectory:
```cpp
class MySpiralGradient : public STArbGradient {
public:
    Vector3 gradientShape(double t) {
        // t from 0 to 1
        // Return k-space position
        double angle = 2*PI*num_turns*t;
        double radius = max_radius*t;
        return Vector3(radius*cos(angle), radius*sin(angle), 0);
    }
};
```

---

## Common Patterns

### Setting TE in Gradient Echo:
```cpp
Block->TE = 5000; // 5 ms
Block->excite_time = 1000; // Excite at 1 ms into TR
// Echo automatically positioned at TE relative to excitation
```

### Phase Encoding:
```cpp
Loop->PE1.set(-64, 1, 63); // ky from -64 to 63
Loop->PE2.set(0, 1, 31);   // kz from 0 to 31
// Loop automatically sets kspace_echo for each iteration
```

### Multi-Echo EPI:
```cpp
MultiEcho->num_echoes = 64;
MultiEcho->echo_spacing = 1000; // 1 ms
MultiEcho->alternating = 1; // Alternate gradient polarity
// Automatically creates 64 readouts with proper k-space indexing
```

### Custom Crushers:
```cpp
Refocus->crusher_moment = Vector3(0, 0, 5000); // 5000 (mT/m)·µs on slice axis
// Crushers automatically positioned around refocusing pulse
```
