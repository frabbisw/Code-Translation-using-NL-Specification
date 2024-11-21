import os
import subprocess

roots = ["outputs/nl_only", "outputs/src_nl", "outputs/repair_nl_only", "outputs/repair_src_nl"]
orgs = ["before-nl-only", "before-src-nl", "after-nl-only", "after-src-nl"]

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