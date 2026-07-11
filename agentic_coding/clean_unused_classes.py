#!/usr/bin/env python3
import sys
import os
import re

def clean_unused_classes(sts_path, output_path):
    if not os.path.exists(sts_path):
        print(f"Error: {sts_path} does not exist")
        sys.exit(1)
        
    with open(sts_path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()
        
    # Parse blocks
    # Custom classes are defined between ++++++ CLASS Name ++++++ or ++++++ USERCLASS Name ++++++ and ++++++ END
    pattern = r"\+\+\+\+\+\+\s+(CLASS|USERCLASS)\s+(\w+)\s+\+\+\+\+\+\+(.*?)\+\+\+\+\+\+\s+END"
    matches = list(re.finditer(pattern, content, re.DOTALL))
    
    declared_classes = {}
    for m in matches:
        ctype = m.group(1)
        cname = m.group(2)
        body = m.group(3)
        start_pos = m.start()
        end_pos = m.end()
        declared_classes[cname] = {
            "type": ctype,
            "body": body,
            "full_text": m.group(0),
            "start": start_pos,
            "end": end_pos
        }
        
    print(f"Found {len(declared_classes)} declared custom classes.")
    
    # Parse the NODES block
    nodes_idx = content.find("++++++ NODES ++++++")
    if nodes_idx == -1:
        print("Error: NODES block not found")
        sys.exit(1)
    nodes_end_idx = content.find("++++++", nodes_idx + len("++++++ NODES ++++++"))
    nodes_text = content[nodes_idx:nodes_end_idx]
    
    # Find all instantiated class names in NODES (e.g. CHILD ClassName NodeName)
    instantiated_classes = set()
    for line in nodes_text.splitlines():
        line = line.strip()
        if line.startswith("CHILD"):
            tokens = line.split()
            if len(tokens) >= 2:
                instantiated_classes.add(tokens[1])
                
    print(f"Found {len(instantiated_classes)} instantiated classes in NODES.")
    
    # Reachability search
    # S = set of reachable custom classes
    reachable = set()
    queue = []
    
    # Initialize with instantiated custom classes and the STRoot container
    for cname in instantiated_classes:
        if cname in declared_classes:
            reachable.add(cname)
            queue.append(cname)
            
    if "STRoot" in declared_classes and "STRoot" not in reachable:
        reachable.add("STRoot")
        queue.append("STRoot")
            
    print(f"Initial reachable custom classes from NODES: {list(reachable)}")
    
    # BFS
    while queue:
        curr = queue.pop(0)
        curr_text = declared_classes[curr]["body"]
        
        # Check all other declared custom classes to see if they are referenced in curr
        for cname in declared_classes:
            if cname in reachable:
                continue
            # Use regex word boundaries to check if cname is referenced as a class type or variable
            if re.search(r'\b' + re.escape(cname) + r'\b', curr_text):
                reachable.add(cname)
                queue.append(cname)
                
    print(f"Total reachable custom classes: {len(reachable)}")
    print(f"Unused custom classes to remove: {len(declared_classes) - len(reachable)}")
    
    unused_classes = set(declared_classes.keys()) - reachable
    print(f"Removing unused: {sorted(list(unused_classes))}")
    
    # Reconstruct the file content by removing the unused classes blocks
    # We sort matches in descending order of start position to remove them without messing up indices
    sorted_matches = sorted([declared_classes[cname] for cname in unused_classes], key=lambda x: x["start"], reverse=True)
    
    new_content = content
    for item in sorted_matches:
        new_content = new_content[:item["start"]] + new_content[item["end"]:]
        
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(new_content)
    print(f"Cleaned sequence saved to {output_path}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: clean_unused_classes.py [input.sts] [output.sts]")
        sys.exit(1)
    clean_unused_classes(sys.argv[1], sys.argv[2])
