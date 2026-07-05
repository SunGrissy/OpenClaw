# HEARTBEAT.md

## 定时任务
- [ ] 每晚 22:30 git 巡检：检查 D:\MyAgents / D:\AgentsHub\MyAgents / D:\OpenClaw\workspace 的修改状态，有变更则整理分类报告老大
  - ⚠️ 注意事项：git 操作含中文路径/消息时，写 `.py` 脚本执行，禁止 exec 里直接 `cmd /c "git commit -m 中文"`（GBK编码吞字符必崩）。新锚点见 AGENTS.md ANCH-011。
- [x] 每30分钟 Hermes 进程巡检：检查满满/阿茶/小美/妙妙4个进程，异常通知老大
  - 脚本：D:\OpenClaw\scripts\hermes-healthcheck.ps1
  - cron job: hermes-healthcheck (49fe70b2-9c4d-43d3-9e24-cb9f8070a391)
  - 检查项：进程存活 + gateway_state + 钉钉连接状态
- [ ] 每30分钟 小马进程巡检：检查 GenericAgent dingtalkapp.py 进程 + 端口19530，异常通知老大
  - 脚本：待创建
  - cron job：待创建
  - 检查项：进程存活 + 端口占用 + 日志最新时间
- [ ] 工作日 21:30 日报生成：收集数据源生成初稿，确认后提交钉钉日志
  - SKILL：D:\OpenClaw\workspace\skills\daily-report\SKILL.md
  - 工作日判定脚本：D:\OpenClaw\scripts\is-workday.ps1（与 PM 系统一致，调休上班日也算）
  - ⚠️ cron job 已丢失（6/25 gateway重启），需要重建
  - 数据源：shared-memory hub + 大虾 Memory + 钉钉日历 + Git巡检 + Hermes状态
  - 非工作日自动跳过

## 已完成提醒
（暂无）

## 待提醒
- [x] 周一(4/28)提醒老大提供钉钉消息关注名单（群名+人名），用于日报和消息巡检
  - ✅ 2026-04-28 07:21 已提醒

- [x] 共享记忆维护：每天读 hub 报告、写入 knowledge、检查 legion-charter 更新
  - 读：D:/MyAgents/shared-memory/hub/YYYY-MM-DD.md
  - 写：D:/MyAgents/shared-memory/knowledge/xiaxia-YYYY-MM-DD.md（有值得共享的发现时写）
  - 完整框架：D:/MyAgents/shared-memory/legion-charter.md

## 心跳复盘
- [x] 检查当天 `memory/YYYY-MM-DD.md` 有没有踩坑记录遗漏 — 今天暂无记忆文件
- [x] TOOLS.md 里的陷阱清单是否需要更新 — 不需要
- [ ] 今日是否有值得写入共享 knowledge/ 的发现
