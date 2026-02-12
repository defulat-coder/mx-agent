## ADDED Requirements

### Requirement: 请求鉴权
系统 SHALL 从 HTTP 请求 header 中提取认证 token 并解析出员工身份信息。

#### Scenario: 有效 token
- **WHEN** 请求携带有效的 `Authorization: Bearer <token>` header
- **THEN** 系统解析出 employee_id 并注入到请求上下文

#### Scenario: 无效或过期 token
- **WHEN** 请求携带的 token 无效或已过期
- **THEN** 系统返回 401 Unauthorized

#### Scenario: 缺少 token
- **WHEN** 请求未携带 Authorization header
- **THEN** 系统返回 401 Unauthorized

### Requirement: Agent Tool 鉴权
所有 Agent Tool 在执行数据查询时 SHALL 强制使用当前认证用户的 employee_id 进行数据过滤。

#### Scenario: Tool 数据隔离
- **WHEN** Agent 调用任何数据查询 Tool
- **THEN** Tool 内部 SQL 查询强制附加 `WHERE employee_id = :current_employee_id`，不可被 prompt 绕过

### Requirement: 身份上下文传递
系统 SHALL 通过 agno 的 run_context 机制将 employee_id 传递给 Agent 及其 Tools。

#### Scenario: 上下文注入
- **WHEN** /v1/chat 接口接收到已认证的请求
- **THEN** employee_id 通过 run_context 传入 Agent，Agent 的所有 Tool 调用均可获取该 employee_id
