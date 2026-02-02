# SequenceTree Framework Documentation

## Overview
SequenceTree is a vendor-agnostic C++ framework for writing MRI pulse sequences. This framework provides the core abstractions and data structures needed to define pulse sequences that can be compiled against vendor-specific hardware implementations (e.g., Siemens).

## Architecture

The framework uses a **hierarchical tree structure** where:
- **STSequence** is the root node containing the entire pulse sequence
- **STNode** objects form the tree structure representing sequence blocks and events
- **STLoop** objects enable iteration over sequence parameters
- **STParameter** objects hold configurable values (timing, gradients, FOV, etc.)
- **STScanner** provides the hardware abstraction layer for vendor-specific compilation

---

## Core Classes

### STObject (`stobject.h`, `stobject.cpp`)
**Base class for all framework objects.**

#### Key Functions:
- `name()` - Returns object name
- `objectType()` - Returns type identifier
- `parent()` - Returns parent node in tree
- `isParameter()`, `isNode()`, `isLoop()` - Type checking
- `isBlock()` - Checks if node is a block (not a loop, but parent is a loop)
- `isModified()`, `setModified(bool)` - Track parameter changes

#### Utility:
- `normalizePhase(long double ph)` - Normalizes phase values to standard range

---

### STNode (`stnode.h`, `stnode.cpp`)
**Represents a node in the sequence tree. Nodes can contain child nodes and parameters.**

#### Key Member Functions:

**Tree Structure:**
- `addChild(STNode*)` - Add child node
- `child(int index)` - Get child by index
- `child(SString name)` - Get child by name
- `childCount()` - Number of children
- `removeChild(int index)` - Remove child
- `replaceChild(STNode* old, STNode* new)` - Replace child node
- `parent()` - Get parent node

**Parameters:**
- `addParameter(STParameter*, SString name)` - Add parameter to node
- `parameter(int index)` - Get parameter by index
- `parameterCount()` - Number of parameters
- `setParameterFromString(SString name, SString value)` - Set parameter value

**Timing:**
- `startTime()` - Absolute start time in microseconds
- `relativeStartTime()` - Start time relative to parent
- `setRelativeStartTime(double t)` - Set relative timing
- `duration()` - Duration in microseconds (virtual, override in subclasses)
- `referenceTime()` - Reference time for alignment

**Gradient Moments:**
- `initialMoment()`, `setInitialMoment(Vector3)` - k-space position at node start
- `terminalMoment()` - k-space position at node end
- `totalGradientMoment()` - Total gradient moment applied by this node and children
- `gradientStartTimes()`, `gradientEndTimes()` - Timing for gradient overlap detection

**Execution:**
- `initialize()` - Initialize node and children before sequence execution
- `prepare()` - Prepare modified children for execution
- `run()` - Execute the node (calls scanner methods, runs children)
- `SAR()` - Specific absorption rate (sum of children by default)

**Scanner/Sequence Access:**
- `scanner()`, `setScanner(STScanner*)` - Hardware abstraction
- `sequence()`, `setSequence(STSequence*)` - Root sequence reference

#### Macros for Subclass Definition:
- `ST_CLASS(name, base)` - Define class type
- `ST_CHILD(type, name)` - Create and add child node
- `ST_PARAMETER(type, name, default, units)` - Create and add parameter
- `ST_ALIGN(name, alignment, timing, relativeindex)` - Align child timing

---

### STParameter (`stparameter.h`, `stparameter.cpp`)
**Base class for typed parameters. Parameters hold configurable values.**

#### Parameter Types:

**STInteger** - Integer values
- `operator long()` - Get value
- `operator=(long)` - Set value
- `setFromString(SString)`, `toString()` - String conversion

**STReal** - Floating-point values
- `operator double()` - Get value
- `operator=(double)` - Set value
- Units: microseconds, mT/m, degrees, Hz, etc.

**STVector3** - 3D vectors (for gradients, FOV, k-space)
- `x()`, `y()`, `z()` - Get components
- `setX()`, `setY()`, `setZ()` - Set components
- `abs()` - Vector magnitude
- Operators: `+`, `-`, `*`, `/`
- String format: `(x,y,z)`

