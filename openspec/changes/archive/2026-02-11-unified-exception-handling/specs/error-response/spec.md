## ADDED Requirements

### Requirement: 统一错误响应格式
所有 API 错误响应 SHALL 使用统一 JSON 格式，包含 code、message、detail、request_id、timestamp 字段。

#### Scenario: 业务异常响应
- **WHEN** 抛出 AppException 及其子类
- **THEN** 响应 body 为 `{"code": <int>, "message": <str>, "detail": <str|null>, "request_id": <str>, "timestamp": <str>}`

#### Scenario: Pydantic 校验失败
- **WHEN** 请求参数不符合 schema（RequestValidationError）
- **THEN** 响应 status=422，code=42201，detail 包含字段级错误信息列表

#### Scenario: FastAPI HTTPException
- **WHEN** 触发 StarletteHTTPException（如 404 路由不存在）
- **THEN** 响应使用统一格式，code 映射为对应业务错误码

#### Scenario: 未知异常
- **WHEN** 发生未捕获的 Exception
- **THEN** 响应 status=500，code=50001，message="服务内部错误"

### Requirement: DEBUG 模式 traceback
DEBUG=true 时，未知异常的错误响应 SHALL 在 detail 字段附带 traceback 信息。

#### Scenario: DEBUG 开启
- **WHEN** DEBUG=true 且发生未捕获异常
- **THEN** detail 字段包含异常 traceback 字符串

#### Scenario: DEBUG 关闭
- **WHEN** DEBUG=false 且发生未捕获异常
- **THEN** detail 字段为 null，不泄露堆栈信息

### Requirement: 业务错误码体系
系统 SHALL 定义 IntEnum 错误码常量类，按 `{HTTP状态码前3位}{序号2位}` 编码。

#### Scenario: 错误码覆盖
- **WHEN** 查看错误码定义
- **THEN** 至少覆盖：40001(通用客户端错误)、40101(token缺失)、40102(token过期)、40103(token无效)、40301(无权访问)、40401(资源不存在)、42201(参数校验失败)、50001(服务内部错误)、50201(外部服务错误)

### Requirement: 异常类体系
系统 SHALL 提供 AppException 基类及 5 个子类，每个子类预设对应的 HTTP 状态码和默认业务错误码。

#### Scenario: 异常类列表
- **WHEN** 查看异常类定义
- **THEN** 存在 UnauthorizedException(401)、ForbiddenException(403)、NotFoundException(404)、ValidationException(422)、BusinessException(400)、ExternalServiceException(502)

### Requirement: ErrorResponse Schema
系统 SHALL 定义 ErrorResponse Pydantic 模型，用于 OpenAPI 文档展示统一错误格式。

#### Scenario: Schema 定义
- **WHEN** 查看 ErrorResponse 模型
- **THEN** 包含 code(int)、message(str)、detail(str|None)、request_id(str)、timestamp(str) 字段
