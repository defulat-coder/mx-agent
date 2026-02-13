## Why

HR 员工助手目前只支持普通员工角色，部门主管无法查看团队数据和审批下属申请，需要扩展主管角色能力。

## What Changes

- 新增主管团队查询 Tools：团队成员列表、团队考勤、团队请假记录、团队假期余额、团队加班记录（递归子部门）
- 新增主管审批 Tools：审批请假申请、审批加班申请（直接更新数据库状态）
- 新增员工档案查询 Tool：主管可查看下属完整档案（基本信息 + 绩效考评历史 + 在职履历）
- 新增数据模型：绩效考评表（performance_reviews）、在职履历表（employment_histories）
- 新增主管 Service 层：递归获取管辖部门 ID 列表、团队查询方法、审批方法、档案查询方法（含权限校验）
- 新增主管相关 Schema：团队成员响应、审批请求/响应、档案响应
- 改造 HR Agent：session_state 增加 role/department_id，按角色动态拼装 tools，system prompt 增加主管行为准则
- **限制**：主管不可查看下属薪资和社保数据

## Capabilities

### New Capabilities
- `hr-manager-query-tools`: 主管团队查询 Tools（团队成员、考勤、请假、假期余额、加班、员工档案），递归子部门范围
- `hr-manager-action-tools`: 主管审批 Tools（审批请假、审批加班），含权限校验
- `hr-employee-profile-models`: 员工档案数据模型（绩效考评表 + 在职履历表）

### Modified Capabilities
- `hr-agent-impl`: system prompt 增加主管角色说明，按 role 动态加载主管 tools

## Impact

- `app/models/hr/` — 新增 performance_review.py、employment_history.py
- `app/tools/hr/` — 新增 manager_query.py、manager_action.py
- `app/services/hr.py` — 新增递归部门查询、团队查询、审批方法、档案查询方法
- `app/schemas/hr.py` — 新增主管相关 Schema、档案相关 Schema
- `app/agents/hr_agent.py` — session_state 扩展、tools 动态拼装、system prompt 改造
- `app/tools/hr/__init__.py` — 导出主管 tools
- `scripts/generate_seed.py` — 新增绩效考评和在职履历测试数据
