## MODIFIED Requirements

### Requirement: 法务 Agent 定义
Legal Agent SHALL 使用 tools 工厂函数动态组装 tools：
- id: "legal-assistant"
- name: "Legal Assistant"
- role: "马喜公司法务助手"
- model: get_model()
- skills: LocalSkills 加载 `app/skills/legal/` 下 3 个 skill
- tools: `get_legal_tools` 工厂函数（根据 roles 返回 leg_employee_tools / leg_admin_tools）
- instructions: 简化的行为指引（移除权限说明段落，保留条款分析 disclaimer 要求）
- markdown: True

#### Scenario: 普通员工请求
- **WHEN** 仅有 employee 角色的用户请求法务服务
- **THEN** LLM 仅能看到 leg_employee_tools（3 个工具：模板查询、模板下载、我的合同）

#### Scenario: 法务管理员请求
- **WHEN** 具有 legal 角色的用户发起请求
- **THEN** LLM 能看到 leg_employee_tools + leg_admin_tools（共 8 个工具）
