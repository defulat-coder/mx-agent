## MODIFIED Requirements

### Requirement: 请求鉴权
系统 SHALL 使用 AgentOS JWTMiddleware 从 HTTP 请求中提取 JWT token 并校验，自动注入 user_id 和 session_state。

#### Scenario: 有效 token
- **WHEN** 请求携带有效 JWT token（含 employee_id、roles、department_id claims）
- **THEN** JWTMiddleware 自动注入 user_id、session_state 到 AgentOS 端点参数

#### Scenario: 无效或过期 token
- **WHEN** 请求携带无效或过期 token
- **THEN** 返回 401 Unauthorized

#### Scenario: 缺少 token
- **WHEN** 请求未携带 Authorization header
- **THEN** 返回 401 Unauthorized

### Requirement: 身份上下文传递
系统 SHALL 通过 JWT session_state_claims 将 employee_id、roles、department_id 传递给 Agent 的 session_state。

#### Scenario: session_state 注入
- **WHEN** JWTMiddleware 解析 token 成功
- **THEN** agent 的 session_state 包含 `{"employee_id": <id>, "roles": [...], "department_id": <id|null>}`
