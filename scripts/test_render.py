#!/usr/bin/env python3
"""Check doc rendering"""
import subprocess, json, sys

if hasattr(sys.stdout,"reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8",errors="replace")

r = subprocess.run(["dws","doc","read","--node","YndMj49yWjPGellDhwOL1gm3J3pmz5aA","--format","json"],
    capture_output=True)
text = r.stdout.decode("utf-8",errors="replace")
try:
    d = json.loads(text)
    md = d.get("markdown","")
    for line in md.split("\n")[:25]:
        if line.strip():
            print(repr(line))
except:
    print(text[:1000])
