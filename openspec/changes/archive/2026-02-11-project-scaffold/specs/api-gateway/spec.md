## ADDED Requirements

### Requirement: FastAPI 应用入口
系统 SHALL 提供基于 FastAPI 的 HTTP 服务入口，通过 uvicorn 启动。

#### Scenario: 服务启动
- **WHEN** 执行 `uv run uvicorn app.main:app`
- **THEN** 服务在配置端口启动并可接受请求

### Requirement: 统一对话接口
系统 SHALL 提供 `POST /v1/chat` 接口作为所有智能助手的统一入口。

#### Scenario: 正常对话请求
- **WHEN** 用户发送 `POST /v1/chat` 包含 `{"message": "我想请假"}` 和有效 auth token
- **THEN** 系统返回 Agent 的回复，格式为 `{"reply": "...", "action": null | {...}}`

#### Scenario: 缺少认证 token
- **WHEN** 用户发送请求但未携带 auth token
- **THEN** 系统返回 401 Unauthorized

### Requirement: API 版本化路由
系统 SHALL 通过 `/v1/` 前缀组织 API 路由，支持未来版本扩展。

#### Scenario: 路由注册
- **WHEN** 应用启动
- **THEN** 所有 v1 接口注册在 `/v1/` 路径下

### Requirement: 全局异常处理
系统 SHALL 捕获未处理的异常并返回统一格式的错误响应。

#### Scenario: 未知异常
- **WHEN** 请求处理过程中抛出未捕获异常
- **THEN** 系统返回 `500 Internal Server Error`，body 为 `{"detail": "Internal server error"}`，不泄露堆栈信息
