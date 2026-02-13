## ADDED Requirements

### Requirement: 递归获取管辖部门
系统 SHALL 提供递归查询方法，根据部门 ID 获取该部门及所有子部门的 ID 列表。

#### Scenario: 递归查询子部门
- **WHEN** 传入 department_id=2（技术部）
- **THEN** 返回 [2, 7, 8, 9, 10]（技术部 + 后端组/前端组/AI组/测试组）

#### Scenario: 叶子部门
- **WHEN** 传入 department_id=7（后端组，无子部门）
- **THEN** 返回 [7]

### Requirement: 查询团队成员列表
系统 SHALL 提供 get_team_members Tool，查询主管管辖范围内所有员工的基本信息。

#### Scenario: 查询团队成员
- **WHEN** 主管调用 get_team_members
- **THEN** 返回管辖部门（递归子部门）内所有员工的姓名、工号、部门、岗位、职级、状态

#### Scenario: 非主管调用
- **WHEN** role 为 employee 的用户调用 get_team_members
- **THEN** 返回错误提示"该功能仅限部门主管使用"

### Requirement: 查询团队考勤
系统 SHALL 提供 get_team_attendance Tool，查询团队成员的考勤记录。

#### Scenario: 查询团队考勤（指定员工）
- **WHEN** 主管调用 get_team_attendance(employee_id=2, start_date="2026-02-01", end_date="2026-02-11")
- **THEN** 返回该员工在日期范围内的考勤明细（前提：该员工在管辖范围内）

#### Scenario: 查询团队考勤（全员异常）
- **WHEN** 主管调用 get_team_attendance(status="异常") 不指定 employee_id
- **THEN** 返回管辖范围内所有异常考勤记录（迟到/早退/缺卡），默认当月

#### Scenario: 查询范围外员工
- **WHEN** 主管查询非管辖范围内的员工考勤
- **THEN** 返回错误提示"该员工不在您的管辖范围内"

### Requirement: 查询团队请假记录
系统 SHALL 提供 get_team_leave_requests Tool，查询团队成员的请假记录。

#### Scenario: 查询待审批请假
- **WHEN** 主管调用 get_team_leave_requests(status="待审批")
- **THEN** 返回管辖范围内所有待审批的请假申请（员工姓名、假期类型、起止日期、天数、原因）

#### Scenario: 查询全部请假记录
- **WHEN** 主管调用 get_team_leave_requests 不指定 status
- **THEN** 返回管辖范围内当年所有请假记录

### Requirement: 查询团队假期余额
系统 SHALL 提供 get_team_leave_balances Tool，查询团队成员的假期余额。

#### Scenario: 查询团队假期余额
- **WHEN** 主管调用 get_team_leave_balances
- **THEN** 返回管辖范围内所有员工的当年各类假期余额（姓名、假期类型、总天数、已用、剩余）

#### Scenario: 查询指定员工假期余额
- **WHEN** 主管调用 get_team_leave_balances(employee_id=2)
- **THEN** 返回该员工的当年各类假期余额（前提：该员工在管辖范围内）

### Requirement: 查询团队加班记录
系统 SHALL 提供 get_team_overtime_records Tool，查询团队成员的加班记录。

#### Scenario: 查询团队加班记录
- **WHEN** 主管调用 get_team_overtime_records(year_month="2026-02")
- **THEN** 返回管辖范围内所有员工该月的加班记录（员工姓名、日期、时段、时长、类型、状态）

#### Scenario: 查询待审批加班
- **WHEN** 主管调用 get_team_overtime_records(status="待审批")
- **THEN** 返回管辖范围内所有待审批的加班申请

### Requirement: 查询员工档案
系统 SHALL 提供 get_employee_profile Tool，主管可查看管辖范围内员工的完整档案。

#### Scenario: 查询员工完整档案
- **WHEN** 主管调用 get_employee_profile(employee_id=2)
- **THEN** 返回该员工的基本信息（姓名、工号、部门、岗位、职级、入职日期、状态）+ 绩效考评历史 + 在职履历，不包含薪资和社保

#### Scenario: 查询范围外员工档案
- **WHEN** 主管查询非管辖范围内的员工档案
- **THEN** 返回错误提示"该员工不在您的管辖范围内"

#### Scenario: 非主管调用
- **WHEN** role 为 employee 的用户调用 get_employee_profile
- **THEN** 返回错误提示"该功能仅限部门主管使用"
