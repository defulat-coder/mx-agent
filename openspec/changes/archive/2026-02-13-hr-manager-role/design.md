## Context

HR 员工助手当前只支持普通员工角色。所有 Tool 通过 `run_context.session_state["employee_id"]` 强制数据隔离，只能查询自己的数据。数据模型中 `Department.manager_id` 已关联部门负责人，部门支持 `parent_id` 树形层级。

需要在同一个 Agent 内扩展主管角色，让部门主管可以查看团队数据并审批下属申请。

## Goals / Non-Goals

**Goals:**
- 主管可查看管辖范围内（递归子部门）所有员工的考勤、请假、假期余额、加班数据
- 主管可查看下属员工档案（基本信息 + 绩效考评历史 + 在职履历）
- 主管可审批下属的请假申请和加班申请
- 主管同时保留员工身份的所有能力（查自己薪资/社保等）
- 权限校验：Tool 层 + Service 层双重校验

**Non-Goals:**
- 主管不可查看下属薪资和社保数据
- 不涉及多级审批流（只做直接主管审批）
- 不涉及主管角色的动态授权/撤销（通过 session_state 传入，由上游认证系统决定）

## Decisions

### 1. 同一个 Agent，按角色动态加载 Tools

**选择**：在 `hr_agent.py` 中提供工厂函数 `create_hr_agent(role, ...)` 按角色拼装不同 tools 列表。

**理由**：主管也是员工，需要查自己的薪资/考勤。拆成两个 Agent 需要在 Router 层做角色判断和转发，增加复杂度且跨 Agent 切换体验差。

### 2. session_state 扩展

```python
session_state = {
    "employee_id": int,
    "role": "employee" | "manager",
    "department_id": int | None,  # 主管时为其管辖的部门 ID
}
```

`role` 和 `department_id` 由上游认证中间件写入，Agent 层只读取不修改。

### 3. 递归子部门查询

Service 层提供 `get_managed_department_ids(session, department_id) -> list[int]`，使用 PostgreSQL 递归 CTE 查询所有子部门 ID（含自身）。

主管 Tool 调用此方法获取管辖范围，再按 `employee.department_id IN (...)` 过滤团队成员。

### 4. 权限校验双层设计

- **Tool 层**：检查 `session_state["role"] == "manager"`，非主管直接返回错误提示
- **Service 层**：验证 `department.manager_id == employee_id`，防止伪造 role 绕过

### 5. 审批直接更新数据库

审批操作直接更新 `leave_requests.status` / `overtime_records.status`，不走外部审批系统链接。与员工端 `apply_leave`（返回审批链接）区分：员工是发起申请，主管是处理申请。

### 6. 主管 Tools 文件组织

```
app/tools/hr/
├── query.py             # 员工查询（现有）
├── action.py            # 员工办理（现有）
├── manager_query.py     # 主管团队查询 + 员工档案查询（新增）
├── manager_action.py    # 主管审批（新增）
└── __init__.py          # 统一导出，新增 manager_tools
```

### 7. 员工档案数据模型

新增两张表，存储绩效考评和在职履历：

```
app/models/hr/
├── performance_review.py   # 绩效考评表（新增）
└── employment_history.py   # 在职履历表（新增）
```

**performance_reviews 表**：employee_id, year, half(上半年/下半年), rating(A/B+/B/C/D), score, reviewer, comment, created_at

**employment_histories 表**：employee_id, start_date, end_date, department, position, level, change_type(入职/转正/晋升/调岗/降级), remark

员工档案查询 `get_employee_profile` 聚合基本信息 + 绩效列表 + 履历列表返回，不包含薪资和社保。

## Risks / Trade-offs

- **递归 CTE 性能** → 部门层级通常不超过 5 层，数据量小，性能可控。如未来部门数量激增可加缓存。
- **role 来源信任** → 依赖上游认证系统正确设置 session_state。Service 层兜底校验 manager_id 防绕过。
- **审批并发** → 同一申请可能被重复审批。通过 status 前置检查（只允许从"待审批"变更）避免重复操作。
