#!/usr/bin/env python3
"""Retry with a skip parameter"""
import sys, openpyxl, subprocess, json

if hasattr(sys.stdout,"reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8",errors="replace")

wb = openpyxl.load_workbook(r"D:\OpenClaw\workspace\temp_interview.xlsx")
MAX = 160

def extract(sname, skip_n=0, max_n=999, label=""):
    ws = wb[sname]
    rows = list(ws.iter_rows(values_only=True))
    if not rows:
        return None
    
    mc, hr = 0, 0
    for i, row in enumerate(rows[:10]):
        n = sum(1 for v in row if v is not None and str(v).strip())
        if n > mc:
            mc, hr = n, i
    
    header, dr = rows[hr], rows[hr+1:]
    
    q = {}
    cq = None
    for j, h in enumerate(header):
        if h is not None and str(h).strip():
            t = str(h).strip()
            if t.startswith("Q") or (t.isdigit() and len(t) <= 2):
                if cq: q[j] = "{} [{}]".format(cq, t)
            else:
                cq = t
                q[j] = cq
    
    if len(q) < 3:
        q = {}
        for j, h in enumerate(header):
            if h is not None and str(h).strip() and len(str(h).strip()) > 2:
                q[j] = str(h).strip()
    
    lines = ["# UE4用户访谈 - {}{}".format(sname, " ({})".format(label) if label else ""), ""]
    
    found, added = 0, 0
    for row in dr:
        uid = str(row[0]) if len(row) > 0 and row[0] else ""
        keys = {}
        for j, v in enumerate(row):
            if j < 2: continue
            if v is not None and str(v).strip() and len(str(v).strip()) > 3:
                keys[j] = str(v).strip()
        if not keys: continue
        
        found += 1
        if found <= skip_n: continue
        if added >= max_n: break
        
        added += 1
        name = str(row[2]) if len(row) > 2 and row[2] else "?"
        lines.append("---")
        lines.append("## 受访者 {}：{} (uid={})".format(added, name, uid))
        lines.append("")
        for ci, a in sorted(keys.items()):
            qt = q.get(ci, "Q{}".format(ci+1))
            if len(a) > MAX: a = a[:MAX] + "..."
            lines.append("- **{}**：{}".format(qt, a.replace("\n", " ")))
        lines.append("")
    
    lines.append("---\n*完整数据见原始 xlsx*")
    return "\n".join(lines)

def create(name, content):
    r = subprocess.run(["dws","doc","create","--name",name,"--markdown",content,"--format","json"],
        capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=30)
    if r.returncode == 0:
        return json.loads(r.stdout).get("docUrl","?")
    return "FAIL: {}".format((r.stderr or r.stdout)[:80])

# Sheet 02: first 4 users, then next 5
c1 = extract("02活跃-平稳大佬", 0, 4, "上")
print("02上: {} bytes".format(len(c1)), create("【UE4用户访谈】02活跃-平稳大佬(上)", c1))

c2 = extract("02活跃-平稳大佬", 4, 9, "下")
print("02下: {} bytes".format(len(c2)), create("【UE4用户访谈】02活跃-平稳大佬(下)", c2))

# Sheet 03: just 2 users, very short answers
c3 = extract("03活跃-沉默大佬", 0, 2)
print("03: {} bytes".format(len(c3)), create("【UE4用户访谈】03活跃-沉默大佬", c3))

c1b = extract("01活跃-加速大佬", 6, 9, "下")  # remaining 1 user (7th)
print("01下: {} bytes".format(len(c1b)), create("【UE4用户访谈】01活跃-加速大佬(下)", c1b))
