import os
import subprocess

roots = ["outputs/lit/fix-0", "outputs/lit/fix-1"]
orgs = ["lit-before", "lit-after"]

for i, root in enumerate(roots):
    files = [f for f in os.listdir(root) if f.startswith("details") and f.endswith(".json")]
    # print(files)
    for file in files:
        with open(f"{root}/{file}", "r") as f:
            code = f.read()
            if len(code) < 5:
                print(root, file)
                # print(file.split("_"))
                _, dataset, src, target, __ = file.split("_")
                result = subprocess.run(["python", "get_info.py", "G", dataset, src, target, root, orgs[i]], capture_output=True, text=True)
                if result.returncode == 0:
                    print(f"Command executed successfully. Output:\n{result.stdout}")
                else:
                    print(f"Command failed with error:\n{result.stderr}")