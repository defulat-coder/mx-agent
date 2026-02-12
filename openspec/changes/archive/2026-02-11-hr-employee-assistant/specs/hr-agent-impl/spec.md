## ADDED Requirements

### Requirement: HR Agent 完整组装
HR Agent SHALL 组合 system prompt + query tools + action tools + skills，能处理员工所有 HR 相关问题。

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

### Requirement: HR Agent System Prompt
HR Agent SHALL 包含清晰的 system prompt，定义角色、能力边界和行为准则。

#### Scenario: 角色定义
- **WHEN** HR Agent 初始化
- **THEN** system prompt 明确：你是马喜公司 HR 员工助手，只服务于当前登录员工，只回答 HR 相关问题

### Requirement: HR Agent Skills 加载
HR Agent SHALL 通过 agno Skills 加载 app/skills/hr/ 下所有 Skills。

#### Scenario: Skills 可用
- **WHEN** HR Agent 启动
- **THEN** 8 个 HR skills（attendance/leave/salary/social-insurance/onboarding/resignation/reimbursement/training）全部可用
