## MODIFIED Requirements

### Requirement: HR Agent 完整组装
HR Agent SHALL 组合 system prompt + query tools + action tools + manager tools + admin tools + talent_dev tools + skills，能处理员工、主管、管理者、人才发展所有 HR 相关问题。

#### Scenario: 制度咨询
- **WHEN** 员工问"年假有多少天"
- **THEN** HR Agent 通过 hr-leave skill 获取假期制度，结合员工信息回答

#### Scenario: 数据查询
- **WHEN** 员工问"我这个月工资多少"
- **THEN** HR Agent 调用 get_salary_records tool 查询并回答

#### Scenario: 业务办理
- **WHEN** 员工说"我要请假"
- **THEN** HR Agent 收集必要信息（假期类型、起止日期、原因），调用 apply_leave tool 返回审批链接

#### Scenario: 超出范围
- **WHEN** 员工问与 HR 无关的问题
- **THEN** HR Agent 礼貌告知该问题不在其服务范围

#### Scenario: 人才发展查询
- **WHEN** talent_dev 用户问"技术部的九宫格分布情况"
- **THEN** HR Agent 调用 td_nine_grid_distribution tool 查询并回答

#### Scenario: 人才发展报表
- **WHEN** talent_dev 用户问"各部门培训完成率"
- **THEN** HR Agent 调用 td_training_summary tool 查询并回答

### Requirement: HR Agent System Prompt
HR Agent SHALL 包含清晰的 system prompt，定义角色、能力边界和行为准则。prompt 中 SHALL 包含人才发展角色说明：当 roles 含 "talent_dev" 时，可查看全公司数据（含薪资社保绩效详情）、培训记录、人才盘点、IDP、以及 6 类分析报表。

#### Scenario: 角色定义
- **WHEN** HR Agent 初始化
- **THEN** system prompt 明确：你是马喜公司 HR 员工助手，支持员工/主管/管理者/人才发展四种角色
