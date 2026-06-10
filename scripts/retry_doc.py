#!/usr/bin/env python3
"""Use dws api to call DingTalk doc API directly"""
import subprocess, json, sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# Read the markdown file
with open(r"D:\OpenClaw\workspace\UE4用户访谈26.6.4_整理版.md", "r", encoding="utf-8") as f:
    content = f.read()

# Try calling the DingTalk doc API directly via dws api
# The API is likely PUT /v1.0/doc/spaces/documents/{documentId}/content
# Or use the doc update API

# Actually, let me try creating the doc from scratch with --markdown via stdin
# Use a temp approach: write content to a temp location and pipe

# Actually, the simplest: just use dws doc create --markdown with a short content
# to create a doc, and upload the full file separately

# Upload the .md file as a document
# dws doc upload doesn't take a file path...

# Let me try a hack: write the content to a file and use subprocess with stdin
import tempfile

# Write content to a temp file, then delete the old doc and create new one
result = subprocess.run(
    ["dws", "doc", "delete", "--node", "Gl6Pm2Db8D3PxMMAT9Bbe2yjJxLq0Ee4", "--yes"],
    capture_output=True, text=True, encoding="utf-8", errors="replace"
)
print("Delete:", result.stdout[:100], result.stderr[:100])

# Now create with pipe approach - use Python subprocess with stdin
# Actually dws doc create --markdown doesn't support stdin
# Let's try: create a minimal doc, then use dws api to update the content

# Create minimal doc
result = subprocess.run(
    ["dws", "doc", "create", "--name", "【整理版】UE4用户访谈26.6.4", "--format", "json"],
    capture_output=True, text=True, encoding="utf-8", errors="replace"
)
print("Create:", result.stdout[:200])

if result.returncode == 0:
    data = json.loads(result.stdout)
    doc_url = data.get("docUrl", "")
    print("New doc URL:", doc_url)
