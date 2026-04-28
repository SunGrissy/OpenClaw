---
name: daily-report
description: 工作日 21:30 自动生成老大日报草稿，确认后提交钉钉日志。非工作日跳过。数据来源：钉钉日历、钉钉消息（@我的+我发的+关注名单）、Agent Memory、Git 变更。工作日判定与 PM 系统「假日与调休管理」一致。
---

# 日报生成 SKILL（保安虾叔专用）

## 触发条件

- **Cron**：每个工作日 21:30 触发
- **手动**：老大说"写日报"/"今天的日报"时触发
- **工作日判定**：与 PM 系统一致（法定假日→非工作日，调休上班日→工作日，否则按周一~周五）
- 非工作日**跳过**（除非老大手动要求）

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

按优先级采集，每个源独立容错（某个挂了不影响其他）：

### ① 钉钉日历（时间线骨架）
```bash
dws calendar event list --start "YYYY-MM-DDT00:00:00+08:00" --end "YYYY-MM-DDT23:59:59+08:00" --format json
```
提取：会议名称、时间、参与人、会议室

### ② 钉钉消息（决策与沟通）
三条路径汇聚去重：

| 路径 | 命令 | 说明 |
|------|------|------|
| 被 @ 的消息 | `dws chat message list-mentions --start <当天0点> --end <当天24点>` | 被人找/需要你决策的 |
| 我发过的消息 | `dws chat message list-by-sender --start <当天0点> --end <当天24点>` | 你主动参与的讨论 |
| 关注名单 | `dws chat message list --group <id>` 或 `--user <id>` | 固定监控的群/单聊 |

**筛选规则**：只提取跟工作相关的——你发的、@ 你的、包含关键决策词（确认/决定/通过/驳回/方案/排期/上线）的。闲聊水群不入。

**关注名单**：存放在 `D:\OpenClaw\workspace\daily_report_watchlist.json`
```json
{
  "groups": [
    {"name": "示例群名", "conversationId": "cidXXX"}
  ],
  "users": [
    {"name": "示例人名", "userId": "userXXX"}
  ]
}
```
> 名单待老大提供（周一提醒），提供前此数据源跳过。

### ③ Agent Memory
| 来源 | 路径 | 说明 |
|------|------|------|
| 大虾 Memory | `D:\OpenClaw\workspace\memory\YYYY-MM-DD.md` | 大虾当天工作记录 |
| shared-memory hub | `D:\MyAgents\shared-memory\hub\YYYY-MM-DD.md` | 小橘每日记忆汇聚 |
| Hermes Memory | `D:\hermes\memories\MEMORY.md` | 硅基军团汇总（筛当天相关） |

### ④ Git 变更
对以下目录执行 `git log --since="YYYY-MM-DD 00:00" --until="YYYY-MM-DD 23:59" --oneline`：
- `D:\MyAgents`
- `D:\AgentsHub\MyAgents`
- `D:\OpenClaw\workspace`
- `D:\hermes`

回退：若 git log 为空，读 `D:\OpenClaw\cron\git-status-last.txt`（最近巡检快照）

## 日报格式

### 钉钉日志模板
- 模板名称：**日报**
- 模板 ID：`153363afc40e225078a5a254ded82265`
- 字段：今日完成工作（sort=0）/ 待完成工作（sort=3）/ 需协助工作（sort=4）

### 「今日完成工作」格式——按标签分类

**固定标签池**（有内容才出现，无内容不写该标签）：

| 标签 | 覆盖范围 |
|------|---------|
| 【管线】 | Pipeline 管理、版本节奏、PMO 对齐、跨职能协调 |
| 【产品】 | 方案审核、体验反馈、设计评审、玩法讨论 |
| 【投放】 | 运营活动、直播、投放策略、数据分析 |
| 【组建】 | 招聘面试、人员调整、团队建设 |
| 【AI实用】 | Agent/工具/自动化/效率提升相关 |
| 【其他】 | 不属于以上的（北极星小组、跨部门沟通等） |

每个标签下的条目：
- 标题格式：`═══【标签】═══`（全角等号包裹，视觉突出）
- 标签之间**两个空行**（`\r\n\r\n\r\n`），视觉分割
- **结论/产出驱动**，不写流水账
- 一句话说清：做了什么 → 产出/结论是什么
- 有会议写会议名+关键结论，不写"开了个会"
- 纯文本格式（钉钉日志不渲染 markdown），用 `\r\n` 换行

### 「待完成工作」和「需协助工作」格式——不分类

- 编号列表（`1. 2. 3.`）
- 待完成写明**下一步动作**
- 需协助写明**需要谁做什么**

### 示例

**今日完成工作：**
```
═══【管线】═══
1. PMO 脉搏会，对齐端午版本内容量，启动容量拆解
2. 同步五月投放资源前置准备需求

═══【产品】═══
1. 五一版本 boss 阶段反馈 / 五月中每日打 boss 活动方案审核

═══【投放】═══
1. 直播运营面试交流

═══【组建】═══
1. 黄梓琪·数据分析（复试，校招）— 备选

═══【AI实用】═══
1. Hermes 多 profile 架构梳理 / PmSystem 权限分级落地

═══【其他】═══
1. 北极星小组阶段沟通
```

