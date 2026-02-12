## Why

当前异常处理过于简陋：只有 `{"detail": "..."}` 格式，无业务错误码、无 request_id 追踪、未覆盖 Pydantic 422 和 FastAPI HTTPException、DEBUG 模式下不返回堆栈。无法满足生产环境排查问题和前端统一错误处理的需求。

## What Changes

- 建立统一错误响应格式（code + message + request_id + timestamp + detail）
- 引入业务错误码体系（按模块编码 401xx/403xx/404xx/422xx/500xx）
- 扩展异常类（ForbiddenException, ValidationException, BusinessException, ExternalServiceException）
- 覆盖所有异常来源（AppException / RequestValidationError / HTTPException / Exception）
- 引入 request_id 机制（生成/透传 X-Request-ID，贯穿日志与响应）
- DEBUG 模式下错误响应附带 traceback

## Capabilities

### New Capabilities

- `error-response`: 统一错误响应格式与业务错误码体系
- `request-id`: request_id 生成/透传机制，贯穿日志上下文与响应 header

### Modified Capabilities

（无已有 spec）

## Impact

- 重构 app/core/exceptions.py（异常类 + handler）
- 修改 app/core/middleware.py（新增 request_id 中间件）
- 修改 app/main.py（注册新 handler）
- 修改 app/schemas/（新增 ErrorResponse schema）
- 所有 API 响应的错误格式变更 — **BREAKING**（前端需适配新格式）
