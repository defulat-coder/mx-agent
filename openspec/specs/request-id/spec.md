## ADDED Requirements

### Requirement: request_id 生成
系统 SHALL 为每个 HTTP 请求生成唯一的 request_id，格式为 `req_{uuid4_hex前12位}`。

#### Scenario: 自动生成
- **WHEN** 请求未携带 X-Request-ID header
- **THEN** 系统自动生成 request_id（如 `req_a1b2c3d4e5f6`）

#### Scenario: 透传
- **WHEN** 请求携带 X-Request-ID header
- **THEN** 系统使用该值作为 request_id

### Requirement: request_id 响应 header
系统 SHALL 在每个 HTTP 响应中写入 X-Request-ID header。

#### Scenario: 正常响应
- **WHEN** 请求正常处理完毕
- **THEN** 响应 header 包含 `X-Request-ID: <request_id>`

#### Scenario: 错误响应
- **WHEN** 请求处理异常
- **THEN** 错误响应 header 同样包含 `X-Request-ID: <request_id>`

### Requirement: request_id 日志上下文
系统 SHALL 通过 contextvars 将 request_id 注入到 loguru 日志上下文，每条日志自动携带 request_id。

#### Scenario: 日志追踪
- **WHEN** 请求处理过程中任何模块打印日志
- **THEN** 日志内容自动包含当前 request_id

### Requirement: request_id 错误响应 body
错误响应 body 中的 request_id 字段 SHALL 与响应 header 中的 X-Request-ID 一致。

#### Scenario: 一致性
- **WHEN** 发生异常返回错误响应
- **THEN** body 中 `request_id` 与 header `X-Request-ID` 值相同
