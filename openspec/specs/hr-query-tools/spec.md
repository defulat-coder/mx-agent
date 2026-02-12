## ADDED Requirements

### Requirement: 个人信息查询
系统 SHALL 提供 get_employee_info Tool，查询当前员工的基本信息。

#### Scenario: 查询个人信息
- **WHEN** Agent 调用 get_employee_info
- **THEN** 返回当前 employee_id 对应的姓名、工号、部门、岗位、职级、入职日期、状态

### Requirement: 薪资明细查询
系统 SHALL 提供 get_salary_records Tool，查询当前员工的薪资明细。

#### Scenario: 查询指定月份薪资
- **WHEN** Agent 调用 get_salary_records(year_month="2026-01")
- **THEN** 返回该月的薪资各项明细（基本工资、奖金、补贴、扣款、社保、公积金、个税、实发）

#### Scenario: 查询最近薪资
- **WHEN** Agent 调用 get_salary_records 不传 year_month
- **THEN** 返回最近 3 个月的薪资记录

#### Scenario: 数据隔离
- **WHEN** Agent 调用 get_salary_records
- **THEN** 只返回 run_context.employee_id 对应的数据，不可查询他人薪资

### Requirement: 社保公积金查询
系统 SHALL 提供 get_social_insurance Tool，查询当前员工的社保公积金缴纳明细。

#### Scenario: 查询社保明细
- **WHEN** Agent 调用 get_social_insurance(year_month="2026-01")
- **THEN** 返回该月五险一金个人缴纳和公司缴纳明细

#### Scenario: 查询最近缴纳记录
- **WHEN** Agent 调用 get_social_insurance 不传 year_month
- **THEN** 返回最近 1 个月的缴纳记录

### Requirement: 考勤记录查询
系统 SHALL 提供 get_attendance Tool，查询当前员工的考勤记录。

#### Scenario: 查询指定日期范围考勤
- **WHEN** Agent 调用 get_attendance(start_date="2026-02-01", end_date="2026-02-11")
- **THEN** 返回该日期范围内每天的打卡记录和考勤状态

#### Scenario: 查询当月考勤
- **WHEN** Agent 调用 get_attendance 不传日期参数
- **THEN** 返回当月至今的考勤记录

### Requirement: 假期余额查询
系统 SHALL 提供 get_leave_balance Tool，查询当前员工的各类假期余额。

#### Scenario: 查询当年假期余额
- **WHEN** Agent 调用 get_leave_balance
- **THEN** 返回当前年度各类假期的总天数、已用天数、剩余天数

### Requirement: 请假记录查询
系统 SHALL 提供 get_leave_requests Tool，查询当前员工的请假申请记录。

#### Scenario: 查询请假记录
- **WHEN** Agent 调用 get_leave_requests(year=2026)
- **THEN** 返回该年度所有请假记录（类型、起止日期、天数、状态）

### Requirement: 加班记录查询
系统 SHALL 提供 get_overtime_records Tool，查询当前员工的加班记录。

#### Scenario: 查询加班记录
- **WHEN** Agent 调用 get_overtime_records(year_month="2026-02")
- **THEN** 返回该月所有加班记录（日期、时段、时长、类型、状态）
