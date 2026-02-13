## ADDED Requirements

### Requirement: 员工技能查询 Tool
系统 SHALL 提供 td_get_employee_skills Tool，查询指定员工的技能标签。

#### Scenario: 查询全部技能
- **WHEN** 调用 td_get_employee_skills(employee_id)
- **THEN** 返回该员工所有技能标签列表

#### Scenario: 按分类过滤
- **WHEN** 调用 td_get_employee_skills(employee_id, category="技术")
- **THEN** 仅返回技术类技能

#### Scenario: 权限校验
- **WHEN** 当前用户无 talent_dev 角色
- **THEN** 返回权限不足错误

### Requirement: 员工教育背景查询 Tool
系统 SHALL 提供 td_get_employee_education Tool，查询指定员工的教育背景。

#### Scenario: 查询教育背景
- **WHEN** 调用 td_get_employee_education(employee_id)
- **THEN** 返回该员工所有教育记录（学历、专业、院校、毕业年份）

#### Scenario: 权限校验
- **WHEN** 当前用户无 talent_dev 角色
- **THEN** 返回权限不足错误

### Requirement: 员工项目经历查询 Tool
系统 SHALL 提供 td_get_employee_projects Tool，查询指定员工的项目参与经历。

#### Scenario: 查询全部项目
- **WHEN** 调用 td_get_employee_projects(employee_id)
- **THEN** 返回该员工所有项目经历

#### Scenario: 按角色过滤
- **WHEN** 调用 td_get_employee_projects(employee_id, role="负责人")
- **THEN** 仅返回作为负责人参与的项目

#### Scenario: 权限校验
- **WHEN** 当前用户无 talent_dev 角色
- **THEN** 返回权限不足错误

### Requirement: 员工证书查询 Tool
系统 SHALL 提供 td_get_employee_certificates Tool，查询指定员工的证书认证。

#### Scenario: 查询全部证书
- **WHEN** 调用 td_get_employee_certificates(employee_id)
- **THEN** 返回该员工所有证书（名称、颁发机构、日期、有效期）

#### Scenario: 按分类过滤
- **WHEN** 调用 td_get_employee_certificates(employee_id, category="专业技术")
- **THEN** 仅返回专业技术类证书

#### Scenario: 权限校验
- **WHEN** 当前用户无 talent_dev 角色
- **THEN** 返回权限不足错误
