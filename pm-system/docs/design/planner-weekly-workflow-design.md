---
status: active
owner: 孙懿
created: 2026-06-21
updated: 2026-06-21
category: design
type: design
related_code:
  - backend/app/routers/planner.py
  - backend/app/services/data_assembler.py
  - business/planner-workbench.js
---

# 策划周计划拆解跟进工作流设计

> 目标：版本 Feature → 周计划 → 个人 Owner → 自动进度追踪，人只做"想清楚 WHAT"和"拍板分工"，其余硅基伙伴搞定。

## 核心问题

- 版本规划有了，但周计划靠手工掰，每周重复劳动
- Feature 进度靠人盯日报，日报填了但没人系统对账
- 工时估算靠经验，偏差没有系统记录和学习机制
- 老大时间被"排期细节"吃掉，而不是"想清楚 WHAT"

**核心决策**

1. **自顶向下分解**：OPS → 版本 → 版本 backbone → Feature 管线 → 全版本 phases → 周目标切片
2. **节点 × 规格分级映射工作日**：Pipeline Skill 已有节点定义，快轨/慢轨作为复杂度分级，按需再拆一层
3. **Agent 自动进度对账**：日报结构化后，Agent 按"交付物状态"更新 Feature 节点完成度，不是简单百分比
4. **工时校准随时记**：发现偏差就 log，Agent 定期汇总学习，规则渐进优化
5. **人只做决策层**：老大想清楚 WHAT + 拍板 Owner 分配 + 确认版本节点日期 + 处理异常阻塞，其余自动化

## 关键场景

### 场景 A：版本启动（双周/版本周期）

1. 老大确定版本 WHAT：要哪些 Feature，每个 Feature 的规格分级（快轨/慢轨/自定义）
2. Agent 按 Pipeline Skill 展开节点，按规格分级映射工作日，反推周计划
3. 老大确认周计划 + 分配 Owner（或 Agent 按负载推荐，老大拍板）
4. 周计划写入 PmSystem，生成周目标条目

### 场景 B：每周站会前（Agent 自动产出）

1. Agent 读取本周日报，按"Pipeline 节点交付物"核对进度
2. 产出：本周完成节点、下周目标节点、阻塞/风险标记
3. 老大站会只看异常：谁卡了、要不要升级、需不需要调整周计划

### 场景 C：工时偏差校准（随时触发）

1. 老大或 Owner 发现某 Feature 实际消耗 vs 规则估算偏差 > 阈值（如 30%）
2. 随手记：原估算 X → 校准为 Y，原因 Z
3. Agent 攒够一批后自动汇总：哪类 Feature 系统性低估？哪个节点总是超期？
4. 老大决定是否调整规则初值

### 场景 D：日报填写（团队执行）

1. 按规范填写：① 完成了哪个 Pipeline 节点（交付物）② 阻塞/风险（哪怕写"无"）③ 不是流水账
2. Agent 每晚自动读取，更新 Feature 进度
3. 异常（节点逾期、阻塞未解）自动标红，升给老大

## 实现状态

⏳ 本文档为设计层，实现方案待 Agent 细化后补充

📎 相关实现：
- Pipeline Skill 节点定义：`.cursor/skills/boss-pipeline-guide/SKILL.md`、`.cursor/skills/system-feature-pipeline/SKILL.md`
- PmSystem Planner 工作台：`business/planner-workbench.js`、`backend/app/routers/planner.py`
- 日报结构化规范：待补充（见下方"待办"）

---

## 详细设计

### 1. 数据产出总流程

```
OPS 规划层（已有）
  ↓ 维度标签人肉排布，作为总体参照
版本创建（按需触发）
  ↓ 读/建版本，检查 pipeline 节点日期是否人工确认
版本 backbone 倒排
  ↓ 按版本发版日倒排 11 节点，标记系统生成日期
Feature 管线节点反拆
  ↓ 按 Feature 类型 + 规格分级查映射表，逐 Feature 倒排
周目标切片（当前周视角）
  ↓ 从全版本 phases 中切出本周目标
团队执行 + 日报回填
  ↓ Agent 解析日报更新进度
校准记录（随时）
  ↓ 偏差记录 → 定期汇总 → 规则迭代
```

### 2. 输入层：OPS 规划 → 版本 WHAT

#### 2.1 OPS 规划层（现状）

