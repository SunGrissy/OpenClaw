#!/usr/bin/env python3
"""Verify doc has all sub-question answers"""
import subprocess, json, sys

if hasattr(sys.stdout,"reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8",errors="replace")

r = subprocess.run(["dws","doc","read","--node","20eMKjyp81R7k00At4RmordLWxAZB1Gv","--format","json"],
    capture_output=True)
text = r.stdout.decode("utf-8",errors="replace")

try:
    data = json.loads(text)
    md = data.get("markdown","")
    # Count question and answer lines
    q_count = md.count("**Q")
    b_count = md.count("**B")
    ans_lines = md.count("\n> ")
    print("Q headers: {} (main Qs: {}, B section: {})".format(q_count + b_count, q_count, b_count))
    print("Answer lines (>):", ans_lines)
    print("Total length:", len(md))
    print()
    # Print first 15 meaningful lines
    for line in md.split("\n")[:30]:
        if line.strip():
            print(line.strip()[:120])
except:
    print("Text preview:", text[:500])
