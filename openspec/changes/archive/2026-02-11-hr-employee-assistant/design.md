## Context

project-scaffold 已建立 FastAPI + agno + SQLAlchemy 基础框架、Router Agent 路由分发、鉴权机制。现在需要在此基础上实现 HR Agent 的完整业务能力，面向员工角色。

已有 8 个 HR Skills（考勤/假期/薪酬/社保/入职/离职/报销/培训）在 `app/skills/hr/` 下。

## Goals / Non-Goals

**Goals:**
- 完整的 HR 数据模型（8 张表）
- 7 个只读查询 Tools，全部强制 employee_id 过滤
- 3 个 Action Tools，收集信息后返回审批系统链接
- HR Agent 组装 Tools + Skills，能处理员工所有 HR 相关问题

**Non-Goals:**
- 不实现审批流程本身（只生成链接）
- 不实现数据写入（leave_requests 等由审批系统管理）
- 不实现部门主管/管理者角色的查询权限
- 不做数据 migration 脚本（后续补充）

## Decisions

### 1. Tool 通过 RunContext 获取 employee_id

agno 的 `RunContext` 机制可以在 Agent.run() 时注入上下文数据。所有 Tool 函数签名接收 `run_context: RunContext`，从中取 `employee_id`。

```python
@tool
async def get_salary_records(run_context: RunContext, year_month: str = None):
    employee_id = run_context.employee_id
    # 查询时强制 WHERE employee_id = employee_id
```

### 2. Service 层封装数据库查询

Tool 不直接写 SQL，而是调用 Service 层。Service 接收 employee_id + 查询参数，返回结构化数据。

```
Tool (参数校验 + 格式化) → Service (业务查询) → DB Session
```

### 3. Action Tool 返回结构化 action 对象

Action Tool 不执行写操作，而是返回一个 action 对象，包含审批链接和预填参数：

```python
{
    "type": "redirect",
    "url": "https://hr.example.com/leave/apply?employee_id=xxx&start=2026-02-15&end=2026-02-16",
    "message": "已为您准备好请假申请，点击链接前往审批系统提交"
}
```

### 4. HR Agent System Prompt 设计

明确角色边界：
- 你是 HR 员工助手，只能回答 HR 相关问题
- 只能查询当前登录员工的数据
- 涉及制度咨询时优先使用 Skills
- 涉及具体数据时调用 Tools
- 涉及业务办理时收集必要信息后引导到审批系统

## Risks / Trade-offs

- **[数据真实性]** → 当前无真实数据，需要后续对接实际 HR 系统或导入种子数据
- **[审批链接格式]** → 实际审批系统 URL 格式待确认，先用占位 URL
- **[Skills 内容准确性]** → 预设制度内容为模板，需替换为公司实际制度
