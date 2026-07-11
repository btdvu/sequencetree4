#!/usr/bin/env python3
import sys
import os

def convert_sts(sts_path, out_path):
    if not os.path.exists(sts_path):
        print(f"Error: {sts_path} does not exist")
        sys.exit(1)
        
    with open(sts_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Find the NODES block
    start_tag = "++++++ NODES ++++++"
    if start_tag not in content:
        print("Error: NODES tag not found in sequence file")
        sys.exit(1)
        
    nodes_idx = content.find(start_tag) + len(start_tag)
    end_idx = content.find("++++++", nodes_idx)
    nodes_content = content[nodes_idx:end_idx].strip()
    
    out_lines = []
    for line in nodes_content.splitlines():
        line = line.strip()
        if not line:
            continue
        tokens = line.split("\t")
        tokens = [t.strip() for t in tokens if t.strip()]
        if not tokens:
            continue
        
        cmd = tokens[0]
        if cmd == "PARAMETER":
            # format: PARAMETER TYPE NAME VALUE
            pname = tokens[2]
            pval = tokens[3]
            out_lines.append(f"PARAM\t{pname}\t{pval}\tactive")
        elif cmd == "CHILD":
            # format: CHILD TYPE NAME
            cname = tokens[2]
            ctype = tokens[1]
            out_lines.append(f"CHILD\t{cname}\t{ctype}")
        elif cmd == "END":
            out_lines.append("ENDCHILD")
            
    # Create parent directories if they do not exist
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(out_lines) + "\n")
    print(f"Parameters converted and saved to {out_path}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: convert_sts_to_params.py [input_sequence.sts] [output_params.sts]")
        sys.exit(1)
    convert_sts(sys.argv[1], sys.argv[2])