**STString** - String values
- `operator SString()` - Get value
- `operator=(SString)` - Set value

**STIterator** - Loop iteration parameter
- `set(double min, double step, double max)` - Define iteration range
- `initialize()` - Reset to start
- `increment()` - Step to next value
- `value()` - Current iteration value
- `numSteps()`, `stepNumber()` - Iteration info
- String format: `min:step:max` with optional `check: val1;val2;...`

#### Common Methods:
- `hasBeenSet()` - Check if parameter was explicitly set by user
- `setFromString(SString)` - Parse from string
- `toString()` - Convert to string

---

### Vector3 (`stparameter.h`)
**3D vector class for spatial quantities.**

Used for:
- Field of view (FOV) in mm
- Gradient moments in (mT/m)·µs
- k-space positions
- Gradient amplitudes per axis

#### Methods:
- `x()`, `y()`, `z()` - Component access
- `abs()` - Magnitude
- Operators: `+`, `-`, `*` (scalar), `/` (scalar), `==`, `!=`

---

### STLoop (`stloop.h`, `stloop.cpp`)
**Node that iterates over child nodes with varying parameters.**

Loops enable scanning over different k-space lines, slices, averages, etc.

#### Key Functions:
- `loopInitialize()` - Initialize all iterators
- `loopStep()` - Increment to next iteration
- `loopRun()` - Execute current iteration
- `run()` - Override that manages loop execution

Loops contain `STIterator` parameters that define iteration ranges.

---

### STSequence (`stsequence.h`, `stsequence.cpp`)
**Root node of the sequence tree. Inherits from STLoop.**

#### Built-in Parameters:
- `FOV` (STVector3) - Field of view in mm, default (200,200,50)
- `maxamp` (STReal) - Maximum gradient amplitude in mT/m (µT/mm), default 20
- `ramprate` (STReal) - Gradient ramp rate in (mT/m)/µs, default 0.1
- `gamma` (STReal) - Gyromagnetic ratio in Hz/µT, default 42.5764 (for ¹H)
- `FOV_shift` (STVector3) - FOV shift in mm, default (0,0,0)
- `phase_shift` (STReal) - Phase shift in degrees
- `FOV_shift_offset` (STVector3) - Internal FOV shift offset

#### Key Functions:

**Execution:**
- `setup()` - Virtual function to define sequence structure (override in subclass)
- `initialize()` - Initialize sequence before execution
- `run()` - Execute the sequence
- `check()` - Run in check mode (validate without hardware execution)
- `checkButDontRun()` - Validate timing without calling scanner
- `computeStatistics()` - Calculate total blocks, duration, SAR

**Loop Management:**
- `loop(int index)` - Get loop child by index
- `loopInitialize()`, `loopStep()`, `loopRun()` - Loop control

**Parameter Management:**
- `loadParametersFromFile(SString)` - Load parameters from file
- `loadParametersFromText(SString)` - Parse parameters from text
- `writeParametersToFile(SString)` - Save parameters to file
- `findNodeFromString(SString)` - Find node by path (e.g., "Root->Loop1->Block2")
- `findParameterFromString(SString)` - Find parameter by path

**k-space Conversion:**
- `kspace2moment(Vector3 kspace)` - Convert k-space position to gradient moment

**Global Parameters:**
- `addGlobalParameterConnection(SString name, SString connection)` - Link global parameter
- `globalParameter(SString name)` - Get global parameter value
- `setGlobalParameter(SString name, double val)` - Set global parameter

**Resources:**
- `resources()` - Get resource manager
- `resource(SString name)` - Get specific resource

**Statistics:**
- `statBlockCount()`, `statDuration()`, `statSAR()` - Get computed statistics

**Phase Calculation:**
- `phaseAdjustment()` - Calculate phase adjustment from FOV shift and gradient moments
- `getFOVShiftX()`, `getFOVShiftY()`, `getFOVShiftZ()` - Get total FOV shifts

---

### STScanner (`stscanner.h`, `stscanner.cpp`)
**Hardware abstraction layer. Vendor-specific implementations inherit from this.**

