## Context

项目当前手工搭建 FastAPI，手写 chat 端点、session 管理、auth。agno AgentOS 提供完整生产运行时。迁移后可用内置 SSE 聊天 API、JWT 认证、session 存储、tracing、Control Plane UI。

HR Agent 之前按 roles 动态过滤 tools。迁移到 AgentOS 后改为全量 tools 单实例，Tool 层通过 session_state.roles 校验权限（方案 A）。LLM 可能尝试调用无权 tools 导致错误响应，但架构更简单且完全兼容 AgentOS 静态注册模型。

## Goals / Non-Goals

**Goals:**
- 用 AgentOS 替代自定义 chat API、session 管理、auth
- HR Agent 全量 tools + Tool 层权限校验
- 保留自定义 middleware、exception handlers、业务路由作为 base_app
- 保留业务 DB 及 init_db 逻辑
- JWT claims 包含 roles、department_id，通过 session_state_claims 自动注入

**Non-Goals:**
- 不迁移业务 DB 到 AgentOS db（业务数据独立）
- 不使用 AgentOS 内置 RBAC scopes（用 Tool 层自定义权限校验）
- 不做 Control Plane UI 对接（后续）
- 不引入 Knowledge / Memory / Evals（后续）

## Decisions

### 1. AgentOS 作为入口，现有 FastAPI 作为 base_app

```python
agent_os = AgentOS(
    agents=[hr_agent],
    teams=[router_team],
    base_app=base_app,  # 保留自定义 middleware、exception handlers、业务路由
    db=SqliteDb(db_file="data/agent_sessions.db"),
    lifespan=lifespan,  # 保留 init_db
    tracing=True,
)
```

**理由**：最小侵入，自定义路由和 middleware 继续工作。

### 2. HR Agent 全量 tools + Tool 层权限

不再动态过滤 tools。单一 HR Agent 包含 employee_tools + manager_tools。主管 tools 内部通过 `session_state.get("roles")` 校验。

**理由**：AgentOS 注册静态实例，不支持每次请求动态创建。Tool 层已有权限校验逻辑，改动最小。

### 3. JWTMiddleware + session_state_claims

```python
app.add_middleware(
    JWTMiddleware,
    verification_keys=[settings.AUTH_SECRET],
    algorithm="HS256",
    user_id_claim="employee_id",
    session_state_claims=["employee_id", "roles", "department_id"],
)
```

JWT payload 示例：
```json
{
    "sub": "9",
    "employee_id": 9,
    "employee_no": "XM0009",
    "name": "郑晓明",
    "roles": ["employee", "manager"],
    "department_id": 2,
    "exp": 1740000000
}
```

**理由**：AgentOS 原生支持，零代码实现 session_state 注入。角色变更需重签 token，对内部系统可接受。

### 4. Agent/Team 需要 id 字段

AgentOS 通过 id 路由请求（如 `/teams/router-team/runs`），Agent 和 Team 需设置 `id` 字段。

### 5. 保留 base_app 自定义路由

业务路由（如未来的会话管理 API）继续通过 base_app 提供。AgentOS 和自定义路由共存。

## Risks / Trade-offs

- **LLM 调用无权 tools** → Tool 返回权限错误文案，LLM 转述给用户。体验略差但可接受。
- **roles 写入 JWT** → 角色变更需重签 token。内部系统 token 有效期短可缓解。
- **移除自定义 chat 端点** → 前端需改调 AgentOS API（`/teams/router-team/runs`）。
- **agno 版本要求** → 需确认当前 agno 版本支持 AgentOS（>= 2.1.0）。
