#!/usr/bin/env python3
"""Check git status for both repos"""
import subprocess, os, sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

for name, path in [("OpenClaw workspace", r"D:\OpenClaw\workspace"), ("MyAgents", r"D:\MyAgents")]:
    git_dir = os.path.join(path, ".git")
    if not os.path.isdir(git_dir):
        print("=== {} === NO GIT".format(name))
        continue
    
    print("\n=== {} ===".format(name))
    
    # Status
    r = subprocess.run(["git", "status", "--short"], cwd=path, capture_output=True, text=True, encoding="utf-8", errors="replace")
    output = r.stdout.strip()
    if not output:
        print("(clean)")
        continue
    
    # Parse changes
    modified = []
    untracked = []
    deleted = []
    for line in output.split("\n"):
        line = line.strip()
        if not line:
            continue
        if line.startswith("??"):
            untracked.append(line[2:].strip())
        elif line.startswith("M") or " M " in line or line.startswith("A"):
            modified.append(line[2:].strip() if line[1] == " " else line[3:].strip())
        elif line.startswith("D") or " D " in line:
            deleted.append(line[2:].strip() if line[1] == " " else line[3:].strip())
    
    if modified:
        print("\n-- Modified: --")
        for f in modified:
            print("  M  {}".format(f))
    if deleted:
        print("\n-- Deleted: --")
        for f in deleted:
            print("  D  {}".format(f))
    if untracked:
        print("\n-- Untracked: --")
        for f in sorted(untracked):
            print("  ?? {}".format(f))
    
    # Branches
    r = subprocess.run(["git", "branch", "--merged"], cwd=path, capture_output=True, text=True, encoding="utf-8")
    merged = [b.strip() for b in r.stdout.split("\n") if b.strip() and not b.strip().startswith("*") and not b.strip() == "master"]
    if merged:
        print("\n-- Merged branches (candidates to delete): --")
        for b in merged:
            print("  {}".format(b))
