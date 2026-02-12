## Context

项目已有基础异常处理（AppException + 2 个子类 + 2 个 handler），现需升级为生产级。当前 middleware 层已有 RequestLoggingMiddleware，需新增 request_id 支持。

## Goals / Non-Goals

**Goals:**
- 统一错误响应 JSON 格式，所有异常来源输出一致
- 业务错误码，便于前端判断和运维排查
- request_id 贯穿请求生命周期（日志 + 响应 header + 错误响应 body）
- DEBUG 模式返回 traceback

**Non-Goals:**
- 不做国际化（错误消息固定中文）
- 不做错误上报/告警（后续迭代）

## Decisions

### 1. 统一错误响应格式

```json
{
  "code": 40101,
  "message": "token 已过期",
  "detail": null,
  "request_id": "req_abc123",
  "timestamp": "2026-02-11T10:00:00Z"
}
```

- `code`: 业务错误码（int），前端据此做分支处理
- `message`: 用户可读的错误描述
- `detail`: 可选，DEBUG 模式下附带 traceback 或校验细节
- `request_id`: 当前请求 ID
- `timestamp`: ISO 8601 格式

### 2. 业务错误码编码规则

`{HTTP状态码前3位}{序号2位}`

| 范围 | 含义 | 示例 |
|------|------|------|
| 40001-40099 | 通用客户端错误 | 40001 参数缺失 |
| 40101-40199 | 认证错误 | 40101 token 缺失, 40102 token 过期, 40103 token 无效 |
| 40301-40399 | 权限错误 | 40301 无权访问 |
| 40401-40499 | 资源不存在 | 40401 员工不存在 |
| 42201-42299 | 参数校验 | 42201 请求参数校验失败 |
| 50001-50099 | 服务内部错误 | 50001 未知服务错误 |
| 50201-50299 | 外部服务错误 | 50201 LLM 调用失败 |

定义为 IntEnum 常量类，便于引用。

### 3. 异常类体系

```python
AppException (base, 默认 400)
├── UnauthorizedException   # 401, code=40101
├── ForbiddenException      # 403, code=40301
├── NotFoundException       # 404, code=40401
├── ValidationException     # 422, code=42201
├── BusinessException       # 400, code=40001
└── ExternalServiceException # 502, code=50201
```

AppException 构造函数签名：`(code: int, message: str, status_code: int, detail: str | None)`

### 4. request_id 中间件

- 检查请求 header `X-Request-ID`，有则复用，无则生成 `req_{uuid4_hex[:12]}`
- 存入 contextvars，loguru 日志自动带上
- 写入响应 header `X-Request-ID`
- 错误响应 body 中的 `request_id` 字段从 contextvars 读取

### 5. 覆盖所有异常来源

| 异常类型 | Handler | 行为 |
|---------|---------|------|
| AppException 及子类 | app_exception_handler | 按 code/message/status_code 返回 |
| RequestValidationError | validation_handler | code=42201，detail 含字段级错误 |
| StarletteHTTPException | http_exception_handler | 映射到对应 code |
| Exception | unhandled_handler | code=50001，DEBUG 时带 traceback |

## Risks / Trade-offs

- **[BREAKING]** 错误响应格式变更 → 前端需适配，但当前项目早期影响可控
- **[性能]** request_id 用 contextvars → 开销极低，可忽略
