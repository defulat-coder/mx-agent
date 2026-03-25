# 评测数据集重构设计

**日期**: 2026-03-26
**状态**: 已确认设计，待实现

## 1. 目标

重构项目评测数据集，目标不是继续维护旧式 Markdown 表格用例，而是建立一套面向业务验收的、可重建的、可发布到 Langfuse 的分层数据集体系。

本次重构聚焦：

- 同时覆盖 `router_team` 和各子 agent
- 采用均衡版规模，而不是超重覆盖
- 以业务验收为主，而不是机械枚举所有工具
- 基于现有 agent 逻辑和种子数据生成稳定数据集

不做的事：

- 不追求把所有 seed 中的实体全部铺平成 case
- 不把所有 case 都改成纯自动生成
- 不把 router 和子 agent 混在同一个数据集中做统一断言

## 2. 范围

### 2.1 主评测对象

- `router_team`
- `HR Assistant`
- `IT Assistant`
- `Admin Assistant`
- `Finance Assistant`
- `Legal Assistant`
- `Talent` 相关能力

### 2.2 评测目标

#### Router 层

- 单域路由是否正确
- 跨域调度顺序是否正确
- 最终汇总是否覆盖关键结论
- 特殊入口能力是否正确，例如 `我是谁`
- 是否能避免误路由

#### 子 Agent 层

- 是否选择正确工具
- 是否避免调用禁止工具
- 是否满足权限边界
- 是否完成关键业务动作
- 最终回复是否满足业务断言

## 3. 数据集策略

采用分层业务验收集，而不是单一大数据集。

### 3.1 数据集划分

- `mx-router-acceptance`
- `mx-agent-hr-acceptance`
- `mx-agent-it-acceptance`
- `mx-agent-admin-acceptance`
- `mx-agent-finance-acceptance`
- `mx-agent-legal-acceptance`
- `mx-agent-talent-acceptance`

### 3.2 规模目标

采用均衡版。

建议规模：

- Router 集：约 `50-65` 条
- 各子 agent 集：每域约 `20-40` 条
- 总量控制在约 `160-260` 条

该规模可以兼顾覆盖率、可维护性和回归成本。

## 4. Case 分类法

每个数据集固定使用以下分类：

- `smoke`
- `core`
- `workflow`
- `forbidden`
- `edge`

### 4.1 Router 集分配建议

- `smoke`: 10
- `core`: 20
- `workflow`: 15
- `forbidden`: 10
- `edge`: 10

### 4.2 子 Agent 集分配建议

每个子 agent：

- `smoke`: 5
- `core`: 10-15
- `workflow`: 5-8
- `forbidden`: 5-8
- `edge`: 5-8

## 5. 数据结构

每条评测 case 不再只保留 `user_input + expected_tool`，而是统一为结构化业务验收记录。

### 5.1 Meta

- `case_id`
- `title`
- `layer`: `router | agent`
- `domain`: `hr | it | admin | finance | legal | talent | cross_domain`
- `scenario_type`: `smoke | core | workflow | forbidden | edge`
- `priority`: `p0 | p1 | p2`

### 5.2 Auth

- `employee_id`
- `roles`
- `department_id`
- `persona_label`

### 5.3 Input

- `user_input`
- `conversation_context`

### 5.4 Expectation

- `expected_agents`
- `expected_agent_mode`: `all | any | ordered | none`
- `expected_tools`
- `expected_tool_mode`: `all | any | ordered | none`
- `forbidden_tools`
- `response_must_include`
- `response_must_not_include`
- `business_assertions`

### 5.5 Seed

- `depends_on_entities`
- `seed_version`
- `notes`

## 6. 断言模型

`business_assertions` 是核心，替代旧数据里松散的“验证点”描述。

断言拆为 4 类：

### 6.1 Route Assertion

用于 router 集。

示例：

- 必须出现 `hr-assistant -> it-assistant -> admin-assistant`
- 必须只命中 `finance-assistant`

### 6.2 Tool Assertion

用于子 agent 集。

示例：

- 必须调用 `get_team_leave_requests`
- 必须调用 `admin_get_employee_salary`
- 不得调用 `get_leave_requests`

### 6.3 Response Assertion

用于回复质量的业务校验。

示例：

- 必须包含“审批”“待审批”“张三”
- 不得包含“无权限”
- 必须包含流程顺序提示

### 6.4 Entity Assertion

用于校验 case 与 seed 实体的绑定。

示例：

- 必须命中 `employee_id=1`
- 必须命中 `department_id=7`
- 必须引用 `meeting_room.id=5`

## 7. Router 集与子 Agent 集职责边界

### 7.1 Router 集

只关注：

- 路由对象对不对
- 调度顺序对不对
- 汇总信息够不够
- 是否避免误路由

Router 集的主要断言：

- `expected_agents`
- `expected_agent_mode`
- `response_must_include`
- `response_must_not_include`

Router 集不以工具断言为主，除非是 router 自己直接调用的能力，例如 `get_current_user`。

### 7.2 子 Agent 集

