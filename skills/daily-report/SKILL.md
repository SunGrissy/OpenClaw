---
name: daily-report
description: 工作日 21:30 自动生成老大日报草稿，确认后提交钉钉日志。非工作日跳过。数据来源：shared-memory hub、大虾 Memory、钉钉日历、Git 巡检、Hermes 进程状态。工作日判定与 PM 系统「假日与调休管理」一致。
---

# 日报生成 SKILL（保安虾叔专用）

## 触发条件

- **Cron**：每个工作日 21:30 触发
- **工作日判定**：与 PM 系统一致（法定假日→非工作日，调休上班日→工作日，否则按周一~周五）
- 非工作日**跳过**，不生成日报

## 工作日判定方法

优先级从高到低：

1. **PM API**：`GET http://192.168.20.160:8112/api/pm-calendar` 返回 `{holidays: [...], workdays: [...]}`
2. **本地回退**：`D:\MyAgents\dingtalk-desktop\pm_work_calendar.py` 中的 `is_pm_workday()` 函数
3. **最终回退**：周一~周五为工作日（降级模式，标记可能不准）

判定逻辑（与 PM 前端一致）：
- 落在 holidays 区间 → 非工作日
- 在 workdays 列表中 → 工作日（即使为周末）
- 周六周日 → 非工作日
- 其他 → 工作日

## 数据源

| 来源 | 路径/方法 | 说明 |
|------|-----------|------|
| ① shared-memory hub | `D:\MyAgents\shared-memory\hub\YYYY-MM-DD.md` | 小橘的每日记忆汇聚，含工作日志 |
| ② 大虾 Memory | `D:\OpenClaw\workspace\memory\YYYY-MM-DD.md` | 大虾当天的工作记录 |
| ③ 钉钉日历 | `dws calendar list --date YYYY-MM-DD` | 老大当天日程 |
| ④ Git 巡检 | `D:\OpenClaw\cron\git-status-last.txt` | 最近一次 git 巡检结果 |
| ⑤ Hermes 进程 | `powershell -ExecutionPolicy Bypass -File D:\OpenClaw\scripts\hermes-healthcheck.ps1` | 四个进程健康状态 |
| ⑥ Hermes Memory | `D:\hermes\memories\MEMORY.md` | 硅基军团汇总记忆（筛当天相关） |
| ⑦ Cursor workLog | `D:\MyAgents\workspace-docs\WORK_LOG.md` | 最近的工作日志条目 |

## 日报格式

基于 `D:\OpenClaw\workspace\daily_report.json` 的结构：

```json
[
  {"key":"今日完成工作","sort":"0","content":"1. ...\n2. ...","contentType":"markdown","type":"1"},
  {"key":"待完成工作","sort":"3","content":"1. ...\n2. ...","contentType":"markdown","type":"1"},
  {"key":"需协助工作","sort":"4","content":"1. ...","contentType":"markdown","type":"1"}
]
```

### 格式铁律

1. 每个条目用**编号列表**（`1. 2. 3.`），不要用 bullet
2. 内容**简洁有力**，一句话说清一件事，不超过两行
3. 动词开头：**完成/修复/配置/启动/调整/排查/创建/提交/验收**
4. 有具体产出就写产出，没产出就写动作
5. 待完成/需协助 要写明**阻塞原因**或**需要谁协助**

## 生成流程

1. 判定今天是否工作日（非工作日直接退出，不生成）
2. 收集所有数据源
3. 综合归纳：
   - 从 hub + 大虾 Memory 提取今天完成的工作
   - 从日程、git 变更、进程状态补充遗漏项
   - 从搁置清单、未完成任务提炼待完成和需协助
4. 按 JSON 格式生成初稿
5. 发给老大确认（通过钉钉消息）
6. 老大确认后，提交钉钉日志（`dws log create`）

## 提交流程

```bash
# 查看可用模板
dws log template list

# 创建日志
dws log create --template <template_id> --content "<json_content>"
```

## 注意事项

- 日报写的是**老大的工作**，不是大虾或小橘的工作
- 语气从老大的视角出发，第一人称或第三人称客观陈述
- 涉及人的名字要准确，不确定的标注 `(待确认)`
- 敏感信息（密码、密钥、内部IP）不入日报