- OPS 矩阵里的维度标签是**人肉排上去的**，作为总体 check 的参照
- 后续产出文档中**必须显示 OPS 日期**，供老大核对"规划 vs 实际"是否一致
- OPS 维度值与 Feature 的关联：通过 `linkedFeatureId` 或 Agent 规则建议分配

#### 2.2 版本创建规则

**触发条件**：当 OPS 里的活动需要进版本时

**两种场景**：

| 场景 | 处理 |
|---|---|
| PmSystem **已有**对应版本 | 读取版本配置的 pipeline 节点 → 检查各节点日期是否全为系统自动生成且未被人工修改 → **若是，产出文档中标红提醒人类确认节点日期** |
| PmSystem **没有**对应版本 | 按规则创建版本（见下方"版本创建规则"）→ 初始化默认 pipeline 节点（日期按发版日自动倒推）→ **标红提醒人类确认** |

**版本创建规则**（待补充细化）：
- 版本名称规范：与 OPS 运营周对应
- 发版日默认规则：与 OPS 实际结束日期对齐
- 版本 pipeline 节点初始化：11 节点按发版日倒推，默认间距按历史规律
- 标记位 `is_date_manually_confirmed`：初始 false，人工确认后 true

#### 2.3 资产/Feature 与版本关联

**现状**：部分 OPS 维度值已有 `linkedFeatureId`

**Agent 建议分配规则**（无手动分配时触发）：
- 按维度名称关键词匹配（如含"Boss"→ Boss Feature，含"活动"→ 系统功能 Feature）
- 按维度所在 OPS 分组匹配（如"系统功能"分组 → 系统功能管线）
- 产出建议列表，供人类确认或修改

**Feature 需补充字段**：
- `pipeline_type`：boss / system / ops / visual / custom
- `track`：fast / slow
- `grade`：light / standard / heavy（或合并为4级：快轨-轻量/快轨-标准/慢轨-标准/慢轨-重型）

### 3. 分解层：版本 backbone → Feature 管线 → 周目标

#### 3.1 版本 Backbone 倒排（11 节点）

**节点定义**（版本级节奏 backbone）：

```
planning → feasibility → capacity → scoping → dev → acceptance → goLiveReview → freezeConfirm → releaseTesting → release → retro
```

**倒推逻辑**：
1. 以版本发版日为锚点（release 节点）
2. 往前按默认间距倒推每个节点日期
3. 所有节点初始标记 `is_system_generated = true`
4. **产出文档中，若存在未人工确认的节点日期，标红提醒**

**与 OPS 的对照**：
- 产出文档同时显示 OPS 规划日期 和 版本 backbone 日期
- 不一致时标黄提醒（如 OPS 说 W25 结束，版本 dev 节点排到 W26）

#### 3.2 Feature 管线节点反拆

**Pipeline 来源**（按 Feature 类型）：

| Feature 类型 | Pipeline Skill | 节点 |
|---|---|---|
| Boss | `boss-pipeline-guide` | 概念设计 → 原型验证 → 配置实现 → 联调测试 → 真机验收 |
| 系统功能 | `system-feature-pipeline` | What → How → Build → Make |
| 运营活动 | `system-feature-pipeline` | What → How → Build → Make |
| 美术/视效 | 视效管线（粗颗粒） | 方向确认 → 节奏微调 → 真机验收 |

**反拆逻辑**（单 Feature）：
1. 确定该 Feature 的 `pipeline_type` + `track` + `grade`
2. 查工作日映射表，得每个节点的估算天数
3. 从版本 backbone 的对应阶段截止日往前倒推（如 Make 节点需在版本 dev 阶段前完成）
4. 生成该 Feature 的完整 phases 数组（所有节点，不是仅本周）

**示例**：
```
Feature: 端午活动-陀螺大战
类型: 系统功能, 快轨-标准
版本发版日: 2025-06-27 (W27)
版本 dev 阶段: W24-W25

倒推结果:
- Make:  W25 (2d) → 需在 dev 阶段内完成
- Build: W24-W25 (4d)
- How:   W23 (3d)
- What:  W22 (2d)
```

#### 3.3 规格分级与工作日映射表

**4 级分级**：

