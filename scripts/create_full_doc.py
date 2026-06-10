#!/usr/bin/env python3
"""Use dws api to update DingTalk doc content"""
import subprocess, json, sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# Read the markdown file
with open(r"D:\OpenClaw\workspace\UE4用户访谈26.6.4_整理版.md", "r", encoding="utf-8") as f:
    content = f.read()

# Create a new doc with markdown content via dws doc create
# Use Python subprocess with PIPE to bypass cmd line length limit
import subprocess as sp

# Delete the old doc first
sp.run(["dws", "doc", "delete", "--node", "Gl6Pm2Db8D3PxMMAT9Bbe2yjJxLq0Ee4", "--yes", "--format", "json"],
    capture_output=True)

# Create a new doc with full content via dws doc create --markdown
# Since --markdown takes a string and cmd line is limited, 
# write the script to call dws with args programmatically
result = sp.run(
    ["dws", "doc", "create",
     "--name", "【整理版】UE4用户访谈26.6.4",
     "--markdown", content,
     "--format", "json"],
    capture_output=True, text=True, encoding="utf-8", errors="replace",
    timeout=60
)

print("stdout:", result.stdout[:500])
print("stderr:", result.stderr[:300])
print("rc:", result.returncode)

if result.returncode == 0:
    data = json.loads(result.stdout)
    print("\nSUCCESS! Doc URL:", data.get("docUrl", ""))
