import os
import subprocess
import sys

root = sys.argv[1]
org = sys.argv[2] 

src_dir = sys.argv[1]
tgt_path = sys.argv[2]
organization = sys.argv[3]
project_key = sys.argv[4]

print(f"checking missing file {tgt_path}")

with open(f"{tgt_path}_details.json", "r") as f:
    code = f.read()
if len(code) < 5:
    print(f"missing: {tgt_path}")
    print("fetching again ...")
    result = subprocess.run(["python", "get_info.py", src_dir, tgt_path, organization, project_key], capture_output=True, text=True)
    if result.returncode == 0:
        print(f"Command executed successfully. Output:\n{result.stdout}")
    else:
        print(f"Command failed with error:\n{result.stderr}")
else:
    print("file is okay!")
