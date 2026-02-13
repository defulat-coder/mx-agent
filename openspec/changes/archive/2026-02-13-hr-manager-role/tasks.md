## 1. 数据模型层

- [x] 1.1 创建 app/models/hr/performance_review.py — PerformanceReview ORM 模型
- [x] 1.2 创建 app/models/hr/employment_history.py — EmploymentHistory ORM 模型
- [x] 1.3 更新 app/models/hr/__init__.py — 导出 PerformanceReview、EmploymentHistory

## 2. Schema 层

- [x] 2.1 在 app/schemas/hr.py 新增 TeamMemberResponse（姓名、工号、部门、岗位、职级、状态）
- [x] 2.2 在 app/schemas/hr.py 新增 TeamAttendanceResponse（员工姓名 + 考勤字段）
- [x] 2.3 在 app/schemas/hr.py 新增 TeamLeaveRequestResponse（员工姓名 + 请假字段 + request_id）
- [x] 2.4 在 app/schemas/hr.py 新增 TeamLeaveBalanceResponse（员工姓名 + 假期余额字段）
- [x] 2.5 在 app/schemas/hr.py 新增 TeamOvertimeRecordResponse（员工姓名 + 加班字段 + record_id）
- [x] 2.6 在 app/schemas/hr.py 新增 ApprovalResponse（success, request_id, action, message）
- [x] 2.7 在 app/schemas/hr.py 新增 PerformanceReviewResponse（year, half, rating, score, reviewer, comment）
- [x] 2.8 在 app/schemas/hr.py 新增 EmploymentHistoryResponse（start_date, end_date, department, position, level, change_type, remark）
- [x] 2.9 在 app/schemas/hr.py 新增 EmployeeProfileResponse（基本信息 + 绩效列表 + 履历列表）

## 3. Service 层

- [x] 3.1 在 app/services/hr.py 新增 get_managed_department_ids — 递归 CTE 查询管辖部门 ID 列表
- [x] 3.2 在 app/services/hr.py 新增 get_managed_employee_ids — 获取管辖范围内所有员工 ID（含权限校验）
- [x] 3.3 在 app/services/hr.py 新增 get_team_members — 查询团队成员列表
- [x] 3.4 在 app/services/hr.py 新增 get_team_attendance — 查询团队考勤（支持指定员工/异常过滤）
- [x] 3.5 在 app/services/hr.py 新增 get_team_leave_requests — 查询团队请假记录（支持 status 过滤）
- [x] 3.6 在 app/services/hr.py 新增 get_team_leave_balances — 查询团队假期余额（支持指定员工）
- [x] 3.7 在 app/services/hr.py 新增 get_team_overtime_records — 查询团队加班记录（支持 status 过滤）
- [x] 3.8 在 app/services/hr.py 新增 get_employee_profile — 查询员工档案（基本信息 + 绩效 + 履历，含范围校验）
- [x] 3.9 在 app/services/hr.py 新增 approve_leave_request — 审批请假（状态校验 + 范围校验 + 更新）
- [x] 3.10 在 app/services/hr.py 新增 approve_overtime_request — 审批加班（状态校验 + 范围校验 + 更新）

## 4. 主管查询 Tools

- [x] 4.1 创建 app/tools/hr/manager_query.py — get_team_members tool
- [x] 4.2 manager_query.py — get_team_attendance tool
- [x] 4.3 manager_query.py — get_team_leave_requests tool
- [x] 4.4 manager_query.py — get_team_leave_balances tool
- [x] 4.5 manager_query.py — get_team_overtime_records tool
- [x] 4.6 manager_query.py — get_employee_profile tool

## 5. 主管审批 Tools

- [x] 5.1 创建 app/tools/hr/manager_action.py — approve_leave_request tool
- [x] 5.2 manager_action.py — approve_overtime_request tool

## 6. Tools 导出

- [x] 6.1 更新 app/tools/hr/__init__.py — 新增 manager_query_tools、manager_action_tools、manager_tools 导出

## 7. Agent 改造

- [x] 7.1 改造 app/agents/hr_agent.py — 新增主管 system prompt 片段
- [x] 7.2 改造 app/agents/hr_agent.py — 替换为 create_hr_agent 工厂函数，按 role 动态拼装 tools 和 instructions

## 8. 测试数据

- [x] 8.1 更新 scripts/generate_seed.py — 新增 performance_reviews 测试数据（20 人 × 多期考评）
- [x] 8.2 更新 scripts/generate_seed.py — 新增 employment_histories 测试数据（入职/转正/晋升/调岗记录）
