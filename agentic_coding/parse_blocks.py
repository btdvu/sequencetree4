#!/usr/bin/env python3
"""
parse_blocks.py — Programmatic dumper for specific blocks and axes from sim.dat.

This utility helps avoid terminal stdout truncation on long sequences by extracting 
detailed timing and amplitude information for a targeted block and/or gradient axis.

Usage:
    python3 agentic_coding/parse_blocks.py <sim.dat_path> <block_num> [axis_filter]

Examples:
    python3 agentic_coding/parse_blocks.py agentic_coding/sequences/st_AUSFIDE_V4_Win10_toBrian_sim.dat 15999
    python3 agentic_coding/parse_blocks.py agentic_coding/sequences/st_AUSFIDE_V4_Win10_toBrian_sim.dat 15999 Z
"""

import sys
import os

# Ensure the agentic_coding module path is accessible
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from parse_sim_dat import parse_simulation_dat

def main():
    if len(sys.argv) < 3:
        print("Error: Missing arguments.")
        print(__doc__)
        sys.exit(1)

    sim_path = sys.argv[1]
    try:
        target_block_num = int(sys.argv[2])
    except ValueError:
        print("Error: block_num must be an integer.")
        sys.exit(1)

    axis_filter = sys.argv[3].upper() if len(sys.argv) > 3 else None

    if not os.path.exists(sim_path):
        print(f"Error: Waveform file '{sim_path}' not found.")
        sys.exit(1)

    # Load block structure headlessly
    blocks = parse_simulation_dat(sim_path, verbose=False)

    # Find the target block
    target_block = None
    for b in blocks:
        if b['block_num'] == target_block_num:
            target_block = b
            break

    if not target_block:
        available_blocks = [b['block_num'] for b in blocks]
        print(f"Error: Block {target_block_num} not found in the sim.dat file.")
        print(f"Available blocks in file: {available_blocks}")
        sys.exit(1)

    print(f"\n================ Block {target_block_num} ================")
    print(f"Duration: {target_block['duration']} us | Elapsed: {target_block['elapsed_time']} us | Events: {target_block['num_events']}")
    
    for i, ev in enumerate(target_block['events']):
        t_name = ev['event_type_name']
        axis = ev.get('grad_axis')

        # Filter by axis if requested
        if axis_filter and axis != axis_filter:
            continue

        print(f"\n  Event [{i}] {t_name}")
        print(f"    Start time: {ev['start_time']} us")
        print(f"    Duration  : {ev['duration']} us")
        
        if t_name == "RF" and ev['rf_points']:
            peak_rf = max(pt[0] for pt in ev['rf_points'])
            print(f"    RF Points : {len(ev['rf_points'])} pts | Peak: {peak_rf:.6f} uT")
            
        elif t_name == "Readout":
            print(f"    ADC Points: {ev['readout_num_points']} pts | Dwell: {ev['timestep']} us")
            
        elif t_name in ["Gradient", "ArbGradient"] and ev['grad_amps']:
            peak_amp = max(abs(amp) for amp in ev['grad_amps'])
            print(f"    Axis      : {axis}")
            print(f"    Peak Amp  : {peak_amp:.6f} uT/mm")
            print(f"    Breakpoints (Time): {ev['grad_times']}")
            print(f"    Breakpoints (Amp) : {ev['grad_amps']}")

if __name__ == "__main__":
    main()
