# 马喜智能助手 (xm-agent)

基于 FastAPI + Agno 的企业级 AI 智能助手，支持 HR、财务、法务等多领域智能问答与业务办理。

## 技术栈

- **Python** >= 3.13
- **FastAPI** + **Uvicorn** — Web 框架
- **Agno** — AI 智能体框架
- **OpenAI** — LLM 接口
- **SQLAlchemy** + **aiosqlite** — 异步 ORM
- **Pydantic Settings** — 配置管理
- **Loguru** — 日志
- **PyJWT** — 认证

## 项目结构

```
app/
├── main.py              # FastAPI + AgentOS 入口
├── config.py            # 环境变量配置
├── agents/              # 智能体定义（路由/HR/财务/法务）
├── api/v1/              # REST API 路由
├── core/                # 中间件、异常、数据库、日志
├── models/              # SQLAlchemy ORM 模型
├── schemas/             # Pydantic 请求/响应 Schema
├── services/            # 业务逻辑层
├── skills/              # Agent Skills（制度知识库）
├── tools/               # Agent Tools（数据查询/业务办理）
└── utils/               # 工具函数
```

## 快速启动

```bash
# 安装依赖
uv sync

# 配置环境变量
cp .env.example .env  # 修改 .env 中的配置

# 启动服务
uv run python main.py
```

服务默认运行在 `http://localhost:8000`。

## 已实现功能

- **路由智能体** — 自动分发请求到对应领域助手
- **HR 助手** — 制度咨询、员工数据查询、请假/加班/报销办理、主管审批
- **财务助手** — 开发中
- **法务助手** — 开发中
