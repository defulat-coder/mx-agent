# MX Agent 重构日志

日期：2026-06-19

## 目标

持续重构 MX Agent，直到当前架构达到满意状态。每个重要步骤都需要：

- 运行 live 验证；
- 执行自审；
- 提交已完成的步骤；
- 在本文档记录结果。

## 约束

- 保留无关的工作区改动。
- 不提交生成的运行时数据、密钥、缓存或本地 artifact。
- 后端改动先跑聚焦的 pytest 目标；如果改动触及共享行为，再扩大到完整测试套件。
- 前端改动使用 `pnpm lint` 和 `pnpm build` 验证。
- 项目说明里配置了 CodeGraph，但当前 checkout 未初始化，因此结构探索先基于仓库文件和测试进行，除非后续构建索引。

## 基线

- 分支：`codex/monorepo-migration`
- 本轮工作前已存在的未跟踪路径：`.codex/`
- 初始项目结构：
  - 后端：FastAPI/Agno 应用位于 `backend/app`
  - 前端：Next.js 应用位于 `frontend`
  - 规范：`openspec/`
  - 既有设计和计划文档：`docs/superpowers/`

## 进展

### Step 0 - 基线与定向

状态：已完成

验证：

- 后端修复前基线：`uv run pytest` -> 92 passed, 10 failed。
- 前端基线：`pnpm lint` -> passed。
- 前端基线：`pnpm build` -> passed。

备注：

- 仓库根目录尚未提供 `CONTEXT.md` 和 `docs/adr/` 等领域文档。本轮采用 `AGENTS.md`、`docs/` 和 `openspec/` 中已有的领域与架构语言。
- 后端失败集中在 AgentOS 与 monorepo 迁移后的旧 API/auth/config 预期上：缺失 `/v1/chat`、`/health` 仍按旧 404 行为断言、AgentOS auth 错误形状不同，以及 SQLite 替代旧 PostgreSQL 默认值。

### Step 1 - 恢复稳定的 chat API 门面

状态：已完成

架构改动：

- 在 AgentOS `router_team` 之上增加产品级 `POST /v1/chat` 门面。
- 增加 `ChatRequest` 和 `ChatResponse` schema，让外部客户端继续使用稳定 API，而不暴露 AgentOS 内部路由。
- 在 chat 门面中解析 JWT claims，并转换为 AgentOS `session_state`，保持工具层身份校验不变。
- 将 `/v1/chat` 从 AgentOS `JWTMiddleware` 中排除，让该产品端点继续返回项目统一错误响应。
- 更新 API/config 测试，使其匹配当前 AgentOS runtime 和 SQLite 后端默认值。

验证：

- 聚焦测试：`uv run pytest tests/test_api.py tests/test_auth.py tests/test_config.py` -> 14 passed。
- 完整后端测试：`uv run pytest` -> 102 passed。
- 8001 端口 live HTTP 检查：
  - `GET /health` -> 200，包含 `X-Request-ID` 和 `X-Trace-Id`。
  - `POST /v1/chat` 无 token -> 401，`code=40101`。
  - `POST /v1/chat` 无效 token -> 401，`code=40103`。

自审：

- 该门面刻意保持很薄：只做请求校验、JWT 到 session_state 的适配，以及 AgentOS 输出归一化。
- 测试 mock 了 team 调用，因此 API 契约测试不依赖真实 LLM 凭据。
- 已知剩余问题：chat 门面的 auth 与 AgentOS JWT validation 有一部分重复。当前保留这点是为了维持产品 API 的统一错误响应；后续可以继续抽取共享 JWT claims adapter。

### Step 2 - 抽取 JWT claims adapter

状态：已完成

架构改动：

- 增加 `app.core.auth`，统一承载 bearer token 提取、JWT 解码、错误码映射、AgentOS `session_state` 构建，以及 AgentOS `user_id` 派生。
- 在 AgentOS middleware 配置和 chat 门面路径中复用同一个 `SESSION_STATE_CLAIMS` 常量，减少 runtime auth 配置与工具身份上下文之间的漂移。
- 增加契约测试，证明 `/v1/chat` 会把 JWT claims 中的 `employee_id`、`roles`、`department_id` 传入 `router_team.arun`。

验证：

- 聚焦测试：`uv run pytest tests/test_api.py tests/test_auth.py` -> 13 passed。
- 完整后端测试：`uv run pytest` -> 103 passed。
- 8001 端口 live HTTP 检查：
  - `GET /health` -> 200，包含 request 和 trace ID。
  - `POST /v1/chat` 无 token -> 401，`code=40101`。
  - `POST /v1/chat` 无效 token -> 401，`code=40103`。

