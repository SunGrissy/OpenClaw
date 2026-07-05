#!/usr/bin/env python3
"""Git 巡检脚本：检查三个仓库的修改状态并分类报告"""
import subprocess, os, json, sys
from datetime import datetime

REPOS = {
    "MyAgents": r"D:\MyAgents",
    "AgentsHub": r"D:\AgentsHub\MyAgents",
    "OpenClaw": r"D:\OpenClaw\workspace",
}

def run_git(repo_path, args):
    try:
        r = subprocess.run(
            ["git"] + args,
            cwd=repo_path,
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=30,
        )
        return r.stdout.strip(), r.stderr.strip(), r.returncode
    except Exception as e:
        return "", str(e), -1

def check_repo(name, path):
    if not os.path.isdir(os.path.join(path, ".git")):
        return {"name": name, "path": path, "error": "不是 git 仓库或无 .git 目录"}

    # Basic status
    status_out, status_err, status_rc = run_git(path, ["status", "--porcelain", "--branch"])
    if status_rc != 0:
        return {"name": name, "path": path, "error": status_err or "git status failed"}

    lines = status_out.split("\n")
    branch_info = ""
    changes = []
    for line in lines:
        if not line.strip():
            continue
        if line.startswith("##"):
            branch_info = line[3:]
            continue
        changes.append(line)

    result = {
        "name": name,
        "path": path,
        "branch": branch_info,
        "changes": changes,
        "clean": len(changes) == 0,
    }

    # If dirty, get more detail
    if changes:
        # Diff stat for staged + unstaged
        staged, __, ___ = run_git(path, ["diff", "--cached", "--stat"])
        unstaged, __, ___ = run_git(path, ["diff", "--stat"])
        result["staged_stat"] = [l for l in staged.split("\n") if l.strip()]
        result["unstaged_stat"] = [l for l in unstaged.split("\n") if l.strip()]

        # Untracked files
        untracked, __, ___ = run_git(path, ["ls-files", "--others", "--exclude-standard"])
        result["untracked_files"] = [l for l in untracked.split("\n") if l.strip()]

        # Recent commits (last 3)
        log, __, ___ = run_git(path, ["log", "--oneline", "-5"])
        result["recent_commits"] = [l for l in log.split("\n") if l.strip()]

    return result

def classify_change(line):
    """分类一条 git status porcelain 行"""
    xy = line[:2]
    path = line[3:].strip()

    # 状态码
    status_map = {
        "M ": "修改(暂存区)",
        "A ": "新增(暂存区)",
        "D ": "删除(暂存区)",
        "R ": "重命名(暂存区)",
        "C ": "复制(暂存区)",
        " M": "修改(工作区)",
        " D": "删除(工作区)",
        "??": "未跟踪",
        "!!": "忽略",
        "AM": "新增→修改",
        "MM": "修改→修改",
        "AD": "新增→删除",
    }

    klass = status_map.get(xy, f"状态:{xy}")
    return klass, path

def generate_report(results):
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    lines = [f"📋 **Git 巡检报告** ({now})", ""]

    has_any_change = False

    for r in results:
        name = r["name"]
        lines.append(f"## 📂 {name}")
        if "error" in r:
            lines.append(f"  ⚠️ {r['error']}")
            lines.append("")
            continue

        lines.append(f"  🌿 分支: {r['branch']}")

        if r["clean"]:
            lines.append(f"  ✅ 干净，无变更")
            lines.append("")
            continue

        has_any_change = True
        changes = r["changes"]
        lines.append(f"  📝 变更文件: {len(changes)} 个")
        lines.append("")

        # 分类统计
        classified = {}
        for c in changes:
            klass, path = classify_change(c)
            classified.setdefault(klass, []).append(path)

        for klass, paths in sorted(classified.items()):
            lines.append(f"  **{klass}** ({len(paths)}个)")
            for p in paths[:10]:
                lines.append(f"    • `{p}`")
            if len(paths) > 10:
                lines.append(f"    • ... 还有 {len(paths)-10} 个")
            lines.append("")

        # Recent commits
        if "recent_commits" in r and r["recent_commits"]:
            lines.append(f"  📜 最近提交:")
            for c in r["recent_commits"]:
                lines.append(f"    • {c}")
            lines.append("")

        lines.append("---")
        lines.append("")

    if not has_any_change:
        lines.append("🎉 三个仓库均无未提交变更。")

    return "\n".join(lines)

def main():
    results = [check_repo(name, path) for name, path in REPOS.items()]
    report = generate_report(results)
    outpath = r"D:\OpenClaw\workspace\scripts\git_check_report.txt"
    with open(outpath, "w", encoding="utf-8") as f:
        f.write(report)
    print(f"Report written to {outpath}")

if __name__ == "__main__":
    main()
