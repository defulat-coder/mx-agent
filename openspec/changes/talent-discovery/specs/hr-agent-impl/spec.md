## MODIFIED Requirements

### Requirement: HR Agent 完整组装
HR Agent SHALL 组合 system prompt + query tools + action tools + skills + **discovery tools**，能处理员工所有 HR 相关问题，**包括人才发现分析**。

#### Scenario: 制度咨询
- **WHEN** 员工问"年假有多少天"
- **THEN** HR Agent 通过 hr-leave skill 获取假期制度，结合员工信息回答

#### Scenario: 数据查询
- **WHEN** 员工问"我这个月工资多少"
- **THEN** HR Agent 调用 get_salary_records tool 查询并回答

#### Scenario: 业务办理
- **WHEN** 员工说"我要请假"
- **THEN** HR Agent 收集必要信息（假期类型、起止日期、原因），调用 apply_leave tool 返回审批链接

#### Scenario: 人才发现分析
- **WHEN** talent_dev 角色用户问"帮我找出被埋没的高潜人才"
- **THEN** HR Agent 调用 td_discover_hidden_talent tool，结合 talent-discovery 知识库的评估框架，返回结构化分析

#### Scenario: 超出范围
- **WHEN** 员工问与 HR 无关的问题
- **THEN** HR Agent 礼貌告知该问题不在其服务范围

### Requirement: HR Agent Skills 加载
HR Agent SHALL 通过 agno Skills 加载 app/skills/hr/ 下所有 Skills。

#### Scenario: Skills 可用
- **WHEN** HR Agent 启动
- **THEN** 9 个 HR skills（attendance/leave/salary/social-insurance/onboarding/resignation/reimbursement/training/**talent-discovery**）全部可用

## ADDED Requirements

### Requirement: HR Agent Instructions 包含人才发现指引
HR Agent instructions SHALL 包含人才发现角色说明，引导 Agent 使用发现 Tool 进行分析。

#### Scenario: 人才发现指引内容
- **WHEN** HR Agent 初始化
- **THEN** instructions 包含：talent_dev 角色可使用 td_discover_hidden_talent / td_assess_flight_risk / td_promotion_readiness / td_find_candidates / td_talent_portrait / td_team_capability_gap 进行人才发现分析

#### Scenario: 工具选择引导
- **WHEN** talent_dev 用户描述分析需求
- **THEN** Agent 根据 instructions 选择最合适的发现 Tool（如"谁可能离职"→ td_assess_flight_risk，"这个人怎么样"→ td_talent_portrait）

### Requirement: HR Agent 加载发现工具
HR Agent SHALL 注册所有 discovery tools。

#### Scenario: 发现工具注册
- **WHEN** HR Agent 启动
- **THEN** 6 个发现 Tool（td_discover_hidden_talent / td_assess_flight_risk / td_promotion_readiness / td_find_candidates / td_talent_portrait / td_team_capability_gap）全部注册可用
