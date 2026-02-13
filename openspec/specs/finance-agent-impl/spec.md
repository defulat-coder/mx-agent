# finance-agent-impl

财务 Agent 定义、Skills 知识库

## Requirements

### REQ-FIN-AGENT-1: 财务 Agent 定义

替换 `app/agents/finance_agent.py` 占位：
- id: "finance-assistant"
- name: "Finance Assistant"
- role: "马喜公司财务助手"
- model: get_model()
- skills: LocalSkills 加载 `app/skills/finance/` 下 3 个 skill
- tools: fin_employee_tools + fin_manager_tools + fin_admin_tools
- instructions: 详细行为指引
- markdown: True

### REQ-FIN-AGENT-2: Skills 知识库

3 个目录，各含 SKILL.md + references/policy.md：
- `app/skills/finance/reimbursement-policy/`
- `app/skills/finance/budget-rules/`
- `app/skills/finance/tax-knowledge/`

### REQ-FIN-AGENT-3: 工具导出

`app/tools/finance/__init__.py`：
- fin_employee_tools = 4 个
- fin_manager_tools = 3 个
- fin_admin_tools = 7 个

## Scenarios

- 报销政策问题先查阅 reimbursement-policy skill
- 个税问题先查阅 tax-knowledge skill
- Agent instructions 描述每个工具的用途
