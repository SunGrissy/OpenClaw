# TOOLS.md - Local Notes

Skills define _how_ tools work. This file is for _your_ specifics — the stuff that's unique to your setup.

## What Goes Here

Things like:

- Camera names and locations
- SSH hosts and aliases
- Preferred voices for TTS
- Speaker/room names
- Device nicknames
- Anything environment-specific

## Examples

```markdown
### Cameras

- living-room → Main area, 180° wide angle
- front-door → Entrance, motion-triggered

### SSH

- home-server → 192.168.1.100, user: admin

### TTS

- Preferred voice: "Nova" (warm, slightly British)
- Default speaker: Kitchen HomePod
```

## Why Separate?

Skills are shared. Your setup is yours. Keeping them apart means you can update skills without losing your notes, and share skills without leaking your infrastructure.

## PowerShell exec 陷阱

OpenClaw 的 exec 工具会**吞掉 PowerShell 的 `$_` 变量**，导致所有 `Where-Object { $_.xxx }` 写法全部报 `CommandNotFoundException`。

**❌ 不要写：**
```powershell
Get-Process | Where-Object { $_.Name -eq 'python' }
```

**✅ 替代方案：**
- 用 `tasklist` / `taskkill` / `netstat` / `findstr` 等 CMD 原生命令
- 用 `Get-CimInstance Win32_Process` 配合 `ForEach-Object` 的简写 `?` 也不行，同样依赖 `$_`
- 真要过滤进程，用 `tasklist /FI` 参数
- 用 `cmd.exe /c "原生命令"` 包一层

**记住：exec 里 PowerShell 只适合简单命令，涉及管道+变量过滤的一律绕道用 CMD 原生命令。**

## read 工具无限循环陷阱

对大文件（特别是 HTML/含中文/非标准行尾的文件），read 工具可能无论 offset 设什么都返回前几行，导致无限循环。

**❌ 不要反复重试同一个失败模式：**
- read offset=230 返回前5行 → 换 offset=231 还是前5行 → 再换…（循环几十次）

**✅ 发现 2-3 次返回相同内容就立刻换道：**
- 用 `py -c "f=open(...); ..."` Python 脚本读写
- 用 `findstr /n` 定位行号
- 用 exec + grep 提取特定内容

**核心原则：同一个方向试 2 次无效就 pivot，别撞墙。**

---

Add whatever helps you do your job. This is your cheat sheet.
