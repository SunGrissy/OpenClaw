#!/usr/bin/env python3
"""Debug: check actual cell values for one interviewed user"""
import openpyxl, sys

if hasattr(sys.stdout,"reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8",errors="replace")

wb = openpyxl.load_workbook(r"D:\OpenClaw\workspace\temp_interview.xlsx")

sname = "01活跃-加速大佬"
ws = wb[sname]
rows = list(ws.iter_rows(values_only=True))
dr = rows[3:]

# Find first interviewed user
for row in dr:
    if "接受" not in str(row[3]):
        continue
    
    print("UID:", row[1])
    print("Interviewer:", row[2])
    print()
    
    # Show ALL columns with content (col 5+)
    for j in range(5, min(len(row), 30)):
        h = rows[0][j] if j < len(rows[0]) else ""
        v = row[j]
        if h or v:
            htext = str(h).strip()[:40] if h else ""
            vtext = str(v).strip()[:80] if v else "(empty)"
            print("  C{}: [{}] -> {}".format(j, htext, vtext))
    
    break