自审：

- endpoint 不再持有 JWT 解析细节；现在只组合门面请求、auth claims adapter 和 router team 调用。
- auth 模块目前只覆盖产品 API 的认证需求，不替代 AgentOS 内置路由的 middleware validation。

### Step 3 - 拆分 HR 员工自助查询

状态：已完成

架构改动：

- 将 `app.services.hr` 从单一大模块转换成 package，同时保持公开导入路径 `from app.services import hr as hr_service` 不变。
- 将员工自助查询函数移动到 `app.services.hr.employee`：
  - `get_employee_info`
  - `get_salary_records`
  - `get_social_insurance`
  - `get_attendance`
  - `get_leave_balance`
  - `get_leave_requests`
  - `get_overtime_records`
- 从 `app.services.hr` re-export 这些函数，现有 HR tools 无需修改。

验证：

- 导入兼容检查：`from app.services import hr as hr_service` 以及必需函数存在性 -> passed。
- 聚焦测试：`uv run pytest tests/test_auth.py tests/test_api.py` -> 13 passed。
- 完整后端测试：`uv run pytest` -> 103 passed。
- 8001 端口 live HTTP 检查：
  - `GET /health` -> 200。
  - `POST /v1/chat` 无 token -> 401，`code=40101`。

自审：

- 这是纯结构拆分；没有改查询逻辑，也没有改工具调用点。
- `app.services.hr.__init__` 当时仍然较大，但 package 结构已经给后续 HR slice 提供了稳定迁移位置，且不需要改变调用方。

### Step 4 - 拆分 HR 主管 service 查询

状态：已完成

架构改动：

- 将主管范围内的团队查询、范围 helper、主管审批移动到 `app.services.hr.manager`。
- 从 `app.services.hr` re-export 主管函数，使现有工具模块继续使用同一个 `hr_service.*` 接口。
- 将员工名和部门名 map helper 保留在 manager slice 中，并为了剩余 admin 汇总函数进行私有 re-export。

验证：

- 主管导出兼容检查 -> passed。
- 完整后端测试：`uv run pytest` -> 103 passed。
- 8001 端口 live HTTP 检查：
  - `GET /health` -> 200。
  - `POST /v1/chat` 无 token -> 401，`code=40101`。

自审：

- 这同样是结构拆分；查询函数体和调用点没有行为变化。
- `app.services.hr.__init__` 降到 945 行。剩余最大 slice 是 admin/reporting/talent-development，已经可以继续拆分而不改变外部 import。

### Step 5 - 拆分 HR 管理员与报表 service 查询

状态：已完成

架构改动：

- 将管理员范围内的员工查询、全公司考勤/请假/加班查询、报表和管理员审批移动到 `app.services.hr.admin`。
- 从 `app.services.hr` re-export admin 函数，保留现有 `hr_service.*` 调用方。
- 将 talent-development 函数暂留在 `app.services.hr.__init__`，作为最后一个大 slice 单独评估。

验证：

- admin 导出兼容检查 -> passed。
- 完整后端测试：`uv run pytest` -> 103 passed。
- 8001 端口 live HTTP 检查：
  - `GET /health` -> 200。
  - `POST /v1/chat` 无 token -> 401，`code=40101`。

自审：

- 拆分基于上一版已提交模块中的 section marker 进行，没有修改函数体。
- `app.services.hr.__init__` 降到 585 行。HR service package 已经具备明确的 employee、manager、admin slice。

### Step 6 - 拆分 HR 人才发展 service 查询

状态：已完成

架构改动：

- 将人才发展相关的员工详情、培训、九宫格、绩效、流动、晋升、IDP 和员工搜索查询移动到 `app.services.hr.talent`。
- 将 `app.services.hr.__init__` 替换为显式 re-export 模块和 `__all__`，保留现有工具所依赖的 `hr_service.*` 接口。

验证：

- 代表性 HR 导出兼容检查 -> passed。
- 完整后端测试：`uv run pytest` -> 103 passed。
- 8001 端口 live HTTP 检查：
  - `GET /health` -> 200。
  - `POST /v1/chat` 无 token -> 401，`code=40101`。

自审：

- HR service 的深度显著提升：原本 1630 行的 `hr.py` 现在变成按角色组织的 package，并由 107 行导出面统一暴露。
- 没有修改任何 tool 调用点；本次重构聚焦于 locality 和可导航性。