| 分级 | 定义 | 适用场景 |
|---|---|---|
| 快轨-轻量 | 复用现有机制，仅换皮/调参 | 换皮 Boss、复用活动模板 |
| 快轨-标准 | 现有机制 + 少量新配置 | 新技能 Boss（无新机制）、常规活动 |
| 慢轨-标准 | 新机制/新系统，但范围可控 | 新玩法原型、新系统 MVP |
| 慢轨-重型 | 跨系统改动、新架构 | 新战斗系统、大规模重构 |

**工作日映射表**（已确认）：

```
Boss 管线:
节点        | 快轨-轻量 | 快轨-标准 | 慢轨-标准 | 慢轨-重型
概念设计    |     2     |     3     |     5     |     8
原型验证    |     2     |     3     |     5     |     8
入版串联    |     2     |     4     |     6     |     8
联调反馈    |     4     |     8     |    16     |    20
真机验收    |     2     |     3     |     4     |     5
合计        |    12     |    21     |    36     |    49

系统功能管线:
节点        | 快轨-轻量 | 快轨-标准 | 慢轨-标准 | 慢轨-重型
What        |     1     |     2     |     3     |     5
How         |     2     |     3     |     5     |     8
Build       |     2     |     3     |     8     |    12
Make        |     3     |     5     |     8     |    12
合计        |     8     |    13     |    24     |    37

运营 Feature（走系统功能管线，Build/Make 略长）:
节点        | 快轨-轻量 | 快轨-标准 | 慢轨-标准 | 慢轨-重型
What        |     1     |     2     |     3     |     5
How         |     2     |     3     |     5     |     8
Build       |     3     |     5     |     8     |    12
Make        |     3     |     5     |     8     |    12
合计        |     9     |    15     |    24     |    37

美术/视效管线（自有节点，非 What/How/Build/Make）:
节点        | 快轨-轻量 | 快轨-标准 | 慢轨-标准 | 慢轨-重型
方向确认    |     1     |     2     |     3     |     5
节奏微调    |     3     |     5     |     8     |    12
真机验收    |     1     |     2     |     3     |     5
合计        |     5     |     9     |    14     |    22
```
Build       |     3     |     5     |     8     |    12
Make        |     3     |     5     |     8     |    12
合计        |     9     |    15     |    24     |    37

