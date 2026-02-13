# admin-agent-impl

行政 Agent 定义、Skills 知识库、挂载到 Router Team

## Requirements

### REQ-ADM-AGENT-1: 行政 Agent 定义

文件 `app/agents/admin_agent.py`：
- id: "admin-assistant"
- name: "Admin Assistant"
- role: "马喜公司行政助手"
- model: get_model()
- skills: LocalSkills 加载 `app/skills/admin/` 下 3 个 skill
- tools: `adm_employee_tools` + `adm_admin_tools`
- instructions: 详细的行为指引
- markdown: True

### REQ-ADM-AGENT-2: Skills 知识库

3 个目录，各含 SKILL.md + references/policy.md：
- `app/skills/admin/travel-policy/` — 差旅标准
- `app/skills/admin/office-rules/` — 办公规范
- `app/skills/admin/meeting-room-rules/` — 会议室使用规范

### REQ-ADM-AGENT-3: Router Team 集成

`app/agents/router_agent.py` members 追加 `admin_agent`。
instructions 增加：行政相关问题（会议室、办公用品、快递、访客、差旅等）→ Admin Assistant。

### REQ-ADM-AGENT-4: 工具导出

`app/tools/admin/__init__.py`：
- `adm_employee_tools` = 查询 4 + 操作 5 = 9 个
- `adm_admin_tools` = 查询 6 + 操作 3 = 9 个

## Scenarios

- Agent instructions 描述每个工具的用途和参数
- 差旅问题先查阅 travel-policy skill
- 会议室规则问题先查阅 meeting-room-rules skill
