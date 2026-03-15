## MODIFIED Requirements

### Requirement: 财务 Agent 定义
Finance Agent SHALL 使用 tools 工厂函数动态组装 tools：
- id: "finance-assistant"
- name: "Finance Assistant"
- role: "马喜公司财务助手"
- model: get_model()
- skills: LocalSkills 加载 `app/skills/finance/` 下 3 个 skill
- tools: `get_finance_tools` 工厂函数（根据 roles 返回 fin_employee_tools / fin_manager_tools / fin_admin_tools）
- instructions: 简化的行为指引（移除权限说明段落）
- markdown: True

#### Scenario: 普通员工请求
- **WHEN** 仅有 employee 角色的用户请求财务数据
- **THEN** LLM 仅能看到 fin_employee_tools（4 个工具）

#### Scenario: 财务管理员请求
- **WHEN** 具有 finance 角色的用户发起请求
- **THEN** LLM 能看到 fin_employee_tools + fin_admin_tools
