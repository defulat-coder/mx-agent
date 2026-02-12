## Why

当前业务数据库依赖 PostgreSQL，开发和本地测试需额外部署 PG 实例，增加环境搭建成本。同时项目尚无对话记忆能力，每次请求独立无上下文。需要切换为 SQLite 降低本地门槛，并引入 agno 短期记忆（按用户+会话持久化对话历史）。

## What Changes

- **BREAKING** 业务 DB 从 PostgreSQL (asyncpg) 切换为 SQLite (aiosqlite)
- 依赖变更：移除 asyncpg，新增 aiosqlite
- 配置默认值调整：DATABASE_URL 改为 sqlite+aiosqlite 格式
- seed 脚本适配 SQLite 语法（TRUNCATE → DELETE FROM，移除 pg 序列重置）
- SQLite 外键约束需在连接时显式开启
- 新增 agno 会话存储（SqliteDb），独立文件存放对话历史
- ChatRequest/ChatResponse 增加 session_id 字段
- chat.py 传递 session_id + user_id 给 Team.arun()
- 新增应用启动时自动建表逻辑（metadata.create_all）

## Capabilities

### New Capabilities
- `session-memory`: Agent 短期记忆能力，按用户+会话持久化对话历史，支持多轮对话

### Modified Capabilities
- `database`: 从 PostgreSQL 切换为 SQLite，连接方式和初始化逻辑变更

## Impact

- `app/core/database.py` — 引擎 URL 格式变更，新增外键 pragma、建表逻辑
- `app/config.py` — DATABASE_URL 默认值
- `.env` — DATABASE_URL 值
- `pyproject.toml` — asyncpg → aiosqlite
- `scripts/generate_seed.py` — SQLite 语法适配
- `app/agents/router_agent.py` — Team 增加 db 参数
- `app/api/v1/endpoints/chat.py` — 传递 session_id/user_id
- `app/schemas/chat.py` — ChatRequest/ChatResponse 增加 session_id
