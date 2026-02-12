## ADDED Requirements

### Requirement: loguru 作为统一日志库
系统 SHALL 使用 loguru 作为唯一日志输出渠道，替代 Python stdlib logging。

#### Scenario: 日志输出
- **WHEN** 应用任何模块调用 `from loguru import logger; logger.info("...")`
- **THEN** 日志按统一格式输出到控制台和/或文件

### Requirement: 拦截第三方库日志
系统 SHALL 拦截 uvicorn、sqlalchemy 等第三方库的 stdlib logging，统一转发到 loguru。

#### Scenario: uvicorn 日志统一
- **WHEN** uvicorn 输出访问日志或错误日志
- **THEN** 日志通过 loguru 格式化输出，而非 uvicorn 默认格式

### Requirement: 请求日志中间件
系统 SHALL 提供 FastAPI 中间件，记录每个 HTTP 请求的关键信息。

#### Scenario: 请求日志记录
- **WHEN** 任何 HTTP 请求到达并完成处理
- **THEN** 记录一条日志包含：method、path、status_code、duration_ms

### Requirement: 日志配置
日志行为 SHALL 通过环境变量配置。

#### Scenario: 配置项
- **WHEN** 应用启动
- **THEN** 从 .env 读取 LOG_LEVEL（默认 INFO）、LOG_FILE（可选，文件路径）、LOG_ROTATION（默认 "500 MB"）、LOG_RETENTION（默认 "10 days"）
