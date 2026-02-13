## 1. 依赖与配置

- [x] 1.1 pyproject.toml — 移除 asyncpg，新增 aiosqlite
- [x] 1.2 app/config.py — DATABASE_URL 默认值改为 sqlite+aiosqlite:///data/xm_agent.db
- [x] 1.3 .env — DATABASE_URL 改为 SQLite 路径
- [x] 1.4 .gitignore — 添加 data/ 目录

## 2. 数据库初始化

- [x] 2.1 app/core/database.py — SQLite 外键 pragma event listener + 建表逻辑（init_db 函数）
- [x] 2.2 app/main.py — lifespan 中调用 init_db 自动建表

## 3. Seed 脚本适配

- [x] 3.1 scripts/generate_seed.py — TRUNCATE → DELETE FROM，移除 pg 序列重置

## 4. Agent 会话存储

- [x] 4.1 app/agents/router_agent.py — 新增 SqliteDb 实例，create_router_team 传入 db 参数
- [x] 4.2 app/schemas/chat.py — ChatRequest 增加 session_id: str | None，ChatResponse 增加 session_id: str
- [x] 4.3 app/api/v1/endpoints/chat.py — 生成/传递 session_id + user_id 给 team.arun()