美术/视效管线（自有节点，非 What/How/Build/Make）:
节点        | 快轨-轻量 | 快轨-标准 | 慢轨-标准 | 慢轨-重型
方向确认    |     1     |     2     |     3     |     5
节奏微调    |     3     |     5     |     8     |    12
真机验收    |     1     |     2     |     3     |     5
合计        |     5     |     9     |    14     |    22
```

**注意**：
- 基数是规则初值，不是铁律
- 每个节点独立校准（如"配置实现"系统性超期，只调该节点）
- 跨职能交接可标注"等待时间"，不计入纯工作日

#### 3.4 周目标生成（版本视角切片）

**不是直接产出全版本 phases，而是先产出"版本本周目标"**

**步骤**：
1. 确定当前周（如 W25）
2. 遍历该版本所有 Feature 的 phases
3. 筛选 `target_week_id == W25` 的 phase
4. 按版本分组汇总：
   ```
   0715版本本周目标:
   - Feature A: 完成 How 节点（交付物：基调卡）
   - Feature B: 完成 Build 节点（交付物：配置表初稿）
   - Feature C: What 节点进行中（60%）
   ```
5. 多版本并行时，产出"本周跨版本目标总览"

**MVP 不做的**（后续迭代）：
- Owner 负载均衡计算
- 冲突检查（同一 Owner 多 Feature 并行）
- 风险提醒（阻塞、逾期预警）

### 4. 宏观拆解层数据模型（version_macro_plan）

**定位**：存储全版本所有 Feature 的完整 phases，周目标是从中切片的视图。

**表结构**：

```json
{
  "version_id": "v1778362605824",
  "version_name": "0715版本",
  "generated_at": "2025-06-20T10:00:00Z",
  "generated_by": "AgentPlan",
  "status": "active",
  
  // 版本 backbone 节点（11节点）
  "backbone": {
    "release_date": "2025-07-15",
    "stages": [
      {
        "stage": "planning",
        "target_week": "W22",
        "target_date": "2025-06-02",
        "is_system_generated": true,
        "is_date_confirmed": false  // 人工确认标记
      }
      // ... 其他 10 个节点
    ]
  },
  
  // 全版本所有 Feature 的完整 phases（不是仅本周）
  "features": [
    {
      "feature_id": "f_xxx",
      "feature_name": "陀螺大战",
      "dimension_value_id": "dv_yyy",
      "pipeline_type": "system",
      "track": "fast",
      "grade": "standard",
      
      "phases": [
        {
          "phase_name": "Make",
          "phase_order": 4,
          "estimated_days": 2,
          "target_week_id": "W25",
          "target_start_date": "2025-06-16",
          "target_end_date": "2025-06-20",
          "owner_id": "u073",
          "status": "pending",
          "actual_days": null,
          "deliverable": "真机验收通过"
        }
        // ... What, How, Build
      ]
    }
  ],
  
  // 校准日志（每次人工调整估算时追加）
  "calibration_log": [
    {
      "timestamp": "2025-06-20T14:00:00Z",
      "feature_id": "f_xxx",
      "phase_name": "Build",
      "old_estimate": 3,
      "new_estimate": 4,
      "reason": "技能配置比预期复杂",
      "adjusted_by": "u001"
    }
  ],
  
  // 周目标视图（由 Agent 自动切片，非人工编辑）
  "weekly_views": {
    "W25": {
      "generated_at": "2025-06-20T10:00:00Z",
      "goals": [
        {
          "feature_id": "f_xxx",
          "feature_name": "陀螺大战",
          "phase_name": "Make",
          "owner_id": "u073",
          "deliverable": "真机验收通过",
          "status": "pending"
        }
      ]
    }
  }
}
```

**设计要点**：
1. **单表 JSON 存储**——MVP 阶段优先灵活性
2. **前端只读**——Agent API 驱动生成和调整
3. **与 OPS 联动**——`dimension_value_id` 关联 OPS 维度值，`target_week_id` 关联运营周
4. **版本 backbone 独立**——11 节点与 Feature phases 分开存储，但日期互相关联

### 3.3 宏观拆解层设计（MVP：Agent API 驱动）

**定位**：版本级 backbone + Feature 级填充，给老大"一眼看清全局"的视图。

**当前缺失**：Workbench 只有微观 work item，没有宏观管线视角。

**MVP 实现**：只通过 Agent API 生成和调整，**前端只读展示**。

#### 数据结构

```json
{
  "version_id": "v1769090773016",
  "version_name": "端午",
  "backbone": {
    "current_stage": "dev",
    "stages": [
      {"stage": "planning", "status": "done", "week": "W22"},
      {"stage": "feasibility", "status": "done", "week": "W22"},
      {"stage": "capacity", "status": "done", "week": "W22"},
      {"stage": "scoping", "status": "done", "week": "W23"},
      {"stage": "dev", "status": "wip", "week": "W24-W25"},
      {"stage": "acceptance", "status": "na", "week": "W26"},
      {"stage": "goLiveReview", "status": "na", "week": "W26"},
      {"stage": "freezeConfirm", "status": "na", "week": "W26"},
      {"stage": "releaseTesting", "status": "na", "week": "W27"},
      {"stage": "release", "status": "na", "week": "W27"},
      {"stage": "retro", "status": "na", "week": "W28"}
    ]
  },
  "feature_pipeline": {
    "boss": [
      {"feature_id": "feat-001", "name": "端午Boss-屈原", "grade": "慢轨-标准", "nodes": [
        {"node": "概念设计", "status": "done", "week": "W22", "owner": "张三"},
        {"node": "原型验证", "status": "done", "week": "W23", "owner": "张三"},
        {"node": "配置实现", "status": "wip", "week": "W24-W25", "owner": "张三"},
        {"node": "联调测试", "status": "na", "week": "W25", "owner": "张三"},
        {"node": "真机验收", "status": "na", "week": "W26", "owner": "张三"}
      ]}
    ],
    "system": [...],
    "ops": [...]
  },
  "owner_view": {
    "张三": [
      {"feature_id": "feat-001", "node": "配置实现", "week": "W24-W25", "status": "wip"},
      {"feature_id": "feat-002", "node": "What", "week": "W24", "status": "na"}
    ],
    "李四": [...]
  }
}
```

#### 生成流程（Agent API）

1. **输入**：版本 WHAT（Feature 列表 + 规格分级）
2. **Agent 反推**：
   - 版本研发 backbone：按版本截止日倒排，确定每个 stage 的默认 week
   - Feature 管线：按优先级排序，每个 Feature 按节点顺序排布，节点间可并行
   - 关键路径识别：跨 Feature 依赖（如 A 的"配置实现"依赖 B 的"接口交付"）
3. **输出**：宏观拆解 JSON（backbone + feature_pipeline + owner_view）
4. **存储**：写入 PmSystem 数据库（新增表 `version_macro_plan`）

#### 调整流程（Agent API）

**触发条件**：
- 老大口头指令（"把 Feature X 提前一周"）
- 阻塞导致顺延（某节点逾期，后续节点自动后移）
- 工时规则校准后重算

**Agent 执行**：
1. 接收调整指令（自然语言或结构化参数）
2. 修改对应节点/Feature 的 week 分配
3. 自动校验：
   - 关键路径是否冲突
   - Owner 周负载是否过载（超过 5 个工作日）
   - 版本截止日是否仍然可达
4. 输出调整后的宏观拆解 JSON
5. 更新数据库

**校验规则**：
- 同一 Owner 同一周的所有节点工作日之和 ≤ 5（或按实际团队规则）
- 有依赖关系的节点，前置节点 week ≤ 后置节点 week
- 版本截止日前，所有 Feature 的最后一个节点必须完成

#### 展示层（前端只读）

**管线视角总览**：
```
端午版本 — 当前: dev 阶段 (W24)

