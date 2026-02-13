## Context

业务 DB 使用 PostgreSQL + asyncpg，本地开发需部署 PG。项目尚无对话记忆，每次请求独立。需切换为 SQLite 降低本地门槛，并引入 agno 短期记忆。

## Goals / Non-Goals

**Goals:**
- 业务 DB 切换为 SQLite (aiosqlite)，本地零依赖
- 新增 agno 会话存储（SqliteDb），按 user_id + session_id 持久化对话历史
- 应用启动自动建表
- seed 脚本适配 SQLite 语法

**Non-Goals:**
- 不做数据迁移（本地开发环境，seed 重建即可）
- 不做长期记忆（Memory）
- 不做会话管理 API（列出/删除会话），后续需求

## Decisions

### 1. 两个 SQLite 文件分离

业务 DB 和 Agent 会话 DB 使用独立文件：
- `data/xm_agent.db` — 业务数据（SQLAlchemy engine）
- `data/agent_sessions.db` — agno 对话历史（agno SqliteDb）

**理由**：业务 DB 可随时 seed 重建不影响对话历史；两者生命周期和备份策略不同。

### 2. SQLite 外键约束

通过 SQLAlchemy event listener 在每次连接时执行 `PRAGMA foreign_keys = ON`。

### 3. 应用启动建表

在 FastAPI lifespan 中调用 `metadata.create_all` 自动建表，免去手动执行 SQL。同时创建 `data/` 目录（如不存在）。

### 4. session_id 由前端管理

ChatRequest 新增 `session_id: str | None`。前端传入则续接对话，不传则后端生成新 UUID 并在 ChatResponse 中返回。

### 5. agno SqliteDb 作为 Team 的 db 参数

`create_router_team(roles)` 接收共享的 `SqliteDb` 实例，传给 Team。每次请求创建 Team 实例但共享同一个 db 连接。

### 6. seed 脚本适配

- `TRUNCATE TABLE ... CASCADE` → `DELETE FROM`（倒序删除，尊重外键）
- 移除 `setval(pg_get_serial_sequence(...))` — SQLite autoincrement 无需手动重置
- `BEGIN` / `COMMIT` 保留，SQLite 支持

## Risks / Trade-offs

- **SQLite 并发写入限制** → 单进程开发环境足够；生产部署可切回 PG（只改 DATABASE_URL + 驱动）
- **time 类型存为 TEXT** → SQLAlchemy 自动处理序列化/反序列化，查询兼容
- **data/ 目录不在版本控制** → 加入 .gitignore
