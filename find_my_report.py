import subprocess, json

user_id = "0165313012750022"
cursor = 0
found = []

while True:
    result = subprocess.run(
        ["dws", "report", "list",
         "--start", "2026-04-24T00:00:00+08:00",
         "--end", "2026-04-24T23:59:59+08:00",
         "--size", "20",
         "--cursor", str(cursor)],
        capture_output=True, text=True, timeout=30, encoding="utf-8"
    )
    data = json.loads(result.stdout)
    reports = data.get("result", {}).get("report_list", [])
    
    for r in reports:
        if r.get("creator_user_id") == user_id:
            found.append(r)
    
    has_more = data.get("result", {}).get("hasMore", False)
    if not has_more or not reports:
        break
    cursor += 20
    
print(f"Found {len(found)} reports from user")
for r in found:
    print(json.dumps(r, ensure_ascii=False, indent=2))
