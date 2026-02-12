## 1. HR 数据模型

- [x] 1.1 创建 app/models/hr/employee.py — Employee ORM 模型
- [x] 1.2 创建 app/models/hr/department.py — Department ORM 模型
- [x] 1.3 创建 app/models/hr/salary.py — SalaryRecord ORM 模型
- [x] 1.4 创建 app/models/hr/social_insurance.py — SocialInsuranceRecord ORM 模型
- [x] 1.5 创建 app/models/hr/attendance.py — AttendanceRecord ORM 模型
- [x] 1.6 创建 app/models/hr/leave.py — LeaveBalance + LeaveRequest ORM 模型
- [x] 1.7 创建 app/models/hr/overtime.py — OvertimeRecord ORM 模型
- [x] 1.8 创建 app/models/hr/__init__.py — 统一导出所有模型

## 2. HR Schema

- [x] 2.1 创建 app/schemas/hr.py — 所有 HR 相关 Pydantic response schema

## 3. HR Service 层

- [x] 3.1 创建 app/services/hr.py — 7 个查询方法（get_employee_info, get_salary_records, get_social_insurance, get_attendance, get_leave_balance, get_leave_requests, get_overtime_records），全部接收 employee_id 参数强制过滤

## 4. HR Query Tools

- [x] 4.1 创建 app/tools/hr/query.py — 7 个 agno tool 函数，从 RunContext 获取 employee_id，调用 service 层

## 5. HR Action Tools

- [x] 5.1 创建 app/tools/hr/action.py — 3 个 action tool（apply_leave, apply_overtime, apply_reimbursement），返回审批系统链接
- [x] 5.2 创建 app/tools/hr/__init__.py — 统一导出所有 tools

## 6. HR Agent 实现

- [x] 6.1 编写 HR Agent system prompt
- [x] 6.2 完善 app/agents/hr_agent.py — 组装 system prompt + query tools + action tools + skills
