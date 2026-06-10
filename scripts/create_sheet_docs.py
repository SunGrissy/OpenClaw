#!/usr/bin/env python3
"""Split large sheets into multiple docs, smaller ones into single docs"""
import sys, openpyxl, subprocess, json
from datetime import datetime

if hasattr(sys.stdout,"reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8",errors="replace")

wb = openpyxl.load_workbook(r"D:\OpenClaw\workspace\temp_interview.xlsx")
MAX_ANSWER = 300

def extract_users(sname, user_list, part_label=""):
    """Extract specific users from a sheet into markdown."""
    ws = wb[sname]
    rows = list(ws.iter_rows(values_only=True))
    if not rows:
        return None
    
    # Find header
    max_cells = 0
    header_row_idx = 0
    for i, row in enumerate(rows[:10]):
        non_empty = sum(1 for v in row if v is not None and str(v).strip())
        if non_empty > max_cells:
            max_cells = non_empty
            header_row_idx = i
    
    header = rows[header_row_idx]
    data_rows = rows[header_row_idx + 1:]
    
    # Question map
    questions = {}
    current_q = None
    for j, h in enumerate(header):
        if h is not None and str(h).strip():
            txt = str(h).strip()
            if txt.startswith("Q") or (txt.isdigit() and len(txt) <= 2):
                if current_q:
                    questions[j] = "{} [{}]".format(current_q, txt)
            else:
                current_q = txt
                questions[j] = current_q
    
    if len(questions) < 3:
        questions.clear()
        for j, h in enumerate(header):
            if h is not None and str(h).strip():
                if len(str(h).strip()) > 2:
                    questions[j] = str(h).strip()
    
    lines = []
    name_suffix = " ({})".format(part_label) if part_label else ""
    lines.append("# UE4用户访谈 - {}{}".format(sname, name_suffix))
    lines.append("")
    
    interviewed = 0
    for row in data_rows:
        # Skip if this user is not in our target list
        uid = str(row[0]) if len(row) > 0 and row[0] else ""
        if user_list and uid not in user_list:
            continue
        
        keys = {}
        for j, v in enumerate(row):
            if j < 2:
                continue
            if v is not None and str(v).strip() and len(str(v).strip()) > 3:
                keys[j] = str(v).strip()
        
        if not keys:
            continue
        
        interviewed += 1
        name = str(row[2]) if len(row) > 2 and row[2] else "?"
        
        lines.append("---")
        lines.append("## 受访者 {}：{} (uid={})".format(interviewed, name, uid))
        lines.append("")
        
        for col_idx, answer in sorted(keys.items()):
            q_text = questions.get(col_idx, "Q{}".format(col_idx+1))
            if len(answer) > MAX_ANSWER:
                answer = answer[:MAX_ANSWER] + "..."
            lines.append("- **{}**：{}".format(q_text, answer.replace("\n", " ")))
        lines.append("")
    
    if interviewed == 0:
        return None
    
    lines.append("---")
    lines.append("*完整数据见原始 xlsx 文件*")
    
    return "\n".join(lines)


def collect_users(sname):
    """Get list of (uid, size_of_content) for interviewed users."""
    ws = wb[sname]
    rows = list(ws.iter_rows(values_only=True))
    if not rows:
        return []
    
    # Find data start
    max_cells = 0
    header_row_idx = 0
    for i, row in enumerate(rows[:10]):
        non_empty = sum(1 for v in row if v is not None and str(v).strip())
        if non_empty > max_cells:
            max_cells = non_empty
            header_row_idx = i
    
    data_rows = rows[header_row_idx + 1:]
    users = []
    
    for row in data_rows:
        total_len = 0
        uid = str(row[0]) if len(row) > 0 and row[0] else ""
        for j, v in enumerate(row):
            if j < 2:
                continue
            if v is not None and str(v).strip() and len(str(v).strip()) > 3:
                total_len += min(len(str(v).strip()), MAX_ANSWER)
        if total_len > 100:  # has substantive answers
            users.append((uid, total_len))
    
    return users


def create_doc(name, content):
    """Create a DingTalk doc with the given content."""
    if not content or len(content) < 100:
        return "SKIP"
    
    result = subprocess.run(
        ["dws", "doc", "create", "--name", name, "--markdown", content, "--format", "json"],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        timeout=30
    )
    
    if result.returncode == 0:
        data = json.loads(result.stdout)
        return data.get("docUrl", "?")
    else:
        return "FAIL: " + (result.stderr or result.stdout)[:100]


TARGET_SIZE = 7000  # target bytes per doc

for sname in wb.sheetnames:
    users = collect_users(sname)
    if not users:
        print("{}: no interviewed users".format(sname))
        continue
    
    total_size = sum(s for _, s in users)
    print("{}: {} users, ~{}KB total".format(sname, len(users), total_size // 1000))
    
    if total_size < TARGET_SIZE:
        # Single doc
        content = extract_users(sname, [u[0] for u in users])
        if content:
            url = create_doc("【UE4用户访谈】{}".format(sname), content)
            print("  1 doc: {}".format(url))
    else:
        # Split into multiple docs
        part = 1
        current_users = []
        current_size = 0
        for uid, size in users:
            if current_size + size > TARGET_SIZE and current_users:
                # Create doc for current batch
                uids = [u[0] for u in current_users]
                label = "Part {}".format(part)
                content = extract_users(sname, uids, label)
                if content:
                    name = "【UE4用户访谈】{} (Part {})".format(sname, part)
                    url = create_doc(name, content)
                    print("  Part {}: {} ({} users)".format(part, url, len(current_users)))
                part += 1
                current_users = [(uid, size)]
                current_size = size
            else:
                current_users.append((uid, size))
                current_size += size
        
        # Last batch
        if current_users:
            uids = [u[0] for u in current_users]
            label = "Part {}".format(part) if part > 1 else ""
            content = extract_users(sname, uids, label)
            if content:
                name = "【UE4用户访谈】{}{}".format(sname, " (Part {})".format(part) if part > 1 else "")
                url = create_doc(name, content)
                print("  Part {}: {} ({} users)".format(part, url, len(current_users)))
    
    print()