#### Event Allocation:
- `allocateRFPulse(STNode*)` - Create RF pulse event
- `allocateReadout(STNode*)` - Create readout/ADC event
- `allocateGradient(STNode*)` - Create trapezoid gradient event
- `allocateArbGradient(STNode*)` - Create arbitrary gradient waveform event

#### Sequence Execution:
- `beginSequence()` - Start sequence execution
- `endSequence()` - Finish sequence execution
- `beginBlock(double duration)` - Start timing block
- `addEvent(STScannerEvent*)` - Add event to current block
- `endBlock(STNode*)` - Finish block, update statistics
- `inBlockRange()` - Check if block should be executed

#### Iterator Callbacks:
- `iteratorInitialized(int index)` - Called when iterator initialized
- `iteratorStepped(int index)` - Called when iterator incremented
- `iteratorReset(int index)` - Called when iterator reset

#### Statistics:
- `totalSAR()` - Total specific absorption rate
- `totalDuration()` - Total sequence duration in µs
- `totalGradientMomentX/Y/Z()` - Total gradient moments per axis

#### Protocol Parameters:
- `setValue(SString key, double val)` - Set protocol parameter
- `value(SString key)` - Get protocol parameter value
- `setRange(SString key, min, step, max)` - Set parameter range
- `setText(SString key, SString val)` - Set text parameter
- `parameter(SString key)` - Get protocol parameter structure

#### Special Parameters:
- `addSpecialParameter(name, ptype, label, units)` - Define UI parameter
- `specialParameterCount()`, `specialParameter(int)` - Access special parameters

#### Error Handling:
- `reportError(SString)` - Report error message
- `errors()` - Get accumulated errors
- `clearErrors()` - Clear error list

#### Timing Utilities:
- `rounduptime(double t)` - Round time up to 10µs boundary
- `rounddowntime(double t)` - Round time down to 10µs boundary

#### Vendor Extension:
- `scannerCommand(SString command, void* data1-4)` - Vendor-specific commands
- `doneScanning()` - Check if scanning complete

---

### STScannerEvent (`stscanner.h`, `stscanner.cpp`)
**Base class for scanner events (RF, gradients, readout).**

#### Common Properties:
- `startTime()`, `setStartTime(double)` - Event start time in µs
- `duration()` - Event duration in µs
- `endTime()` - Calculated end time
- `referenceTime()` - Reference point within event
- `phase()`, `setPhase(double)` - Phase in degrees
- `frequency()`, `setFrequency(double)` - Frequency in Hz
- `eventType()` - Event type identifier
- `parent()` - Parent STNode
- `treeIndex()` - Index in sequence tree

---

### STScannerRFPulse (`stscanner.h`, `stscanner.cpp`)
**RF excitation/refocusing pulse event.**

#### Properties:
- `pulseCount()` - Number of samples in pulse
- `pulseMagnitude(long index)` - RF amplitude at sample in µT
- `pulsePhase(long index)` - RF phase at sample in degrees
- `timeStep()` - Time between samples in µs
- `flipAngle()` - Actual flip angle in degrees
- `SAR()` - Specific absorption rate for this pulse

#### Configuration:
- `setPulse(N, mag_data, phase_data, timestep, ref_flip, ref_time)` - Define pulse waveform
- `setFlipAngle(double)` - Set desired flip angle (scales magnitude)
- `setReferenceInfo(slice_amp, thickness, type)` - Slice selection info (vendor override)

#### Event Type:
`ST_EVENT_RF_PULSE` (1)

---

### STScannerReadout (`stscanner.h`, `stscanner.cpp`)
**ADC readout event for data acquisition.**

#### Properties:
- `readoutCount()` - Number of ADC samples
- `dwellTime()` - Time between samples in µs
- `ADCIndex()` - ADC channel index
- `onlineADC()` - Whether ADC is processed online
- `referenceTime()` - Reference point in readout

#### k-space Indexing:
Set current position in k-space for image reconstruction:
- `setCurrentLine(long)` - Phase encode line
- `setCurrentPartition(long)` - Partition (3D)
- `setCurrentSlice(long)` - Slice number
- `setCurrentEcho(long)` - Echo number
- `setCurrentAverage(long)` - Average number
- `setCurrentPhase(long)` - Cardiac phase
- `setCurrentRepetition(long)` - Repetition
- `setCurrentSet(long)` - Set number
- `setCurrentSegment(long)` - Segment
- `setCurrentIda/b/c/d/e(long)` - Custom indices

