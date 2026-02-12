## ADDED Requirements

### Requirement: 员工表
系统 SHALL 定义 employees 表，包含员工基本信息字段。

#### Scenario: 员工信息存储
- **WHEN** 查询 employees 表
- **THEN** 包含 id, name, employee_no(工号), department_id, position, level, hire_date, status(在职/离职/试用期), email, phone 字段

### Requirement: 部门表
系统 SHALL 定义 departments 表，支持树形层级结构。

#### Scenario: 部门层级
- **WHEN** 查询 departments 表
- **THEN** 包含 id, name, parent_id(上级部门), manager_id(部门负责人) 字段

### Requirement: 薪资记录表
系统 SHALL 定义 salary_records 表，存储月度薪资明细。

#### Scenario: 薪资明细字段
- **WHEN** 查询 salary_records 表
- **THEN** 包含 id, employee_id, year_month, base_salary, bonus, allowance, deduction, social_insurance, housing_fund, tax, net_salary 字段

### Requirement: 社保公积金记录表
系统 SHALL 定义 social_insurance_records 表，存储五险一金缴纳明细。

#### Scenario: 社保明细字段
- **WHEN** 查询 social_insurance_records 表
- **THEN** 包含 id, employee_id, year_month, pension, medical, unemployment, injury, maternity, housing_fund 及对应公司缴纳部分字段

### Requirement: 考勤记录表
系统 SHALL 定义 attendance_records 表，存储每日考勤打卡数据。

#### Scenario: 考勤记录字段
- **WHEN** 查询 attendance_records 表
- **THEN** 包含 id, employee_id, date, check_in, check_out, status(正常/迟到/早退/缺卡/外勤), remark 字段

### Requirement: 假期余额表
系统 SHALL 定义 leave_balances 表，存储员工各类假期余额。

#### Scenario: 假期余额字段
- **WHEN** 查询 leave_balances 表
- **THEN** 包含 id, employee_id, year, leave_type(年假/调休/病假/事假/婚假/产假等), total_days, used_days, remaining_days 字段

### Requirement: 请假记录表
系统 SHALL 定义 leave_requests 表，存储请假申请记录。

#### Scenario: 请假记录字段
- **WHEN** 查询 leave_requests 表
- **THEN** 包含 id, employee_id, leave_type, start_date, end_date, days, reason, status(待审批/已通过/已拒绝/已撤销), created_at 字段

### Requirement: 加班记录表
系统 SHALL 定义 overtime_records 表，存储加班申请与记录。

#### Scenario: 加班记录字段
- **WHEN** 查询 overtime_records 表
- **THEN** 包含 id, employee_id, date, start_time, end_time, hours, type(工作日/周末/节假日), status(待审批/已通过) 字段
