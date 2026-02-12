## Why

基于已搭建的项目框架，实现 HR 员工智能助手的完整业务功能。员工需要一个统一入口来查询个人薪资、社保、考勤等信息，咨询公司制度政策，以及发起请假/加班等业务办理。

## What Changes

- 创建 HR 业务数据库模型（employees, salary_records, attendance_records 等 8 张表）
- 实现 7 个数据查询 Tools（个人信息/薪资/社保/考勤/假期余额/请假记录/加班记录）
- 实现 3 个业务办理 Action Tools（请假申请/加班登记/报销申请 → 生成审批链接）
- 完善 HR Agent，接入 Tools + Skills
- 为所有 Tool 实现 employee_id 强制过滤

## Capabilities

### New Capabilities

- `hr-data-models`: HR 业务数据库模型定义（8 张表的 ORM 模型）
- `hr-query-tools`: HR 数据查询 Tools（员工信息/薪资/社保/考勤/假期/请假/加班）
- `hr-action-tools`: HR 业务办理 Tools（请假申请/加班登记/报销申请 → 审批链接）
- `hr-agent-impl`: HR Agent 完整实现（system prompt + tools + skills 组装）

### Modified Capabilities

（无，基于 project-scaffold 新增）

## Impact

- 新增 app/models/hr/ 下 8 个 ORM 模型文件
- 新增 app/tools/hr/ 下 query.py 和 action.py
- 完善 app/agents/hr_agent.py（从占位变为完整实现）
- 新增 app/schemas/hr.py（HR 相关请求/响应 schema）
- 新增 app/services/hr.py（HR 业务查询逻辑）