Corresponding getters: `currentLine()`, `currentPartition()`, etc.

#### Scan Flags:
- `setFirstScanInSlice(bool)` - Mark first scan in slice
- `setLastScanInSlice(bool)` - Mark last scan in slice
- `setLastScanInConcatenation(bool)` - Mark last in concatenation
- `setLastScanInMeasurement(bool)` - Mark end of measurement

#### Configuration:
- `setReadout(N, dwell_time, ref_time, ADC_index)` - Define readout
- `setADCIndex(int)` - Set ADC channel
- `setOnlineADC(bool)` - Enable/disable online processing

#### Event Type:
`ST_EVENT_READOUT` (2)

---

### STScannerGradient (`stscanner.h`, `stscanner.cpp`)
**Trapezoid gradient event.**

#### Properties:
- `direction()` - Gradient axis: 1=X, 2=Y, 3=Z
- `amplitude()` - Plateau amplitude in mT/m (µT/mm)
- `rampTime1()` - Ramp-up time in µs
- `plateauTime()` - Plateau duration in µs
- `rampTime2()` - Ramp-down time in µs
- `moment()` - Total gradient moment (area under trapezoid)

#### Configuration:
- `setGradient(direction, amp, ramp1, plateau, ramp2)` - Define trapezoid

#### Event Type:
`ST_EVENT_GRADIENT` (3)

---

### STScannerArbGradient (`stscanner.h`, `stscanner.cpp`)
**Arbitrary gradient waveform event.**

#### Properties:
- `direction()` - Gradient axis: 1=X, 2=Y, 3=Z
- `count()` - Number of samples
- `amplitude(long index)` - Amplitude at sample in mT/m
- `timeStep()` - Time between samples in µs
- `moment()` - Total gradient moment (integral of waveform)

#### Configuration:
- `setArbGradient(direction, N, amplitudes, time_step)` - Define waveform

#### Event Type:
`ST_EVENT_ARB_GRADIENT` (4)

---

### STResources (`stresources.h`, `stresources.cpp`)
**Resource manager for storing reusable data (RF pulses, gradient waveforms, etc.).**

#### STResource Class:
- `name()` - Resource name
- `setDoubleList(N, data)` - Store array of doubles
- `doubleListCount()`, `getDoubleList(index)` - Access array
- `setDouble(double)`, `getDouble()` - Store single value
- `writeToText(SString&)`, `readFromText(SString&)` - Serialization

#### STResources Manager:
- `addResource(STResource*)` - Add resource
- `resource(SString name)` - Get resource by name
- `resource(long index)` - Get resource by index
- `count()` - Number of resources
- `removeResource(long index)` - Remove resource
- `writeToText(SString&)`, `readFromText(SString&)` - Serialization

---

## Utility Classes

### SString (`sstring.h`, `sstring.cpp`)
**Custom string class (alternative to QString for non-Qt builds).**

#### Key Functions:
- `count()` - String length
- `operator+`, `operator+=` - Concatenation
- `append(char)`, `append(SString)` - Append
- `remove(char)`, `remove(const char*)` - Remove substring
- `split(char)`, `split(const char*)` - Split into list
- `indexOf(SString)` - Find substring
- `mid(long index, long count)` - Extract substring
- `toInt()`, `toDouble()` - Parse numeric values
- `SString::number(double)` - Convert number to string
- Comparison: `==`, `!=`
- Index access: `operator[](long)`

---

### SList<T> (`slist.h`)
**Custom templated linked list class (alternative to QList for non-Qt builds).**

#### Key Functions:
- `append(T)` - Add element to end
- `operator<<(T)` - Append operator
- `operator[](long)` - Access by index
- `value(long)` - Safe access (returns default if out of bounds)
- `count()` - Number of elements
- `isEmpty()` - Check if empty
- `removeAt(long)` - Remove element
- `clear()` - Remove all elements

---

## Data Structures

### STProtocolParameter (`stscanner.h`)
Protocol parameter exposed to scanner UI:
- `name` - Parameter name
- `value` - Current value
- `minimum`, `maximum`, `step` - Range constraints
- `text` - Text value (for string parameters)

