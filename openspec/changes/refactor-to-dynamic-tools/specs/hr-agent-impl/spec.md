## MODIFIED Requirements

### Requirement: HR Agent 完整组装
HR Agent SHALL 使用 tools 工厂函数动态组装 tools，根据用户 roles 返回对应权限的工具集。

#### Scenario: 制度咨询
- **WHEN** 员工问"年假有多少天"
- **THEN** HR Agent 通过 hr-leave skill 获取假期制度，结合员工信息回答

#### Scenario: 数据查询
- **WHEN** 员工问"我这个月工资多少"
- **THEN** HR Agent 调用 get_salary_records tool 查询并回答

#### Scenario: 业务办理
- **WHEN** 员工说"我要请假"
- **THEN** HR Agent 收集必要信息（假期类型、起止日期、原因），调用 apply_leave tool 返回审批链接

#### Scenario: 主管查询团队
- **WHEN** 具有 manager 角色的用户问"我团队的考勤情况"
- **THEN** HR Agent 可调用 get_team_attendance tool（因为动态 tools 已包含 manager_tools）

#### Scenario: 普通员工无主管工具
- **WHEN** 仅有 employee 角色的用户发起请求
- **THEN** LLM function calling 列表中不包含 get_team_* 系列工具

### Requirement: HR Agent System Prompt
HR Agent SHALL 包含简化的 system prompt，移除权限说明段落，仅保留角色定义和行为准则。

#### Scenario: 简化后的指令
- **WHEN** HR Agent 初始化
- **THEN** system prompt 不包含"## 部门主管权限"、"## 管理者权限"等段落
