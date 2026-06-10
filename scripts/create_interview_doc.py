#!/usr/bin/env python3
"""Create DingTalk doc from extracted interview data"""
import subprocess, json, sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

with open(r"D:\OpenClaw\workspace\UE4用户访谈26.6.4_整理版.md", "r", encoding="utf-8") as f:
    content = f.read()

print("Content length:", len(content))

# Create doc via dws CLI
result = subprocess.run(
    ["dws", "doc", "create",
     "--name", "【整理版】UE4用户访谈26.6.4",
     "--workspace", "xMEGYyZb8PBgGoQv",
     "--markdown", content,
     "--format", "json"],
    capture_output=True, text=True, encoding="utf-8", errors="replace",
)

if result.returncode != 0:
    print("FAILED:")
    print("  stderr:", result.stderr[:500])
    print("  stdout:", result.stdout[:500])
    sys.exit(1)

data = json.loads(result.stdout)
print("SUCCESS:", json.dumps(data, ensure_ascii=False)[:300])

# Extract the doc URL
doc_url = data.get("docUrl", "")
if doc_url:
    print("\n文档链接:", doc_url)
