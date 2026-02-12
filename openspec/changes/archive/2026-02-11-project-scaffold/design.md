## Context

全新项目 xm-agent，需要一个支撑多 Agent（HR/Finance/Legal）的基础框架。技术栈已确定：FastAPI + agno + SQLAlchemy async + uv。当前只有空壳 main.py 和已创建的 HR Skills 文件。

## Goals / Non-Goals

**Goals:**
- 建立可扩展的多 Agent 路由架构
- 统一的 /v1/chat 对话接口
- Agent 层鉴权机制（employee_id 注入）
- 异步数据库基础设施
- HR/Finance/Legal Agent 占位，新 Agent 可即插即用

**Non-Goals:**
- 不实现具体业务逻辑（属于 hr-employee-assistant change）
- 不做前端/UI
- 不做用户注册/登录系统（鉴权通过 header token 传入，假设上游已认证）
- 不做消息持久化/会话管理（后续迭代）

## Decisions

### 1. Router Agent 采用 agno Team 模式

agno 原生支持 Team（多 Agent 协作），Router Agent 作为 team coordinator，根据用户意图分发到子 Agent。

- **选择**：agno `Team(mode="router")` 
- **替代方案**：手写 intent classifier → 太重，且 agno 已内置路由能力
- **理由**：开箱即用，减少自定义代码，后续加 Agent 只需注册到 Team

### 2. 鉴权设计：FastAPI Depends + Agent Context 注入

- Auth 中间件从请求 header 提取 token → 解析出 employee_id
- 通过 FastAPI Depends 注入到 endpoint
- Agent 调用 Tool 时通过 `run_context` 传入 employee_id
- Tool 内部强制 `WHERE employee_id = :current_id`

**不在 Agent prompt 层做权限控制**（不可靠），而是在 Tool 代码层硬编码过滤。

### 3. 数据库：SQLAlchemy 2.0.46 async + asyncpg

- **选择**：SQLAlchemy 2.0.46 async session + asyncpg 驱动
- **替代方案**：Tortoise ORM / databases 库
- **理由**：SQLAlchemy 生态最成熟，async 支持已稳定，团队最熟悉

### 4. 配置管理：pydantic-settings

从 `.env` 读取配置，类型安全，与 FastAPI 天然集成。

### 5. 日志：loguru 替代 stdlib logging

- **选择**：loguru
- **替代方案**：stdlib logging / structlog
- **理由**：零配置即可用，格式美观，支持结构化日志、rotation、retention，API 极简
- **集成方式**：
  - 拦截 stdlib logging（uvicorn/sqlalchemy 等库的日志）统一走 loguru
  - FastAPI 请求日志通过 middleware 记录（method, path, status, duration）
  - 配置项：日志级别、输出文件路径、rotation 策略，均从 .env 读取

### 6. 项目结构：按职责分层

```
app/
├── api/          # HTTP 层
├── agents/       # Agent 定义
├── tools/        # Agent Tools
├── skills/       # agno Skills（已有）
├── core/         # 横切关注点
├── models/       # ORM 模型
├── schemas/      # 请求/响应
├── services/     # 业务逻辑
└── utils/        # 工具函数
```

## Risks / Trade-offs

- **[agno Team router 准确性]** → 对子 Agent 的 description 要描述清晰，确保路由准确；兜底到通用回复
- **[Token 鉴权为简化假设]** → Phase 1 假设上游已认证，仅做 token 解析；后续可对接 SSO/OAuth
- **[无会话管理]** → 每次请求独立，无上下文记忆；后续通过 agno Storage 补充
