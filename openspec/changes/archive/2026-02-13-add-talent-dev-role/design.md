## Context

HR Agent 已有三层角色体系（员工/主管/管理者），遵循统一的架构模式：`utils.py` 提取身份 → `service` 层查询 → `tools` 层封装 → `agent` 注册。新增人才发展角色需严格复用此模式。

当前数据库使用 SQLite + aiosqlite，通过 `scripts/generate_seed.py` 生成种子数据 SQL，项目启动时自动建表。新增 3 张表需要融入现有的种子数据生成流程。

## Goals / Non-Goals

**Goals:**
- 新增 Training、TalentReview、DevelopmentPlan 3 个 ORM 模型
- 为 3 张新表生成合理的模拟数据
- 实现 13 个只读 Tool（7 查询 + 6 报表），遵循现有 tool 编码模式
- 人才发展角色权限隔离：只有 `roles` 含 `talent_dev` 的用户才能调用

**Non-Goals:**
- 不实现写入操作（安排培训、录入盘点、创建 IDP 等留后续迭代）
- 不新增 API 端点，全部通过 Agent Tool 调用
- 不修改现有角色的权限边界

## Decisions

### 1. 培训记录与计划合并为一张表 `trainings`

**选择**：单表 + `status` 字段区分（待开始/进行中/已完成/未通过），`assigned_by` 非空表示指派计划。

**替代方案**：拆成 `training_records` + `training_plans` 两张表。

**理由**：两者字段高度重叠（课程名、分类、学时），拆分会导致查询和报表需要 UNION 两张表。单表用 status 区分更简洁，也符合培训的自然生命周期（计划 → 执行 → 完成）。

### 2. 九宫格位置存为字符串而非枚举

**选择**：`nine_grid_pos` 存中文字符串（明星/骨干/潜力股/中坚/待雕琢/守成者/专家/待观察/淘汰区）。

**理由**：九宫格标签在不同公司差异大，用字符串保持灵活性。performance + potential 两个维度字段可做程序化计算，nine_grid_pos 作为人工确认结果。

### 3. 人才发展角色复用管理者的档案查询能力

**选择**：`td_get_employee_profile` 直接调用 `get_any_employee_profile` service 函数（管理者已实现），避免重复代码。

**替代方案**：为人才发展单独写一套 profile 查询。

**理由**：两者数据权限一致（全公司 + 含薪资社保），复用已有 service 函数减少维护成本。

### 4. 报表 Tool 在 service 层实现聚合逻辑

**选择**：报表的聚合计算（如各部门培训完成率、九宫格分布）放在 service 层用 Python 实现。

**替代方案**：用 SQL GROUP BY 做聚合。

**理由**：SQLite 对复杂聚合（如跨表 JOIN + 分组 + 百分比计算）支持有限，且数据量小（模拟数据），Python 端聚合更灵活、更易调试。与现有报表 service（如 `get_department_headcount`）保持一致。

## Risks / Trade-offs

- **[数据库重建]** → 新增 3 张表需要删旧库重跑种子脚本。已有的对话/记忆数据会丢失。缓解：这是开发阶段，影响可接受。
- **[Tool 数量膨胀]** → HR Agent 总 tool 数将达到 ~40 个，可能影响 LLM 的 tool 选择准确率。缓解：tool 命名加 `td_` 前缀区分，instructions 中明确角色 → 工具映射。
- **[种子数据质量]** → 模拟的培训/盘点/IDP 数据需要与已有员工数据自洽（如绩效 A 的员工九宫格应在高绩效列）。缓解：种子脚本中基于 PerformanceReview 数据生成一致的 TalentReview。
