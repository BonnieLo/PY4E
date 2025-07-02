import os
import re
from collections import defaultdict

def analyze_cpp_stl_usage(base_path):
    # Regular expression to find all std::Xxx usages
    stl_pattern = re.compile(r"\bstd::\w+\b")

    # Dictionary to hold the result
    stl_usage = defaultdict(lambda: {"count": 0, "locations": []})

    # Traverse directory for .cpp, .hpp, .h, .cc, .cxx files
    for root, dirs, files in os.walk(base_path):
        for file in files:
            if file.endswith((".cpp", ".hpp", ".h", ".cc", ".cxx")):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        for idx, line in enumerate(f, 1):
                            matches = stl_pattern.findall(line)
                            for match in matches:
                                stl_usage[match]["count"] += 1
                                rel_path = os.path.relpath(file_path, base_path)
                                if len(stl_usage[match]["locations"]) < 3:
                                    stl_usage[match]["locations"].append(f"{rel_path}:{idx}")
                except Exception as e:
                    print(f"Error reading file {file_path}: {e}")

    # Convert to list of records for display
    result = []
    for stl_type, data in stl_usage.items():
        result.append({
            "STL_Type": stl_type,
            "Count": data["count"],
            "Sample_Location": data["locations"][:3]  # Show only top 3 sample locations
        })

    return result

# Example usage
repo_directory = "/Users/bonnie/Documents/program/libpldm"  # Replace with your local path
stl_data = analyze_cpp_stl_usage(repo_directory)

import pandas as pd

df = pd.DataFrame(stl_data)
#print(df.to_string(index=False))
df.to_csv("stl_usage_summary.csv", index=False)  # 產出 CSV