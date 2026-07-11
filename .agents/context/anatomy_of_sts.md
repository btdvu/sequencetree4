# Anatomy of an `.sts` File

An `.sts` file is the plain-text representation of a SequenceTree pulse sequence. It is split into distinct sections marked by `++++++ SECTION_NAME ++++++` and `++++++ END [SECTION_NAME] ++++++` delimiters.

## Key Sections:

1. **`++++++ HEADER ++++++`**: Contains the version of SequenceTree (e.g. `STVERSION=4.6.0`).
2. **`++++++ NOTES ++++++`**: Holds user-facing description notes and **Siemens User Interface Directives** (e.g. `UIDOUBLE`, `UICHECKBOX`) that map parameters to GUI controls.
3. **`++++++ GLOBAL ++++++`**: Declares global parameters (e.g., `FOV`, `TR`, `TE1`) and establishes mapping connections to child nodes in the tree hierarchy using `->` (e.g., `readout_N -> Root->MainLoop->Block->Acquire1->Readout->N`).
4. **`++++++ RECONSTRUCTION ++++++`**: Holds MATLAB-like code that defines how acquired raw data (MDA files) are reconstructed in the viewer.
5. **`++++++ NODES ++++++`**: Represents the serialization of the sequence tree layout (hierarchical parameters and child nodes).

   Each parameter line has the form:
   ```
   PARAMETER  <Type>  <Name>  <Value>  <units>  <active|passive>  [global_alias]
   ```
   * **`active`**: User-settable parameter. The GLOBAL section's `->` mappings flow into active
     parameters at runtime. These are what the C++ `prepare()` reads as inputs.
   * **`passive`**: Computed output. The GUI's `prepare()` writes its computed results back into
     passive parameters and serializes them into the NODES section as a cache. For a GUI-designed
     sequence, passive values (e.g. `Tacq`, `plateau_time`, `N`) are the **authoritative ground truth**
     and can be read directly from the `.sts` file without running the simulator.

6. **`++++++ USERCLASS / CLASS [Name] ++++++`**: Contains inline C++ header and source code for custom classes (e.g., custom loops or custom block chains).
7. **`++++++ RESOURCES ++++++`**: Holds binary or text-based waveform tables and pulse shape resources.
