## ADDED Requirements

### Requirement: Agent 占位骨架
系统 SHALL 为 HR、Finance、Legal 三个子 Agent 创建占位文件，每个 Agent 有明确的职责描述。

#### Scenario: HR Agent 占位
- **WHEN** 查看 `app/agents/hr_agent.py`
- **THEN** 存在 HR Agent 定义，description 描述了其职责范围（考勤、假期、薪酬、社保、入离职、报销、培训）

#### Scenario: Finance Agent 占位
- **WHEN** 查看 `app/agents/finance_agent.py`
- **THEN** 存在 Finance Agent 定义，当前回复"财务助手功能开发中"

#### Scenario: Legal Agent 占位
- **WHEN** 查看 `app/agents/legal_agent.py`
- **THEN** 存在 Legal Agent 定义，当前回复"法务助手功能开发中"

### Requirement: Skills 加载机制
HR Agent SHALL 通过 agno Skills 机制加载 `app/skills/hr/` 下的所有 Skills。

#### Scenario: Skills 按需加载
- **WHEN** HR Agent 收到制度咨询类问题
- **THEN** Agent 通过 Skills 工具按需加载对应制度内容（如 hr-attendance、hr-leave 等）

### Requirement: Agent 模型配置
每个 Agent 使用的 LLM 模型 SHALL 通过配置文件指定，支持灵活切换。

#### Scenario: 模型配置
- **WHEN** 需要切换 Agent 使用的 LLM
- **THEN** 修改 `.env` 中的模型配置即可，无需改代码
