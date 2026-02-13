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

### Requirement: 财务角色
系统 SHALL 支持 `finance` 角色，允许财务人员访问全公司报销审核、预算分析、应收应付等财务管理功能。

#### Scenario: Mock 用户 finance 角色
- **WHEN** 开发/测试环境
- **THEN** `_MOCK_EMPLOYEES` 中郑晓明具有 `finance` 角色，`generate_token.py` 的 manager 用户包含 `finance`

#### Scenario: get_finance_id 校验
- **WHEN** 财务人员工具被调用
- **THEN** `app/tools/finance/utils.py` 的 `get_finance_id` 校验当前用户具有 `finance` 角色，否则返回权限不足
