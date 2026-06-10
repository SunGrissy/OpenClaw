#!/usr/bin/env python3
import subprocess, json, sys
if hasattr(sys.stdout,"reconfigure"): sys.stdout.reconfigure(encoding="utf-8",errors="replace")

r = subprocess.run(["dws","doc","read","--node","93NwLYZXWygK4xxRFZ4L7nO7JkyEqBQm","--format","json"],capture_output=True)
d = json.loads(r.stdout.decode("utf-8",errors="replace"))
for line in d.get("markdown","").split("\n")[:15]:
    if line.strip():
        print(repr(line))
