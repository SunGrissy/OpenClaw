#!/usr/bin/env python3
"""Check doc rendering v2"""
import subprocess, json, sys

if hasattr(sys.stdout,"reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8",errors="replace")

for node in ["YndMj49yWjPGellDhwOL1gm3J3pmz5aA","vy20BglGWOe9kxxgc0Lx4eDQJA7depqY"]:
    r = subprocess.run(["dws","doc","read","--node",node,"--format","json"],capture_output=True)
    d = json.loads(r.stdout.decode("utf-8",errors="replace"))
    md = d.get("markdown","")
    print("=== {} ===".format(node[:15]))
    for line in md.split("\n")[:20]:
        if line.strip():
            print(repr(line))
    print()
