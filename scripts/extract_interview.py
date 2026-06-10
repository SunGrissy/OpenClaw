#!/usr/bin/env python3
"""Extract interview data from xlsx and format for DingTalk doc"""
import sys, openpyxl
from datetime import datetime

if hasattr(sys.stdout,"reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8",errors="replace")

wb = openpyxl.load_workbook(r"D:\OpenClaw\workspace\temp_interview.xlsx")

output_lines = []

def p(*args):
    s = " ".join(str(a) for a in args)
    output_lines.append(s)
    print(s)

p("# UE4用户访谈26.6.4 - 整理版")
p("")
p("> 数据来源：钉钉文档 xlsx 导出")
p("> 整理时间：{}".format(datetime.now().strftime("%Y-%m-%d %H:%M")))
p("")

for sname in wb.sheetnames:
    ws = wb[sname]
    rows = list(ws.iter_rows(values_only=True))
    if not rows or len(rows) < 2:
        continue
    
    p("---")
    p("")
    p("## {}".format(sname))
    p("")
    
    # Find where header starts and data starts
    # The sheet has the header row with questions, then data rows
    # Some sheets have a subtitle row first, then header
    
    # Determine structure
    max_header_cells = 0
    header_row_idx = 0
    for i, row in enumerate(rows[:10]):
        non_empty = sum(1 for v in row if v is not None and str(v).strip())
        if non_empty > max_header_cells:
            max_header_cells = non_empty
            header_row_idx = i
    
    header = rows[header_row_idx]
    data_rows = rows[header_row_idx + 1:]
    
    # Build question map from header row
    questions = {}  # col_idx -> question text
    current_q = None
    for j, h in enumerate(header):
        if h is not None and str(h).strip():
            txt = str(h).strip()
            # Check if this is a Q* or number (sub-question)
            if txt.startswith("Q") or (txt.isdigit() and len(txt) <= 2):
                # This is a sub-question under current_q
                if current_q:
                    questions[j] = "{} [{}]".format(current_q, txt)
            else:
                current_q = txt
                questions[j] = current_q
    
    # If not enough questions found, use sequential numbering
    if len(questions) < 3:
        questions = {}
        q_num = 1
        for j, h in enumerate(header):
            if h is not None and str(h).strip():
                txt = str(h).strip()
                if len(txt) > 2 or (txt.isdigit() and int(txt) > 10):
                    questions[j] = txt
    
    p("### 接受访谈用户（{}人）".format(len([r for r in data_rows if any(v and str(v).strip() and len(str(v).strip()) > 3 for v in r[3:])])))
    p("")
    
    interviewed_count = 0
    for row in data_rows:
        # Check if this user actually answered
        answer_cols = {}
        for j, v in enumerate(row):
            if j < 2:
                continue
            if v is not None and str(v).strip() and len(str(v).strip()) > 3:
                answer_cols[j] = str(v).strip()
        
        if not answer_cols:
            continue
        
        interviewed_count += 1
        
        # User info
        uid = str(row[0]) if len(row) > 0 and row[0] else "?"
        name = str(row[2]) if len(row) > 2 and row[2] else "?"
        
        p("**受访者 {}：{} (uid={})**".format(interviewed_count, name, uid))
        p("")
        
        for col_idx, answer in sorted(answer_cols.items()):
            q_text = questions.get(col_idx, "Q{}".format(col_idx+1))
            p("- **{}**：{}".format(q_text, answer.replace("\n", " ")))
        
        p("")
    
    if interviewed_count == 0:
        p("（本表单无接受访谈用户）")
        p("")

# Save
out_path = r"D:\OpenClaw\workspace\UE4用户访谈26.6.4_整理版.md"
with open(out_path, "w", encoding="utf-8") as f:
    f.write("\n".join(output_lines))
print("\nSaved to {}".format(out_path))
