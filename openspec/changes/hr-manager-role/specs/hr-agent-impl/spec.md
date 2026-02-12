## MODIFIED Requirements

### Requirement: HR Agent 完整组装
HR Agent SHALL 通过工厂函数 `create_hr_agent` 按角色组装不同的 tools 列表。员工角色加载员工 tools，主管角色额外加载主管 tools。

#### Scenario: 员工角色初始化
- **WHEN** role="employee" 时创建 HR Agent
- **THEN** Agent 加载员工查询 tools（7 个） + 员工办理 tools（3 个） + skills

#### Scenario: 主管角色初始化
- **WHEN** role="manager" 时创建 HR Agent
- **THEN** Agent 加载员工 tools（10 个） + 主管查询 tools（6 个，含员工档案） + 主管审批 tools（2 个） + skills

### Requirement: HR Agent System Prompt
HR Agent SHALL 根据角色生成不同的 system prompt，主管角色额外包含团队管理和审批行为准则。

#### Scenario: 员工 System Prompt
- **WHEN** role="employee"
- **THEN** system prompt 定义：你是马喜公司 HR 员工助手，只服务于当前登录员工

#### Scenario: 主管 System Prompt
- **WHEN** role="manager"
- **THEN** system prompt 额外包含：你同时具备部门主管权限，可查看团队数据和审批下属申请；不可查看下属薪资和社保；审批前应先查看待审批列表确认信息
