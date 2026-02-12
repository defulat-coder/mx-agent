## ADDED Requirements

### Requirement: 绩效考评表
系统 SHALL 定义 performance_reviews 表，存储员工半年度绩效考评记录。

#### Scenario: 绩效考评字段
- **WHEN** 查询 performance_reviews 表
- **THEN** 包含 id, employee_id, year, half(上半年/下半年), rating(A/B+/B/C/D), score(百分制), reviewer(考评人姓名), comment(考评评语), created_at 字段

#### Scenario: 绩效数据关联
- **WHEN** 通过 employee_id 查询绩效
- **THEN** 返回该员工的所有历史绩效记录，按 year + half 倒序

### Requirement: 在职履历表
系统 SHALL 定义 employment_histories 表，存储员工在职期间的岗位变动记录。

#### Scenario: 在职履历字段
- **WHEN** 查询 employment_histories 表
- **THEN** 包含 id, employee_id, start_date, end_date(可为空表示当前), department(部门名称), position(岗位), level(职级), change_type(入职/转正/晋升/调岗/降级), remark 字段

#### Scenario: 履历数据关联
- **WHEN** 通过 employee_id 查询履历
- **THEN** 返回该员工从入职至今的所有岗位变动记录，按 start_date 倒序
