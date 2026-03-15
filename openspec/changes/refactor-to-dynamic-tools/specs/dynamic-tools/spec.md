## ADDED Requirements

### Requirement: 动态 Tools 工厂函数
各 Agent SHALL 使用工厂函数动态返回 tools，根据 `run_context.session_state.roles` 组装用户有权限的 tools 列表。

#### Scenario: 普通员工请求
- **WHEN** 用户 roles=["employee"] 发起请求
- **THEN** HR Agent 仅返回 employee_tools（7 个查询 + 3 个办理）

#### Scenario: 部门主管请求
- **WHEN** 用户 roles=["employee", "manager"] 发起请求
- **THEN** HR Agent 返回 employee_tools + manager_tools

#### Scenario: 管理者请求
- **WHEN** 用户 roles=["employee", "admin"] 发起请求
- **THEN** HR Agent 返回 employee_tools + admin_tools

#### Scenario: 人才发展角色请求
- **WHEN** 用户 roles=["employee", "talent_dev"] 发起请求
- **THEN** HR Agent 返回 employee_tools + talent_dev_tools + discovery_tools

### Requirement: 工厂函数签名
工厂函数 SHALL 接收 `run_context: RunContext` 参数，Agno 框架自动注入。

#### Scenario: 参数注入
- **WHEN** Agent.run() 执行时调用 tools 工厂函数
- **THEN** Agno 自动传入当前请求的 run_context

### Requirement: Tools 缓存
动态 tools SHALL 使用 Agno 默认缓存策略，按 session_id 缓存 tools 列表。

#### Scenario: 同 session 多次请求
- **WHEN** 同一 session 内用户发起多次请求
- **THEN** tools 工厂函数仅在首次请求时执行，后续从缓存获取
