import sys
import os
import subprocess

def extract_and_build(sts_path, simulator_dir="simulator"):
    print(f"Reading {sts_path}...")
    if not os.path.exists(sts_path):
        print(f"Error: {sts_path} does not exist.")
        return False
        
    with open(sts_path, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()
        
    classes = {}
    current_class = None
    section = None
    
    for line in lines:
        line_stripped = line.strip()
        if line_stripped.startswith("++++++ USERCLASS") or line_stripped.startswith("++++++ CLASS"):
            parts = line_stripped.split()
            if len(parts) >= 3:
                current_class = parts[2]
                classes[current_class] = {"header": [], "source": []}
                section = None
        elif line_stripped.startswith("++++++ HEADER"):
            section = "header"
        elif line_stripped.startswith("++++++ SOURCE"):
            section = "source"
        elif line_stripped.startswith("++++++ END"):
            current_class = None
            section = None
        elif current_class and section:
            classes[current_class][section].append(line)
            
    if not classes:
        print("No custom USERCLASS or CLASS sections found in the .sts file.")
        return False
        
    # Write customclasses.h
    header_path = os.path.join(simulator_dir, "customclasses.h")
    print(f"Writing {header_path}...")
    with open(header_path, "w", encoding="utf-8") as f:
        f.write("#ifndef customclasses_H\n#define customclasses_H\n\n#include \"foundationclasses.h\"\n\n")
        for cname in classes.keys():
            f.write(f"class {cname};\n")
        f.write("\n")
        for cname, data in classes.items():
            f.write(f"////// {cname} //////\n")
            f.write("".join(data["header"]))
            f.write("\n\n")
        f.write("#endif\n")
        
    # Write customclasses.cpp
    source_path = os.path.join(simulator_dir, "customclasses.cpp")
    print(f"Writing {source_path}...")
    with open(source_path, "w", encoding="utf-8") as f:
        f.write("#include \"customclasses.h\"\n\n")
        for cname, data in classes.items():
            f.write(f"////// {cname} //////\n")
            f.write("".join(data["source"]))
            f.write("\n\n")
            
    # Write clean createsequence.cpp
    createseq_path = os.path.join(simulator_dir, "createsequence.cpp")
    print(f"Writing {createseq_path}...")
    with open(createseq_path, "w", encoding="utf-8") as f:
        f.write("""#include "createsequence.h"
#include "foundationclasses.h"
#include "customclasses.h"
#include "loadparametersfile.h"
#include <string.h>

STSequence *createSequence(char *parameter_fname) {
\tSTRoot *Root = new STRoot;
\tif (parameter_fname) {
\t\tRoot->loadParametersFromFile(parameter_fname);
\t}
\telse {
\t\tSString parameter_txt;
\t\tloadParametersFile(parameter_txt);
\t\tRoot->loadParametersFromText(parameter_txt);
\t}
\tSString resource_text;
\tloadResourceText(resource_text);
\tRoot->resources()->readFromText(resource_text);
\treturn Root;
}

void getSequenceName(char *ret) {
\tstrcpy(ret, "sequence_name");
}

bool setGlobalParameter(STSequence *Seq, SString pname, SString pval) {
\treturn true;
}

int uiParameterCount() { return 0; }
const char *uiParameterName(int index) { return ""; }
const char *uiParameterLabel(int index) { return ""; }
const char *uiParameterType(int index) { return ""; }
const char *uiParameterUnits(int index) { return ""; }
double uiParameterMin(int index) { return 1; }
double uiParameterMax(int index) { return 10; }
double uiParameterStep(int index) { return 1; }
double uiParameterFactor(int index) { return 1; }
const char *uiParameterDefault(int index) { return "1"; }
int getResolution() { return 0; }
""")

    # Write clean loadparametersfile.cpp
    loadparam_path = os.path.join(simulator_dir, "loadparametersfile.cpp")
    print(f"Writing {loadparam_path}...")
    with open(loadparam_path, "w", encoding="utf-8") as f:
        f.write("""#include "loadparametersfile.h"
void loadParametersFile(SString &ret) {
\tret = "";
}
void loadResourceText(SString &ret) {
\tret = "";
}
""")
            
    # Trigger qmake and make in simulator directory
    print("Compiling simulator...")
    # Clean previous builds to avoid caching issues
    subprocess.run(["make", "clean"], cwd=simulator_dir, capture_output=True)
    
    result = subprocess.run(["qmake"], cwd=simulator_dir, capture_output=True, text=True)
    if result.returncode != 0:
        print("qmake failed:", result.stderr)
        return False
        
    result = subprocess.run(["make"], cwd=simulator_dir, capture_output=True, text=True)
    if result.returncode != 0:
        print("make failed:")
        print(result.stderr)
        print(result.stdout)
        return False
        
    print("Build successful! Binary compiled in bin/simulator")
    return True

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 extract_and_build.py [path_to_sts_file]")
        sys.exit(1)
    
    success = extract_and_build(sys.argv[1])
    sys.exit(0 if success else 1)
