# Docker Development Environment

Documentation on the purpose, configuration, and libraries pre-installed in the workspace Docker environment.

---

## 1. Role of the Docker Environment
Because MRI sequence simulation relies on specific mathematical and graphical software libraries, the workspace is packaged with a pre-configured Docker image (`sequencetree_env:base`).

This container serves two roles:
* **For Humans (Interactive GUI)**: Allows compiling and launching the full Qt5 SequenceTree GUI application on both macOS (via XQuartz bridge) and Linux (via direct X11 sockets) without manual dependency installs.
* **For AI Agents (Headless Sandbox)**: Provides a stable execution environment containing the compilation toolchain (g++, qmake, make) and libraries (GSL, FFTW) necessary to build the simulator binaries headlessly.

---

## 2. Pre-installed Libraries & Toolchain
The Docker environment guarantees the presence of:
* **Qt5 Core/Widgets**: Necessary to compile the simulator engine.
* **GNU Scientific Library (GSL)**: Used for physical vector math and numeric integration in Bloch-equation calculations.
* **FFTW3**: Utilized for Fast Fourier Transforms during raw signal reconstruction.
* **GCC / Build Essentials**: Toolchain used to compile custom classes dynamically.

---

## 3. How the Host Workspace is Mounted
When launched via development scripts, the container executes with the following flags:
* `-v "$(pwd)":/st_workspace`: Mounts the host workspace root directory directly to `/st_workspace` inside the container. All compilation or simulation output writes straight back to the host filesystem.
* `--user "$(id -u):$(id -g)"`: Matches host file ownership to prevent permission errors when agents write files.

---

## 4. Run Scripts comparison
* **[dev.sh](file:///dev.sh)**: Designed for **human developers**. Spins up the container interactively with pseudo-TTY allocation (`-it`) and binds X11 routing variables to forward visual windows to the host display.
* **[run_in_docker.sh](file:///agentic_coding/run_in_docker.sh)**: Designed for **AI agents**. Drops pseudo-TTY allocation (`-it` -> `-i`) to prevent command execution stalls, bypasses X11 socket bindings if headless, and shares the host network namespace (`--net=host`) to keep long-lived API model streaming streams stable.

---

## 5. ⚠️ Never Write Output Files to `/tmp`

The Docker container mounts **only the workspace root** (`$(pwd)`) to `/st_workspace`. Any path
outside this mount — including `/tmp` — is **ephemeral**: it exists only for the lifetime of that
container invocation and is silently lost when the container exits.

This is the most common cause of "file not found" errors immediately after a Docker run:

```bash
# ❌ WRONG — /tmp is inside the container; file disappears on exit
./bin/simulator check seq.sts /tmp/out.sts /tmp/sim.dat /tmp/results.txt -1 -1
cat /tmp/results.txt   # No such file or directory

# ✅ CORRECT — write to a path inside the mounted workspace
bash agentic_coding/simulate.sh check agentic_coding/sequences/seq.sts
# simulate.sh automatically writes outputs alongside the input .sts file
```

Always write output files to workspace-relative paths (under `/agentic_coding/` or `/.agents/`).
The `simulate.sh` wrapper enforces this automatically.
