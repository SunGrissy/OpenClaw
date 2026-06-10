#!/usr/bin/env python3
"""Execute git commits for MyAgents + OpenClaw workspace"""
import subprocess, os, sys, shutil

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

CWD_M = r"D:\MyAgents"
CWD_O = r"D:\OpenClaw\workspace"

def git(args, cwd, msg=""):
    result = subprocess.run(["git"] + args, cwd=cwd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if result.returncode != 0:
        print("  FAIL:", result.stderr.strip()[:200])
    else:
        out = result.stdout.strip()[:100]
        print("  OK" + (" - " + out if out else ""))
    return result

# === Step 1: OpenClaw workspace ===
print("=== OpenClaw workspace ===")
# .gitignore for todo-scanner
gitignore_path = os.path.join(CWD_O, ".gitignore")
if not os.path.isfile(gitignore_path):
    with open(gitignore_path, "w") as f:
        f.write("todo-scanner/\n")
    print("Created .gitignore")

# Delete temp file
tmp = os.path.join(CWD_O, "_tmp_test.md")
if os.path.isfile(tmp): os.remove(tmp)

# Add and commit memory + scripts
git(["add", "memory/"], CWD_O)
git(["add", "scripts/"], CWD_O)
git(["add", "package.json"], CWD_O)
git(["add", ".gitignore"], CWD_O)
git(["add", "UE4用户访谈26.6.4_整理版.md"], CWD_O)
git(["add", "temp_interview.xlsx"], CWD_O)
git(["commit", "-m", "chore: daily memory and utility scripts"], CWD_O)

# === Step 2: MyAgents - cleanup temp files ===
print("\n=== MyAgents: cleanup ===")
cleanup_files = [
    "_commit_msg_econ.txt", "_commit_msg_handbook.txt", "_commit_msg_interview.txt",
    "_commit_msg_mdreader.txt", "_commit_msg_pm.txt", "_commit_msg_pmsystem.txt",
    "_commit_msg_root.txt", "_commit_msg_root_mdreader.txt", "_commit_msg_session.txt",
    "tmp_card_final.txt",
    "todo-scanner/test_emoji.py", "todo-scanner/test_emoji2.py",
    "todo-scanner/disable_oc_cron.py", "todo-scanner/fix_cron_msg.py",
    "todo-scanner/register_schtasks.py",
]
for f in cleanup_files:
    fp = os.path.join(CWD_M, f)
    if os.path.isfile(fp): os.remove(fp)
    elif os.path.isdir(fp): shutil.rmtree(fp)

# Delete dingtalk-desktop/output
dd_out = os.path.join(CWD_M, "dingtalk-desktop", "output")
if os.path.isdir(dd_out): shutil.rmtree(dd_out)

# Commit deletions (staged via git add)
git(["add", "-A"], CWD_M)
git(["commit", "-m", "cleanup: remove temp files and unused outputs"], CWD_M)

# === Step 3: MyAgents - commit cursor skills ===
print("\n=== MyAgents: cursor skills ===")
git(["add", ".cursor/rules/resume-screening.mdc"], CWD_M)
git(["add", ".cursor/skills/_recruitment-toolkit-guide.md"], CWD_M)
git(["add", ".cursor/skills/boss-pipeline-guide/SKILL.md"], CWD_M)
git(["add", ".cursor/skills/cognitive-design/SKILL.md"], CWD_M)
git(["add", ".cursor/skills/devops/hermes-gateway-health-check/SKILL.md"], CWD_M)
git(["add", ".cursor/skills/digital-twin-voice/SKILL.md"], CWD_M)
git(["add", ".cursor/skills/interview-checklist/"], CWD_M)
git(["add", ".cursor/skills/interview-evaluation/"], CWD_M)
git(["add", ".cursor/skills/interview-shared/"], CWD_M)
git(["add", ".cursor/skills/meeting-memory-pipeline/SKILL.md"], CWD_M)
git(["add", ".cursor/skills/resume-screening/"], CWD_M)
git(["add", ".cursor/skills/skill-guide/SKILL.md"], CWD_M)
git(["add", ".cursor/skills/survey-analysis/SKILL.md"], CWD_M)
git(["add", ".cursor/skills/weekly-report/SKILL.md"], CWD_M)
git(["commit", "-m", "docs: update cursor skills (interview, resume, pipeline)"], CWD_M)

# === Step 4: MyAgents - commit narrative docs ===
print("\n=== MyAgents: narrative docs ===")
git(["add", "docs/narrative/meeting-transcription-ledger.md"], CWD_M)
git(["add", "docs/narrative/producer-context-updates/"], CWD_M)
git(["add", "docs/narrative/producer-tower-index.md"], CWD_M)
git(["add", "docs/narrative/工作手册/"], CWD_M)
git(["add", "docs/narrative/经济迭代/"], CWD_M)
git(["add", "docs/narrative/meetings/"], CWD_M)
git(["add", "docs/narrative/_scratch/"], CWD_M)
git(["commit", "-m", "docs: update narrative docs and producer context"], CWD_M)

# === Step 5: MyAgents - palace/design ===
print("\n=== MyAgents: palace/design ===")
git(["add", "palace/"], CWD_M)
git(["commit", "-m", "feat: add palace design docs and interview package"], CWD_M)

# === Step 6: MyAgents - todo-scanner updates ===
print("\n=== MyAgents: todo-scanner ===")
git(["add", "todo-scanner/scan.py"], CWD_M)
git(["add", "todo-scanner/state.json"], CWD_M)
git(["commit", "-m", "feat: todo-scanner emoji reply detection and webhook switch"], CWD_M)

# === Step 7: MyAgents - shared-memory ===
print("\n=== MyAgents: shared-memory ===")
git(["add", "shared-memory/"], CWD_M)
git(["add", "dingtalk-desktop/work_report_assistant_roster.json"], CWD_M)
git(["commit", "-m", "chore: shared-memory hub, knowledge, pending-upgrade"], CWD_M)

# === Step 8: Final status ===
print("\n=== FINAL STATUS ===")
git(["status", "--short"], CWD_M)
print()
git(["status", "--short"], CWD_O)

# === Step 9: Delete merged branches ===
print("\n=== Cleanup branches ===")
for branch in ["agent/UUM-24", "agent/UUM-25", "feature/demand-pool", "tmp/push-editable-deck"]:
    r = subprocess.run(["git", "branch", "-d", branch], cwd=CWD_M, capture_output=True, text=True)
    print("  Delete {}: {}".format(branch, "OK" if r.returncode == 0 else r.stderr.strip()[:60]))

# feat/dingtalk-aider-runner was merged on remote but may have local
r = subprocess.run(["git", "branch", "-d", "feat/dingtalk-aider-runner"], cwd=CWD_M, capture_output=True, text=True)
print("  Delete feat/dingtalk-aider-runner: {}".format("OK" if r.returncode == 0 else r.stderr.strip()[:60]))