### STSpecialParameter (`stscanner.h`)
Special UI parameter definition:
- `name` - Parameter name (matches protocol parameter)
- `ptype` - Parameter type
- `label` - Display label
- `units` - Unit string

### STSequenceGlobalParameter (`stsequence.h`)
Global parameter with multiple connections:
- `name` - Parameter name
- `connections` - List of connected parameter paths

---

## Typical Workflow

### 1. Define Sequence Class
```cpp
class MySequence : public STSequence {
public:
    STReal TR;
    STReal TE;
    STInteger num_slices;
    
    void setup() {
        // Define parameters
        ST_PARAMETER(STReal, TR, 1000, ms)
        ST_PARAMETER(STReal, TE, 30, ms)
        ST_PARAMETER(STInteger, num_slices, 10, )
        
        // Create sequence structure
        ST_CHILD(MyLoop, acquisition_loop)
        // ... add more children
    }
};
```

### 2. Initialize and Run
```cpp
MySequence seq;
STScanner* scanner = new VendorSpecificScanner();
seq.setScanner(scanner);
seq.initialize();
seq.run();
```

### 3. Execution Flow
1. `initialize()` - Prepare sequence tree
2. `run()` - Execute sequence
   - Calls `beginSequence()` on scanner
   - Iterates through loops
   - For each block: `beginBlock()`, add events, `endBlock()`
   - Calls `endSequence()` on scanner

---

## Key Concepts for MRI Scientists

### Timing
- All times in **microseconds (µs)**
- Nodes have relative start times within parent
- Absolute times calculated by traversing tree
- Reference times used for alignment (e.g., echo center)

### Gradient Moments
- Units: **(mT/m)·µs** or equivalently **(µT/mm)·µs**
- Represents k-space trajectory
- `initialMoment` = k-space position at node start
- `terminalMoment` = k-space position at node end
- Used for gradient balancing and k-space navigation

### k-space and FOV
- `kspace2moment()` converts k-space position to gradient moment
- FOV in mm, gradient moments in (mT/m)·µs
- Gyromagnetic ratio γ = 42.5764 Hz/µT for ¹H

### SAR Calculation
- RF pulse SAR computed from B₁² × time
- Accumulated through tree hierarchy
- Units depend on implementation

### Phase Adjustment
- Accounts for FOV shifts via gradient moments
- `phaseAdjustment()` = ∫(G·shift)·γ·360°

### Iterators and Loops
- `STIterator` defines parameter sweep: min:step:max
- Loops iterate over k-space lines, slices, averages
- Nested loops create multi-dimensional acquisitions

---

## File Organization

| File | Purpose |
|------|---------|
| `st4.h` | Main include file (includes all framework headers) |
| `stobject.h/cpp` | Base object class |
| `stnode.h/cpp` | Tree node class |
| `stparameter.h/cpp` | Parameter types and Vector3 |
| `stloop.h/cpp` | Loop iteration node |
| `stsequence.h/cpp` | Root sequence class |
| `stscanner.h/cpp` | Hardware abstraction and events |
| `stresources.h/cpp` | Resource management |
| `sstring.h/cpp` | String utility class |
| `slist.h` | List utility template |

---

## Usage for AI Coding Tools

When working with SequenceTree:

1. **Include `st4.h`** to access all framework classes
2. **Inherit from `STSequence`** to create new sequences
3. **Override `setup()`** to define sequence structure using macros
4. **Use `ST_CHILD()` macro** to create child nodes
5. **Use `ST_PARAMETER()` macro** to define parameters
6. **Units**: Time=µs, Gradient=mT/m, FOV=mm, Phase=degrees, Frequency=Hz
7. **Gradient moments** in (mT/m)·µs for k-space navigation
8. **Tree structure**: Sequence → Loops → Blocks → Events
9. **Vendor abstraction**: Inherit from `STScanner` for hardware-specific implementation
10. **Parameter files**: Use `loadParametersFromFile()` to configure sequences

---

## Export Macro

`ST_EXPORT` - Used for Windows DLL export/import
- Defined as `__declspec(dllexport)` when building library on Windows
- Empty on other platforms
