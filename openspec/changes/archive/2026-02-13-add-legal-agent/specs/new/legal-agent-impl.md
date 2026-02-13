# legal-agent-impl

法务 Agent 定义、Skills 知识库

## ADDED Requirements

### Requirement: 法务 Agent 定义

替换 `app/agents/legal_agent.py` 占位：
- id: "legal-assistant"
- name: "Legal Assistant"
- role: "马喜公司法务助手"
- model: get_model()
- skills: LocalSkills 加载 `app/skills/legal/` 下 3 个 skill
- tools: leg_employee_tools + leg_admin_tools
- instructions: 详细行为指引（含条款分析 disclaimer 要求）
- markdown: True

#### Scenario: Agent 加载
- **WHEN** 导入 legal_agent
- **THEN** Agent 包含 8 个工具和 3 个 Skills，可正常初始化

### Requirement: Skills 知识库

3 个目录，各含 SKILL.md + references/policy.md：
- `app/skills/legal/labor-law/`：劳动合同法、试用期、解雇保护、经济补偿
- `app/skills/legal/contract-knowledge/`：合同签订流程、竞业限制、保密协议、知识产权归属
- `app/skills/legal/compliance/`：企业合规要求、反腐败、数据隐私保护、审计配合

#### Scenario: Skills 加载
- **WHEN** Agent 初始化加载 Skills
- **THEN** 3 个 Skill 均成功加载，SKILL.md frontmatter 仅包含 allowed 字段

### Requirement: 工具导出

`app/tools/legal/__init__.py`：
- leg_employee_tools = [leg_get_templates, leg_get_template_download, leg_get_my_contracts]
- leg_admin_tools = [leg_admin_get_contracts, leg_admin_review_contract, leg_admin_get_expiring, leg_admin_analyze_contract, leg_admin_get_stats]

#### Scenario: 工具导入
- **WHEN** 执行 `from app.tools.legal import leg_employee_tools, leg_admin_tools`
- **THEN** 成功导入，leg_employee_tools 含 3 个函数，leg_admin_tools 含 5 个函数
