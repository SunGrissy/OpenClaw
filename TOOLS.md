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

**同样：**
- `&&` 在 PowerShell 里不是逻辑与，会被解析为后台运算符 `&` + 语法错误
- `||` 不是逻辑或，PowerShell 不认
- 多条 `set` 环境变量 + 启动命令的写法在 PS 里全部失败
- **解决：写 `.bat` 脚本文件，再 `cmd /c "路径"` 执行**

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

## Hermes 启动注意
- 必须设 `PYTHONIOENCODING=utf-8`，否则 hermes.exe 输出 emoji 时 GBK 编码崩溃（`UnicodeEncodeError: 'gbk' codec can't encode character`）
- 启动脚本：`D:\OpenClaw\scripts\start_hermes.bat`（已包含编码设置）
- 4 个实例：满满(D:\hermes) / 阿茶(D:\hermes\acha) / 小美(D:\hermes\xiaomei) / 妙妙(D:\hermes\miaomiao)

## 钉钉引用消息结构
- 群聊+私聊：isReplyMsg/repliedMsg 在 `text.extensions` 里，**不在** `text` 顶层
- 检查顺序：先 `text.isReplyMsg`（旧结构），再 `text.extensions.isReplyMsg`（新结构）
- `message.extensions.originalMsgId` 也含被引用消息 ID

---

## OpenClaw gateway restart 不支持 --workdir

- `openclaw gateway restart` 没有 `--workdir` 选项，只能重启默认实例（我的，端口 18789）
- 要重启小马（D:\OpenClaw2，端口 18790）需要手动：
  1. `taskkill /PID <pid> /F` 杀进程
  2. 用 bat 脚本设环境变量后 `start` 新进程
- 小马启动脚本：`D:\OpenClaw2\start_gateway.bat`（已写好）

---

## 钉钉发图
- 格式：`![描述](MEDIA:D:/path/to/image.jpg)` 注意用**正斜杠**
- ❌ 反斜杠 `D:\path\image.png` → 空图/叉
- ✅ 正斜杠 `D:/path/image.jpg` → 成功
- PNG 大图也能发，但压缩成 JPG 更稳

---

## OpenClaw DeepSeek 插件 vs 自定义 Provider
- 内置 DeepSeek 插件需要 `DEEPSEEK_API_KEY` 环境变量才能注册模型，`plugins.entries.deepseek.enabled: true` 不够
- 插件 schema 不支持 `apiKey` 和 `env` 字段，不能在 plugins.entries 里直接传 key
- `.env` 文件放 `$OPENCLAW_STATE_DIR/.env` 不一定被读
- **最终方案**：用自定义 `models.providers.deepseek` 直连 API + `models.mode: "replace"` 替代内置 catalog + 禁用插件避免冲突
- 小马配置：`D:\OpenClaw2\openclaw.json`（deepseek 直连 + tuyoo relay 备用）
- 小马启动脚本：`D:\OpenClaw2\start_gateway.bat`（含环境变量）
- DeepSeek V4 正确参数：`reasoning: true`, `contextWindow: 1000000`, `maxTokens: 384000`

---

Add whatever helps you do your job. This is your cheat sheet.
