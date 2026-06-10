#!/usr/bin/env python3
"""Use DingTalk REST API via dws api with stdin"""
import subprocess, json, sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

with open(r"D:\OpenClaw\workspace\UE4用户访谈26.6.4_整理版.md", "r", encoding="utf-8") as f:
    content = f.read()

print("Content size:", len(content))

workspace_id = "xMEGYeVpbE4dpGoQ"
doc_id = "Gl6Pm2Db8D3PxMMAT9Bbe2yjJxLq0Ee4"
body = json.dumps({"content": content})

# Pipe body via stdin
p = subprocess.Popen(
    ["dws", "api", "PUT",
     "/v1.0/doc/spaces/{}/documents/{}/content".format(workspace_id, doc_id),
     "--data", "-",
     "--format", "json"],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
)
stdout, stderr = p.communicate(input=body.encode("utf-8"), timeout=60)
print("stdout:", stdout.decode("utf-8", errors="replace")[:500])
print("stderr:", stderr.decode("utf-8", errors="replace")[:500])
print("rc:", p.returncode)
