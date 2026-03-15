## Context

当前项目通过静态 tools 列表 + 提示词 + Tool 层运行时校验实现权限控制。Agno 2.5+ 原生支持 callable tools factory，可在每次 run 时根据 `run_context.session_state` 动态返回 tools 列表。

已有权限角色：
- `employee`: 基础员工权限（所有用户默认拥有）
- `manager`: 部门主管权限
- `admin`: 管理者权限（HR 全公司数据）
- `talent_dev`: 人才发展权限
- `it_admin`: IT 管理员权限
- `admin_staff`: 行政管理员权限
- `finance`: 财务权限
- `legal`: 法务权限

## Goals / Non-Goals

**Goals:**
- 各 Agent 的 tools 改为工厂函数，根据 roles 动态返回可用 tools
- 简化 Agent instructions，移除权限说明段落
- 移除 Tool 层冗余的权限校验（角色检查），保留身份提取逻辑

**Non-Goals:**
- 不改变现有的 roles 定义和权限划分逻辑
- 不调整 router_team 的 members（Team 成员保持静态）
- 不修改 Tool 的业务逻辑

## Decisions

### 1. Tools 工厂函数签名

使用 Agno 支持的 `run_context` 参数注入：

```python
def get_hr_tools(run_context: RunContext) -> list[Callable]:
    roles = run_context.session_state.get("roles", [])
    tools = list(employee_tools)  # 基础权限
    if "manager" in roles:
        tools.extend(manager_tools)
    if "admin" in roles:
        tools.extend(admin_tools)
    if "talent_dev" in roles:
        tools.extend(talent_dev_tools)
        tools.extend(discovery_tools)
    return tools
```

**选择理由**：Agno 自动将 `run_context` 注入到工厂函数，无需额外配置。

### 2. 缓存策略

使用 Agno 默认的按 `user_id`/`session_id` 缓存，无需自定义 `callable_tools_cache_key`。

**选择理由**：当前 roles 绑定在 JWT token 中，同一 session 内 roles 不变，默认缓存策略足够。

### 3. 权限校验函数处理

| 函数 | 当前行为 | 重构后 |
|------|----------|--------|
| `get_employee_id` | 提取 employee_id | 保留，无变化 |
| `get_manager_info` | 校验 manager + 提取 dept_id | 移除角色校验，仅提取 dept_id |
| `get_admin_id` | 校验 admin | 移除（动态 tools 已隔离） |
| `get_talent_dev_id` | 校验 talent_dev | 移除（动态 tools 已隔离） |

### 4. Instructions 简化

移除各 Agent 中 "## 部门主管权限"、"## 管理者权限" 等段落，因为 LLM 只能看到它有权限的 tools，不需要再用提示词约束。

保留：角色定义、能力范围、行为准则。

## Risks / Trade-offs

| 风险 | 缓解措施 |
|------|----------|
| 移除 Tool 层校验后，若工厂函数有 bug 可能导致越权 | 保留 tools/utils.py 的身份提取逻辑，关键 tools 可添加断言校验 |
| 缓存导致 roles 变更不生效 | 当前 roles 在 JWT 中，session 内不变，问题不大；如需实时刷新可设置 `cache_callables=False` |
| instructions 简化后 LLM 行为可能变化 | 分 Agent 灰度验证，保留核心行为准则 |