只关注：

- 工具是否正确
- 权限是否正确
- 业务动作是否完成
- 最终回复是否满足业务断言

子 agent 集的主要断言：

- `expected_tools`
- `expected_tool_mode`
- `forbidden_tools`
- `business_assertions`
- `response_must_include`

## 8. 生成策略

采用：

- 模板驱动
- Seed 实体绑定
- 少量人工黄金 case

不采用纯 LLM 生成，也不采用全手工维护。

### 8.1 Seed-Aware Templates

每个 domain 定义业务模板，而不是直接写死所有 case。

示例模板能力：

- HR：选取有薪资记录、请假记录、团队成员的员工或主管
- IT：选取存在指定状态工单的提交人或可操作资产
- Admin：选取可用会议室、维护会议室、待审批用品申请、访客记录
- Finance：选取 pending/paid/rejected 报销单、预算记录
- Legal：选取 draft/approved/returned 合同、模板记录

### 8.2 Seed Resolvers

Resolver 从以下 seed 中抽取满足条件的实体：

- `scripts/seed.sql`
- `scripts/admin_seed.sql`
- `scripts/finance_seed.sql`
- `scripts/it_seed.sql`
- `scripts/legal_seed.sql`

输出稳定参数：

- 员工 ID / 工号 / 姓名
- 部门 ID / 名称
- 会议室 ID / 名称
- 工单 ID
- 报销单 ID / 编号
- 合同 ID / 编号

### 8.3 Manual Curated Cases

以下场景必须人工维护：

- 跨域协作
- Router 歧义路由
- 权限绕过
- 复杂 workflow
- 组合工具顺序

## 9. 文件结构

建议新增目录：

```text
evals/
  profiles.yaml
  schema/
  resolvers/
  datasets/
    router/
      templates.yaml
      generated.yaml
    hr/
      templates.yaml
      generated.yaml
    it/
      templates.yaml
      generated.yaml
    admin/
      templates.yaml
      generated.yaml
    finance/
      templates.yaml
      generated.yaml
    legal/
      templates.yaml
      generated.yaml
    talent/
      templates.yaml
      generated.yaml
```

### 9.1 公共文件

- `evals/profiles.yaml`
  - 标准身份定义
- `evals/schema/`
  - case schema 校验
- `evals/resolvers/`
  - seed 解析逻辑

### 9.2 脚本

- `scripts/build_eval_datasets.py`
  - 读取模板
  - 解析 seed
  - 生成实例化 case
  - 校验结构
  - 写出 `generated.yaml`

- `scripts/publish_eval_datasets.py`
  - 将生成数据发布到 Langfuse

## 10. 生成流程

统一生成流程：

1. 读取模板
2. 解析 seed
3. 实例化 case
4. 做结构与引用校验
5. 写本地生成文件
6. 发布到 Langfuse

## 11. 验证策略

生成后的数据集必须通过 5 道校验：

### 11.1 Schema Validation

- 字段完整
- 类型正确
- 枚举合法

### 11.2 Seed Reference Validation

- 引用的员工、会议室、工单、报销单、合同必须存在

### 11.3 Auth Validation

- case 使用的身份必须和目标 domain/工具权限匹配

### 11.4 Assertion Validation

- `expected_agents` 必须映射到现有 agent
- `expected_tools` / `forbidden_tools` 必须映射到现有工具

### 11.5 Dataset Balance Validation

- 每个数据集的 `smoke/core/workflow/forbidden/edge` 达到最低配额

## 12. 错误处理

### 12.1 生成期错误

- 模板字段缺失
- resolver 找不到实体
- 角色和 domain 不匹配
- 断言格式非法

处理方式：

- 直接失败
- 不发布 dataset
- 输出清晰错误报告

### 12.2 发布期错误

- dataset 不存在
- item 写入失败
- 重复 `case_id`
- 线上字段不兼容

处理方式：

- 终止发布
- 输出失败明细

### 12.3 运行期错误

这是评测结果，不是生成失败。

例如：

- `401/403/404/422/5xx`
- `route_mismatch`
- `tool_mismatch`
- `forbidden_tool_called`
- `response_quality` 过低

## 13. 成功标准

以下条件同时满足才算本次重构完成：

- Router 和各子 agent 均拥有独立验收数据集
- 数据集能基于当前 seed 稳定重建
- 数据生成不依赖手工修改具体实体 ID
- 业务主流程、权限、边界、跨域都有覆盖
- 能稳定发布到 Langfuse
- 回归失败时能快速定位到 router / domain / auth / tool / response 层

## 14. 推荐实施顺序

1. 定义统一 case schema 与 profiles
2. 先实现 Router + HR 两个数据集生成链路
3. 再扩到 IT / Admin / Finance / Legal / Talent
4. 最后补发布脚本和校验脚本

## 15. 决策结论

本次采用的最终方案是：

- 业务验收型
- 双层评测目标：Router + 子 Agent
- 均衡版规模
- 分层数据集
- 模板驱动 + Seed 实体绑定 + 少量人工黄金 case

