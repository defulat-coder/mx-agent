## 1. 项目依赖与配置

- [x] 1.1 pyproject.toml 添加依赖（fastapi, uvicorn, agno, sqlalchemy==2.0.46, asyncpg, pydantic-settings, loguru）
- [x] 1.2 创建 app/config.py — pydantic-settings 配置类（DATABASE_URL, LLM_MODEL, API_PREFIX, LOG_LEVEL, LOG_FILE, LOG_ROTATION, LOG_RETENTION 等）
- [x] 1.3 创建 .env.example 配置模板

## 2. FastAPI 应用入口

- [x] 2.1 创建 app/__init__.py
- [x] 2.2 创建 app/main.py — FastAPI app 实例、lifespan（启动/关闭 DB 连接池）、全局异常处理
- [x] 2.3 创建 app/api/v1/router.py — v1 路由聚合
- [x] 2.4 创建 app/api/v1/endpoints/chat.py — POST /v1/chat 接口

## 3. 数据库基础设施

- [x] 3.1 创建 app/core/database.py — async engine、session factory、get_db 依赖
- [x] 3.2 创建 app/models/base.py — declarative Base，含 id/created_at/updated_at 公共字段
- [x] 3.3 创建 app/models/__init__.py

## 4. 鉴权

- [x] 4.1 创建 app/core/auth.py — 从 Authorization header 解析 token 提取 employee_id
- [x] 4.2 创建 app/core/deps.py — FastAPI Depends 依赖（get_current_employee）
- [x] 4.3 创建 app/schemas/auth.py — EmployeeContext schema

## 5. Agent 框架

- [x] 5.1 创建 app/agents/router_agent.py — agno Team(mode="router")，注册子 Agent
- [x] 5.2 创建 app/agents/hr_agent.py — HR Agent 占位，加载 hr skills
- [x] 5.3 创建 app/agents/finance_agent.py — Finance Agent 占位（回复"功能开发中"）
- [x] 5.4 创建 app/agents/legal_agent.py — Legal Agent 占位（回复"功能开发中"）

## 6. 请求/响应 Schema

- [x] 6.1 创建 app/schemas/chat.py — ChatRequest / ChatResponse schema

## 7. 全局异常处理

- [x] 7.1 创建 app/core/exceptions.py — 自定义异常类 + 全局异常 handler

## 8. 日志系统

- [x] 8.1 创建 app/core/logging.py — loguru 初始化（控制台+文件输出、rotation/retention、拦截 stdlib logging）
- [x] 8.2 创建 app/core/middleware.py — 请求日志中间件（method, path, status_code, duration_ms）
- [x] 8.3 在 app/main.py 中集成日志初始化和请求日志中间件

## 9. 入口脚本更新

- [x] 9.1 更新根目录 main.py 为 uvicorn 启动入口
