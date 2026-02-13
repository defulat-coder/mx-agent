## 1. Agent 层改造

- [x] 1.1 更新 app/agents/hr_agent.py — 全量 tools 单实例（移除 create_hr_agent 工厂），添加 id 字段，prompt 合并员工+主管
- [x] 1.2 更新 app/agents/router_agent.py — 静态 router_team 实例（移除 create_router_team 工厂），添加 id 字段，移除 SqliteDb（交给 AgentOS 管理）

## 2. AgentOS 入口

- [x] 2.1 重写 main.py — AgentOS 入口，base_app 保留自定义 middleware/exception/业务路由，JWTMiddleware 配置，lifespan 保留 init_db
- [x] 2.2 确认 pyproject.toml agno 版本支持 AgentOS（>= 2.4.8，满足）

## 3. 清理旧代码

- [x] 3.1 移除 app/core/auth.py — JWTMiddleware 替代
- [x] 3.2 移除 app/core/deps.py — AgentOS 自动注入替代
- [x] 3.3 移除 app/api/v1/endpoints/chat.py — AgentOS 内置 API 替代
- [x] 3.4 清理 app/schemas/auth.py 和 app/schemas/chat.py — 移除不再需要的 schema
- [x] 3.5 更新 app/api/v1/router.py — 移除 chat 路由引用

## 4. Token 适配

- [x] 4.1 新建 scripts/generate_token.py — JWT payload 包含 employee_id、roles、department_id、employee_no、name
