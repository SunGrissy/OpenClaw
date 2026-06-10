#!/usr/bin/env python3
"""Check git status for workspaces"""
import subprocess, os, sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

repos = [
    ("OpenClaw workspace", r"D:\OpenClaw\workspace"),
    ("MyAgents", r"D:\MyAgents"),
]

for name, path in repos:
    if not os.path.isdir(os.path.join(path, ".git")):
        print("=== {} === NO GIT REPO".format(name))
        continue
    print("\n=== {} ({}) ===".format(name, path))
    
    # Status
    r = subprocess.run(["git", "status", "--short"], cwd=path, capture_output=True, text=True, encoding="utf-8")
    print("--- git status --short ---")
    print(r.stdout.strip() or "(clean)")
    if r.stderr.strip():
        print("stderr:", r.stderr.strip())

    # Branches
    r = subprocess.run(["git", "branch", "-a"], cwd=path, capture_output=True, text=True, encoding="utf-8")
    branches = [b.strip() for b in r.stdout.split("\n") if b.strip()]
    print("\n--- branches ---")
    for b in branches:
        print("  {}".format(b))

    # Check merged branches
    r = subprocess.run(["git", "branch", "--merged"], cwd=path, capture_output=True, text=True, encoding="utf-8")
    merged = [b.strip() for b in r.stdout.split("\n") if b.strip() and not b.strip().startswith("*")]
    if merged:
        print("\n--- merged branches (candidates for deletion) ---")
        for b in merged:
            print("  {}".format(b))
    else:
        print("\n--- no merged branches besides current ---")

    # Remote branches merged
    r = subprocess.run(["git", "branch", "-r", "--merged"], cwd=path, capture_output=True, text=True, encoding="utf-8")
    r_merged = [b.strip() for b in r.stdout.split("\n") if b.strip() and "origin/HEAD" not in b]
    if r_merged:
        print("\n--- remote merged branches ---")
        for b in r_merged:
            print("  {}".format(b))

    # Untracked files
    r = subprocess.run(["git", "status", "--porcelain"], cwd=path, capture_output=True, text=True, encoding="utf-8")
    untracked = []
    modified = []
    for line in r.stdout.strip().split("\n"):
        if not line.strip():
            continue
        if line.startswith("??"):
            untracked.append(line[3:])
        elif line.startswith(" M") or line.startswith("M ") or line.startswith(" A"):
            modified.append(line[3:])
    if untracked:
        print("\n--- untracked files ---")
        for f in untracked:
            print("  {}".format(f))
    if modified:
        print("\n--- modified files ---")
        for f in modified:
            print("  {}".format(f))
