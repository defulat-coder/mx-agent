## MODIFIED Requirements

### Requirement: 身份上下文传递
系统 SHALL 通过 agno 的 run_context 机制将 employee_id、roles、department_id 传递给 Agent 及其 Tools。

#### Scenario: 员工上下文注入
- **WHEN** /v1/chat 接口接收到普通员工的已认证请求
- **THEN** session_state 包含 `{"employee_id": <id>, "roles": ["employee"], "department_id": null}`

#### Scenario: 主管上下文注入
- **WHEN** /v1/chat 接口接收到部门主管的已认证请求
- **THEN** session_state 包含 `{"employee_id": <id>, "roles": ["employee", "manager"], "department_id": <dept_id>}`

### Requirement: 请求鉴权
系统 SHALL 从 HTTP 请求 header 中提取认证 token 并解析出员工身份信息，同时查库判断角色列表。

#### Scenario: 有效 token（普通员工）
- **WHEN** 请求携带有效 token 且该员工不是任何部门的 manager
- **THEN** 返回 EmployeeContext，roles=["employee"]，department_id=None

#### Scenario: 有效 token（部门主管）
- **WHEN** 请求携带有效 token 且该员工是某部门的 manager_id
- **THEN** 返回 EmployeeContext，roles=["employee", "manager"]，department_id=该部门 ID

#### Scenario: 无效或过期 token
- **WHEN** 请求携带的 token 无效或已过期
- **THEN** 系统返回 401 Unauthorized

#### Scenario: 缺少 token
- **WHEN** 请求未携带 Authorization header
- **THEN** 系统返回 401 Unauthorized

## ADDED Requirements

### Requirement: 按角色动态创建 Agent
系统 SHALL 根据当前用户 roles 列表动态创建包含对应 tools 的 Agent Team。

#### Scenario: 纯员工请求
- **WHEN** roles=["employee"] 的用户发起聊天
- **THEN** HR Agent 只含员工 tools 和员工 prompt

#### Scenario: 主管请求
- **WHEN** roles 包含 "manager" 的用户发起聊天
- **THEN** HR Agent 含员工 tools + 主管 tools，以及对应 prompt

### Requirement: Tool 层权限防御
Tools SHALL 通过 session_state.roles 做权限校验，作为防御纵深。

#### Scenario: 非主管调用主管 Tool
- **WHEN** roles 不包含 "manager" 的用户尝试调用主管 Tool
- **THEN** Tool 抛出权限错误
