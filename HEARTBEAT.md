# HEARTBEAT.md

## 定时任务
- [ ] 每晚 22:30 git 巡检：检查 D:\MyAgents / D:\AgentsHub\MyAgents / D:\OpenClaw\workspace 的修改状态，有变更则整理分类报告老大
  - 脚本：D:\OpenClaw\scripts\git-status-check.ps1
  - 结果写入：D:\OpenClaw\cron\git-status-last.txt
  - 计划任务注册（需管理员）：D:\OpenClaw\scripts\register-git-status-check.cmd
- [x] 每30分钟 Hermes 进程巡检：检查满满/阿茶/小美/妙妙4个进程，异常通知老大
  - 脚本：D:\OpenClaw\scripts\hermes-healthcheck.ps1
  - cron job: hermes-healthcheck (49fe70b2-9c4d-43d3-9e24-cb9f8070a391)
  - 检查项：进程存活 + gateway_state + 钉钉连接状态
- [x] 工作日 21:30 日报生成：收集数据源生成初稿，确认后提交钉钉日志
  - SKILL：D:\OpenClaw\workspace\skills\daily-report\SKILL.md
  - 工作日判定脚本：D:\OpenClaw\scripts\is-workday.ps1（与 PM 系统一致，调休上班日也算）
  - cron job: daily-report (3482b998-596d-41cc-9363-0b3ef22ceaba)
  - 数据源：shared-memory hub + 大虾 Memory + 钉钉日历 + Git巡检 + Hermes状态
  - 非工作日自动跳过

## 已完成提醒
（暂无）

## 心跳复盘
- [x] 检查当天 `memory/YYYY-MM-DD.md` 有没有踩坑记录遗漏 — 2026-04-25 已有踩坑记录（dingtalk-stream process() 参数类型），已记入硅基军团 SKILL.md
- [x] TOOLS.md 里的陷阱清单是否需要更新 — 不需要，今天的坑不属于我的环境