**待完成工作：**
```
1. 端午版本容量拆解完成（周三前）
2. Hermes 主 profile SOUL.md 正名为总管满满
```

**需协助工作：**
```
1. PmSystem OIDC 自动登录方案——需确认是否可配 token
```

### 换行符

钉钉日志 content 字段使用 `\r\n` 换行。

## 生成流程

1. 判定今天是否工作日（非工作日且非手动触发→退出）
2. 并行采集所有数据源（每个独立容错）
3. **归纳分类**：
   - 从日历提取会议→按标签归类
   - 从钉钉消息提取决策/讨论→按标签归类
   - 从 Agent Memory 提取 AI/工具工作→【AI实用】
   - 从 Git 变更补充代码/文档产出
   - 未覆盖的→【其他】
4. 按格式生成初稿 JSON
5. 发给老大确认（钉钉消息）
6. **等老大明确确认后才提交**——绝对不能自动提交！老大可能修改内容、调整分类、或要求重写。收到“确认”/“提交”/“发”等明确指令后才执行 dws report create

## 提交方法

使用 Python subprocess 调用 dws（避免 PowerShell 转义问题）。

**contents 字段 key 必须与模板字段名完全一致：**
- `今日完成工作`（sort=0）
- `待完成工作`（sort=3）
- `需协助工作`（sort=4）

```python
import subprocess, json

contents = [
    {
        "content": "【管线】\r\n1. xxx\r\n\r\n【产品】\r\n1. xxx",
        "sort": "0",
        "key": "今日完成工作",
        "contentType": "markdown",
        "type": "1"
    },
    {
        "content": "",
        "sort": "3",
        "key": "待完成工作",
        "contentType": "markdown",
        "type": "1"
    },
    {
        "content": "",
        "sort": "4",
        "key": "需协助工作",
        "contentType": "markdown",
        "type": "1"
    }
]
contents_json = json.dumps(contents, ensure_ascii=False)

cmd = [
    "dws", "report", "create",
    "--template-id", "153363afc40e225078a5a254ded82265",
    "--contents", contents_json,
    "--to-user-ids", "0426535900663699,06190305261218848,282615375724254293,083544684131913450,03076540256050,122009354035315553,253240393526384538,124400492823788983,131262131635970380",
    "--format", "json",
    "--yes"
    # 注意：不传 --to-chat，不勾选「通过聊天发送给接收人」
]
result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
print(result.stdout)
```

**Pitfall 警示：**
- `key` 写成 `今日完成` 等简称会导致 `PARAM_ERROR`，必须与模板字段名完全一致。
- 可用 `dws report template detail --name 日报 --yes` 验证字段名称。

## 注意事项

- 日报写的是**老大的工作**，不是大虾或小橘的工作
- 从老大视角出发，第一人称或第三人称客观陈述
- 涉及人的名字要准确，不确定的标注 `(待确认)`
- 敏感信息（密码、密钥、内部 IP）不入日报
- PowerShell 下 dws 传 JSON 参数会转义出错，**一律用 Python subprocess**

## 抄送名单（to-user-ids）

日报提交时固定抄送以下 9 人，通过 `--to-user-ids` 传入，逗号分隔：

```
0426535900663699,06190305261218848,282615375724254293,083544684131913450,03076540256050,122009354035315553,253240393526384538,124400492823788983,131262131635970380
```

| 姓名 | userId |
|------|--------|
| 侯涌 | 0426535900663699 |
| 陈晨 | 06190305261218848 |
| 张梦君 | 282615375724254293 |
| 纪小可 | 083544684131913450 |
| 李建良 | 03076540256050 |
| 许燕飞 | 122009354035315553 |
| 杨玉涛 | 253240393526384538 |
| 崔正钦 | 124400492823788983 |
| 车君怡 | 131262131635970380 |

完整 JSON 备份：`D:\hermes\skills\dingtalk\dws-dingtalk-cli\references\daily-report-cc-list.json`

完整提交命令示例：
```python
cmd = [
    "dws", "report", "create",
    "--template-id", "153363afc40e225078a5a254ded82265",
    "--contents", contents_json,
    "--to-chat",
    "--to-user-ids", "0426535900663699,06190305261218848,282615375724254293,083544684131913450,03076540256050,122009354035315553,253240393526384538,124400492823788983,131262131635970380",
    "--format", "json"
]
```

## 待办

- [ ] 老大提供钉钉消息关注名单（周一）→ 写入 `daily_report_watchlist.json`
- [ ] 消息巡检拆为独立 SKILL/cron（`inbox-triage`），每天 10:00/14:00/18:00 运行
- [x] 日报提交时需选抄送人员——确认名单和 dws 参数写法（`--to-user-ids`）✅ 2026-04-28