backbone:  planning → feasibility → capacity → scoping → [dev] → acceptance → ...
           done       done           done       done       wip      na

Feature 管线:
Boss:
  屈原    [概念][原型][配置====][联调][验收]
           done   done   wip(W24)  na    na
  龙舟    [概念][原型][配置][联调][验收]
           done   done   na    na    na

系统:
  端午活动 [What][How][Build][Make]
           done   wip   na     na

Owner 负载:
  张三: W24 配置实现(3d) + What(2d) = 5d ✅
  李四: W24 原型验证(2d) = 2d ✅
```

**策划组视角总览**：
```
策划组 — W24 目标

张三:
  - 屈原 Boss: 配置实现节点（3d）→ 交付物: 配置表初稿
  - 端午活动: What 节点（2d）→ 交付物: 功能基调卡
  合计: 5d

李四:
  - 龙舟 Boss: 原型验证节点（2d）→ 交付物: 原型文档
  合计: 2d
```

#### 与 Workbench 的关系

| 层级 | 数据 | 编辑权限 | 用途 |
|---|---|---|---|
| 宏观拆解层 | 版本 backbone + Feature 节点 + Owner 周分配 | Agent API（MVP） | 老大全局预览、周计划确认 |
| Workbench | work item（具体任务） | 人手动 | 个人执行、日常跟踪 |

**关联**：宏观拆解层的每个节点，可展开为多个 work item。例如"配置实现"节点 = work item "配置技能表" + work item "配置数值表" + work item "配置 UI 布局"。

**MVP 不打通**：宏观拆解层和 Workbench 各自独立，后续可迭代关联。

### 5. 执行层：周目标 → 个人 → 日报

#### 5.1 周目标条目设计

**PmSystem 中新增或复用现有条目**：

| 字段 | 说明 |
|---|---|
| 周目标 ID | 自动生成 |
| 关联 Feature ID | 指向版本中的 Feature |
| 目标节点 | 本周要完成的 Pipeline 节点 |
| 交付物标准 | 节点完成的具体验收标准（Pipeline Skill 中已有） |
| Owner | 负责人（人） |
| 计划工作日 | 该节点规则估算的工作日 |
| 实际工作日 | 填写后自动累计 |
| 状态 | 未开始 / 进行中 / 已完成 / 阻塞 |
| 阻塞原因 | 日报中解析或手动填写 |
| 校准记录 | 工时偏差时的调整记录 |

#### 5.2 日报规范（团队填写）

**现有结构化日报基础上，增加/强化以下字段**：

```
【本周完成】
- Feature X：完成"原型验证"节点（交付物：原型文档 + 配置表初稿）
- Feature Y："配置实现"节点进行中（60%，预计下周二完成）

【下周目标】
- Feature X：进入"配置实现"节点
- Feature Y：完成"配置实现"节点

【阻塞/风险】
- Feature Y：美术资源（技能特效）尚未提供，预计阻塞 2 天 → 已同步美术负责人
- 无其他阻塞

