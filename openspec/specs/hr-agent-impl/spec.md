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
HR Agent SHALL 包含清晰的 system prompt，定义角色、能力边界和行为准则；当用户具备 `talent_dev` 角色时，提示词 MUST 提供 discovery tools 的场景化选择指引。

#### Scenario: 角色定义
- **WHEN** HR Agent 初始化
- **THEN** system prompt 明确：你是马喜公司 HR 员工助手，只服务于当前登录员工，只回答 HR 相关问题

#### Scenario: 人才发现工具选择指引
- **WHEN** `roles` 包含 `talent_dev` 且用户提出人才分析诉求
- **THEN** instructions 明确按意图选择对应 discovery tool（如离职风险→`td_assess_flight_risk`，晋升准备度→`td_promotion_readiness`，人岗匹配候选→`td_find_candidates`，个体画像→`td_talent_portrait`）

#### Scenario: 人才分析输出要求
- **WHEN** HR Agent 使用 discovery tool 返回数据
- **THEN** Agent 按“结论-依据-建议”结构输出，避免仅返回原始数据

### Requirement: HR Agent Skills 加载
HR Agent SHALL 通过 agno Skills 加载 app/skills/hr/ 下所有 Skills。

#### Scenario: Skills 可用
- **WHEN** HR Agent 启动
- **THEN** 8 个 HR skills（attendance/leave/salary/social-insurance/onboarding/resignation/reimbursement/training）全部可用
