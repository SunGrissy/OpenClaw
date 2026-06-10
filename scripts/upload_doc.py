#!/usr/bin/env python3
"""Create doc with stdin content"""
import subprocess, sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

with open(r"D:\OpenClaw\workspace\UE4用户访谈26.6.4_整理版.md", "rb") as f:
    content = f.read()

print("Content size:", len(content), "bytes")

# Try piping via stdin with --content-file -
# First create a temp doc, then try updating with stdin
p = subprocess.Popen(
    ["dws", "doc", "update",
     "--node", "Gl6Pm2Db8D3PxMMAT9Bbe2yjJxLq0Ee4",
     "--content-file", "-",
     "--format", "json"],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
)
stdout, stderr = p.communicate(input=content)
print("stdout:", stdout.decode("utf-8", errors="replace")[:500])
print("stderr:", stderr.decode("utf-8", errors="replace")[:500])
print("rc:", p.returncode)
