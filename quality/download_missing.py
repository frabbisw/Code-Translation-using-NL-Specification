import os
import subprocess
import sys

root = sys.argv[1]
org = sys.argv[2] 

files = [f for f in os.listdir(root) if f.startswith("details") and f.endswith(".json")]
for file in files:
    with open(f"{root}/{file}", "r") as f:
        code = f.read()
        if len(code) < 5:
            print(root, file)
            _, dataset, src, target, __ = file.split("_")
            result = subprocess.run(["python", "get_info.py", "G", dataset, src, target, root, org], capture_output=True, text=True)
            if result.returncode == 0:
                print(f"Command executed successfully. Output:\n{result.stdout}")
            else:
                print(f"Command failed with error:\n{result.stderr}")
