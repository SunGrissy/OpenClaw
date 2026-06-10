import json, os, glob
from datetime import datetime, timezone, timedelta

tz = timezone(timedelta(hours=8))
today = datetime(2026, 6, 3, tzinfo=tz)
today_ts = int(today.timestamp() * 1000)
tomorrow = datetime(2026, 6, 4, tzinfo=tz)
tomorrow_ts = int(tomorrow.timestamp() * 1000)

found_any = False

# Search all Hermes session files for today's messages
agent_dirs = [
    ("满满", r"D:\hermes\sessions"),
    ("阿茶", r"D:\hermes\acha\sessions"),
    ("小美", r"D:\hermes\xiaomei\sessions"),
    ("妙妙", r"D:\hermes\miaomiao\sessions"),
]
# Add GenericAgent
agent_dirs.append(("小马", r"D:\GenericAgent\sessions"))

for agent, root_dir in agent_dirs:
    if not os.path.isdir(root_dir):
        continue
    files = glob.glob(os.path.join(root_dir, "*.jsonl"))
    for f in files:
        try:
            with open(f, "r", encoding="utf-8") as fh:
                for line in fh:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        msg = json.loads(line)
                        if msg.get("role") != "user":
                            continue
                        ts = msg.get("timestamp", 0)
                        if not (today_ts <= ts < tomorrow_ts):
                            continue
                        content = msg.get("content", "")
                        if isinstance(content, list):
                            texts = [c.get("text", "") for c in content if c.get("type") == "text"]
                            content = " ".join(texts)
                        if len(content) > 300:
                            content = content[:300] + "..."
                        dt = datetime.fromtimestamp(ts / 1000, tz=tz)
                        time_str = dt.strftime("%H:%M")
                        print("{} [{}] {}".format(agent, time_str, content))
                        found_any = True
                    except:
                        pass
        except:
            pass

if not found_any:
    print("NO_TODAY_MESSAGES_FOUND_IN_ANY_AGENT")
