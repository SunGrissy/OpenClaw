#!/usr/bin/env python3
"""Create DingTalk doc with content from file"""
import subprocess, sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# Read content
with open(r"D:\OpenClaw\workspace\UE4用户访谈26.6.4_整理版.md", "r", encoding="utf-8") as f:
    content = f.read()

# Use doc create with markdown directly via pipe/stdin approach
# Or: write to a temp file and use --content-file

# Approach 1: Use --content-file with the file path
result = subprocess.run(
    ["dws", "doc", "update",
     "--node", "Gl6Pm2Db8D3PxMMAT9Bbe2yjJxLq0Ee4",
     "--content-file", r"D:\OpenClaw\workspace\UE4用户访谈26.6.4_整理版.md",
     "--format", "json"],
    capture_output=True, text=True, encoding="utf-8", errors="replace",
    timeout=60
)

print("stdout:", result.stdout[:500])
if result.stderr:
    print("stderr:", result.stderr[:500])
print("rc:", result.returncode)

if result.returncode == 0:
    import json
    d = json.loads(result.stdout)
    print("\nDoc URL:", d.get("docUrl", "?"))

# If update didn't work, try recreating with a shorter approach
if result.returncode != 0:
    print("\nTrying alternative: delete and recreate...")
    # Delete old doc
    # Actually, let me just tell the user the file is ready
