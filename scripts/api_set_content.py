#!/usr/bin/env python3
"""Use DingTalk REST API to set document content via dws api"""
import subprocess, json, sys, os

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

with open(r"D:\OpenClaw\workspace\UE4用户访谈26.6.4_整理版.md", "r", encoding="utf-8") as f:
    content = f.read()

print("Content size:", len(content))

# Try using dws api to set document content
# The API path: PUT /v1.0/doc/spaces/{workspaceId}/documents/{documentId}/content
# Body: {"content": "markdown text"}

workspace_id = "xMEGYeVpbE4dpGoQ"
doc_id = "Gl6Pm2Db8D3PxMMAT9Bbe2yjJxLq0Ee4"

body = json.dumps({"content": content})

# Write body to a temp file to avoid cmd line limit
tmpfile = os.path.join(os.path.dirname(__file__), "_tmp_body.json")
with open(tmpfile, "w", encoding="utf-8") as f:
    f.write(body)

# Use dws api with POST/PUT
api_path = "/v1.0/doc/spaces/{}/documents/{}/content".format(workspace_id, doc_id)

result = subprocess.run(
    ["dws", "api", "PUT", api_path, "--data", "@" + tmpfile, "--format", "json"],
    capture_output=True, text=True, encoding="utf-8", errors="replace",
    timeout=60
)

print("stdout:", result.stdout[:500])
print("stderr:", result.stderr[:300])

# Clean up
try:
    os.remove(tmpfile)
except:
    pass

if result.returncode == 0:
    data = json.loads(result.stdout)
    print("\nSUCCESS:", json.dumps(data, ensure_ascii=False)[:500])
else:
    print("FAILED. Trying alternative approach...")
    # Maybe the endpoint is different
    api_path2 = "/v1.0/doc/spaces/{}/documents/{}/markdown".format(workspace_id, doc_id)
    result = subprocess.run(
        ["dws", "api", "PUT", api_path2, "--data", "@" + tmpfile, "--format", "json"],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        timeout=60
    )
    print("Alt stdout:", result.stdout[:500])
    print("Alt stderr:", result.stderr[:300])