【工时偏差】（可选，发现时填）
- Feature X"原型验证"节点：原估算 3d，实际 5d，原因：机制比预期复杂，需补充 2 个分支场景
```

**Agent 解析规则**：
- "完成 XX 节点" → 该节点标记为已完成
- "进行中（N%）" → 该节点标记为进行中，进度 N%
- "阻塞" → 标记阻塞状态，提取阻塞原因和预计天数
- "工时偏差" → 写入校准日志

#### 5.3 自动进度更新

**Agent 每晚执行**（或日报提交后触发）：

1. 读取当日日报
2. 按 Feature ID 和节点名称匹配周目标条目
3. 更新节点状态：未开始 → 进行中 → 已完成
4. 累计实际工作日
5. 识别异常：
   - 节点逾期（计划完成日 < 今日且状态 ≠ 已完成）
   - 阻塞未解（阻塞原因连续 N 天相同）
   - 工时偏差累计 > 阈值
6. 产出简报：异常项标红，正常项绿标

### 6. 校准层：工时规则迭代

#### 6.1 校准日志格式

```json
{
  "calibration_id": "cal-001",
  "feature_id": "feat-xxx",
  "feature_type": "boss",
  "grade": "快轨-标准",
  "node_name": "原型验证",
  "original_estimate": 3,
  "calibrated_estimate": 5,
  "reason": "机制比预期复杂，需补充 2 个分支场景",
  "calibrated_by": "孙懿",
  "date": "2026-06-21",
  "version_id": "v1769090773016"
}
```

#### 6.2 定期汇总学习

**Agent 每月/每版本自动汇总**：

| 汇总维度 | 输出 |
|---|---|
| 按 Feature 类型 | Boss 类平均偏差 +15%，系统功能类平均偏差 -5% |
| 按节点 | "配置实现"节点系统性超期 20%，"验收"节点通常提前 1d |
| 按分级 | 快轨-轻量估算准，慢轨-重型系统性低估 30% |
| 按版本 | 端午版本 vs 0527 版本偏差趋势 |

**老大决策**：是否调整规则初值？调整哪个节点？

### 7. 人的角色

| 事项 | 频率 | 人（老大/团队） | 硅基伙伴 |
|---|---|---|---|
| 想清楚版本 WHAT | 版本启动前 | 老大 | 辅助记录 |
| 确定 Feature 规格分级 | 版本启动时 | 老大 | 按规则推荐 |
| 拍板 Owner 分配 | 版本启动时 | 老大 | 按负载推荐 |
| 确认版本节点日期 | 版本创建/读取时 | 老大 | 标红提醒未确认项 |
| 确认周计划 | 每周（或版本启动时一次） | 老大 | 自动反推 |
| 站会同步阻塞 | 每周 | 老大 + 团队 | 产出异常简报 |
| 工时校准 | 随时（发现偏差时） | 老大/Owner | 记录 + 汇总 |
| 填写日报 | 每日 | 团队 | 解析 + 更新进度 |
| 进度对账 | 每日/每周 | — | Agent 自动 |
| 异常预警 | 触发式 | — | Agent 自动标红升给老大 |

---

## 待办

- [x] 填充工作日映射表（已确认）
- [ ] 细化版本创建规则（名称规范、发版日规则、节点初始化间距）
- [ ] 设计 PmSystem 周目标条目的数据模型（是否复用现有 Feature 字段？新增表？）
- [ ] 日报规范文档（半页纸，团队可见）
- [ ] 校准日志存储方案（PmSystem 数据库？独立文件？）
- [ ] Agent 自动对账脚本设计（解析日报 → 更新进度 → 识别异常）
- [ ] 与现有 PmSystem Planner 工作台的集成方案

## 附录：术语表

| 术语 | 定义 |
|---|---|
| Pipeline 节点 | Feature 从构思到交付的阶段性里程碑（如"概念设计""原型验证"） |
| 规格分级 | Feature 的复杂度分级（快轨-轻量/快轨-标准/慢轨-标准/慢轨-重型） |
| 周目标 | 本周必须完成的 Pipeline 节点集合，跨 Feature 汇总 |
| 节点工作日基数 | 某规格分级下，某节点的规则估算工作日 |
| 校准日志 | 实际消耗 vs 规则估算的偏差记录，用于迭代规则 |
| 版本 backbone | 版本级 11 节点（planning→...→retro），管版本整体节奏 |
| Feature phases | 单个 Feature 的所有管线节点（全版本，不是仅本周） |
| 交付物标准 | 节点完成时必须产出的具体成果（Pipeline Skill 中定义） |
