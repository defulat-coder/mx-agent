## 1. 错误码与 Schema

- [x] 1.1 创建 app/core/error_codes.py — IntEnum 错误码常量类（ErrorCode）
- [x] 1.2 创建 app/schemas/error.py — ErrorResponse Pydantic 模型

## 2. 异常类重构

- [x] 2.1 重构 app/core/exceptions.py — AppException 新增 code 字段 + 5 个子类（Forbidden/Validation/Business/ExternalService）
- [x] 2.2 更新 app/core/auth.py — UnauthorizedException 调用改用新的 code 参数

## 3. request_id 机制

- [x] 3.1 创建 app/core/context.py — contextvars 定义 request_id_var + get/set 函数
- [x] 3.2 修改 app/core/middleware.py — 新增 RequestIDMiddleware（生成/透传 X-Request-ID，存入 contextvars，写入响应 header）
- [x] 3.3 修改 app/core/logging.py — loguru format 加入 request_id

## 4. 异常 Handler

- [x] 4.1 重写 app/core/exceptions.py 中的 handler — app_exception_handler 输出统一格式（含 request_id + timestamp）
- [x] 4.2 新增 validation_exception_handler — 处理 RequestValidationError
- [x] 4.3 新增 http_exception_handler — 处理 StarletteHTTPException
- [x] 4.4 重写 unhandled_exception_handler — DEBUG 时附带 traceback

## 5. 集成

- [x] 5.1 修改 app/main.py — 注册新 handler + RequestIDMiddleware
- [x] 5.2 更新测试用例 — 验证新错误格式、request_id、422 格式
