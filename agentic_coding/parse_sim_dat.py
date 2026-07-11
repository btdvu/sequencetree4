#!/usr/bin/env python3
"""
parse_sim_dat.py — SequenceTree simulation output parsers.

Provides two top-level functions that can be imported or run directly:
  - parse_simulation_dat(file_path, verbose=True) -> list[dict]
      Parses the binary waveform output written by `simulator run` (sim.dat).
      Returns a list of block dicts, each with an 'events' list of event dicts.

  - parse_raw_template(file_path, verbose=True) -> list[dict]
      Parses the logical execution template written by `simulator raw_template`
      (sim_raw.dat). Returns a list of decoded command dicts.

Event type codes: 1=RF, 2=Readout, 3=Gradient, 4=ArbGradient

Usage (as a script):
    python3 agentic_coding/parse_sim_dat.py sim.dat          # waveform
    python3 agentic_coding/parse_sim_dat.py sim_raw.dat raw  # template
"""

import struct
import sys
import math

EVENT_TYPES = {1: "RF", 2: "Readout", 3: "Gradient", 4: "ArbGradient"}
GRAD_AXES   = {1: "X", 2: "Y", 3: "Z"}


# ---------------------------------------------------------------------------
# 1. Waveform parser  (sim.dat / sim_filtered.dat)
# ---------------------------------------------------------------------------

def parse_simulation_dat(file_path, verbose=True):
    """
    Parse a sim.dat binary file produced by `simulator run`.

    Returns
    -------
    blocks : list[dict]
        Each block dict has keys:
          block_num, duration, elapsed_time, num_events, events

        Each event dict has keys:
          block_idx, tree_idx, event_type, event_type_name,
          start_time, duration, reference_time, timestep, phase, frequency,
          rf_points,          # list of (mag, phase) tuples  — empty if not RF
          readout_num_points, readout_online_adc,
          grad_axis, grad_times, grad_amps   # lists — empty if no gradient
    """
    blocks = []
    with open(file_path, "rb") as f:

        # --- Global header ---
        max_rf, num_blocks = struct.unpack("=dq", f.read(16))
        if verbose:
            print(f"=== sim.dat: Max RF={max_rf:.4f} uT | Total Blocks={num_blocks} ===\n")

        for _ in range(num_blocks):

            # --- Block header (33 bytes) ---
            duration, block_num, elapsed, trigger, num_events = \
                struct.unpack("=dqdbq", f.read(33))

            if verbose:
                print(f"--- Block #{block_num} | duration={duration:.1f} us "
                      f"({duration/1000:.3f} ms) | elapsed={elapsed:.1f} us "
                      f"| events={num_events} ---")

            block = dict(block_num=block_num, duration=duration,
                         elapsed_time=elapsed, num_events=num_events, events=[])

            for e in range(num_events):

                # --- Event header (60 bytes) ---
                block_idx, tree_idx, event_type, \
                    start, dur, ref, step, phase, freq = \
                    struct.unpack("=iiidddddd", f.read(60))

                type_name = EVENT_TYPES.get(event_type, f"Unknown({event_type})")

                if verbose:
                    print(f"  [{e}] {type_name:12s} "
                          f"start={start:.1f} us  dur={dur:.1f} us  "
                          f"ref={ref:.1f} us  step={step:.1f} us  "
                          f"phase={phase:.2f} deg  freq={freq:.2f} Hz")

                event = dict(
                    block_idx=block_idx, tree_idx=tree_idx,
                    event_type=event_type, event_type_name=type_name,
                    start_time=start, duration=dur, reference_time=ref,
                    timestep=step, phase=phase, frequency=freq,
                    rf_points=[],
                    readout_num_points=0, readout_online_adc=False,
                    grad_axis=None, grad_times=[], grad_amps=[],
                )

                # --- RF segment (always present; num_rf_pts=0 if not an RF event) ---
                num_rf_pts, = struct.unpack("=q", f.read(8))
                for _ in range(num_rf_pts):
                    mag, ph = struct.unpack("=dd", f.read(16))
                    event["rf_points"].append((mag, ph))
                if verbose and num_rf_pts > 0:
                    peak = max(x[0] for x in event["rf_points"])
                    print(f"       RF: {num_rf_pts} pts, peak={peak:.4f} uT")

                # --- Readout segment (always 65 bytes) ---
                ro_data = struct.unpack("=qB" + "i" * 14, f.read(65))
                event["readout_num_points"] = ro_data[0]
                event["readout_online_adc"] = bool(ro_data[1])
                if verbose and ro_data[0] > 0:
                    print(f"       Readout: N={ro_data[0]}  onlineADC={bool(ro_data[1])}")

                # --- Gradient segment (always present; num_times=0 if no gradient) ---
                direction, num_grad_pts = struct.unpack("=iq", f.read(12))
                for _ in range(num_grad_pts):
                    t_val, a_val = struct.unpack("=dd", f.read(16))
                    event["grad_times"].append(t_val)
                    event["grad_amps"].append(a_val)
                if num_grad_pts > 0:
                    event["grad_axis"] = GRAD_AXES.get(direction, str(direction))
                    if verbose:
                        peak_amp = max((a for a in event["grad_amps"]
                                        if not math.isnan(a)), default=float("nan"))
                        print(f"       Gradient {event['grad_axis']}: "
                              f"{num_grad_pts} pts, peak={peak_amp:.4f} uT/mm")

                block["events"].append(event)

            if verbose:
                print()
            blocks.append(block)

    return blocks


# ---------------------------------------------------------------------------
# 2. Raw template parser  (sim_raw.dat)
# ---------------------------------------------------------------------------

def parse_raw_template(file_path, verbose=True):
    """
    Parse a sim_raw.dat binary file produced by `simulator raw_template`.

    Returns
    -------
    commands : list[dict]
        Each dict has a 'code' key and type-specific payload keys:
          code=5  → adc_index, num_points
          code=10 → op="Init",  iterator_index
          code=15 → op="Step",  iterator_index
          code=20 → op="Reset", iterator_index
          code=25 → adc_index, iterator_index, value
    """
    OP = {10: "Init", 15: "Step", 20: "Reset"}
    commands = []
    with open(file_path, "rb") as f:
        while True:
            raw = f.read(4)
            if not raw:
                break
            code, = struct.unpack("=i", raw)

            if code == 5:
                adc, n = struct.unpack("=ii", f.read(8))
                cmd = dict(code=code, adc_index=adc, num_points=n)
                if verbose:
                    print(f"Readout: ADC={adc}, Points={n}")

            elif code in (10, 15, 20):
                iter_idx, = struct.unpack("=i", f.read(4))
                cmd = dict(code=code, op=OP[code], iterator_index=iter_idx)
                if verbose:
                    print(f"Iterator {OP[code]}: Index={iter_idx}")

            elif code == 25:
                num_bytes, = struct.unpack("=i", f.read(4))
                adc, iter_idx, val = struct.unpack("=iii", f.read(num_bytes))
                cmd = dict(code=code, adc_index=adc, iterator_index=iter_idx, value=val)
                if verbose:
                    print(f"Set Readout Index: ADC={adc}, Iterator={iter_idx}, Val={val}")

            else:
                if verbose:
                    print(f"[WARN] Unknown code: {code}")
                cmd = dict(code=code)

            commands.append(cmd)

    return commands


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    file_path = sys.argv[1]
    mode = sys.argv[2] if len(sys.argv) > 2 else "waveform"

    if mode == "raw":
        parse_raw_template(file_path, verbose=True)
    else:
        parse_simulation_dat(file_path, verbose=True)
