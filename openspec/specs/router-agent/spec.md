## ADDED Requirements

### Requirement: 意图识别与路由分发
Router Agent SHALL 接收用户消息，识别意图，将请求分发到对应的子 Agent（HR/Finance/Legal）。

#### Scenario: HR 相关问题路由
- **WHEN** 用户消息涉及考勤、请假、薪资、社保、入离职、报销、培训等 HR 话题
- **THEN** Router Agent 将请求分发到 HR Agent 处理

#### Scenario: 财务相关问题路由
- **WHEN** 用户消息涉及财务相关问题（报销查询、预算管理、个税查询、费用汇总、应收应付等）
- **THEN** Router Agent 将请求分发到 Finance Assistant

#### Scenario: 法务相关问题路由
- **WHEN** 用户消息涉及法务相关问题（合同查询、合同模板、合同审查、法律咨询、合规问题等）
- **THEN** Router Agent 将请求分发到 Legal Assistant

### Requirement: 兜底回复
Router Agent SHALL 在无法识别意图时提供友好的兜底回复。

#### Scenario: 无法识别意图
- **WHEN** 用户消息不属于任何子 Agent 的服务范围
- **THEN** Router Agent 回复引导信息，告知用户当前支持的功能范围

### Requirement: 基于 agno Team 实现
Router Agent SHALL 基于 agno Team(mode="router") 实现，子 Agent 通过注册方式接入。

#### Scenario: 新 Agent 接入
- **WHEN** 开发者创建新的子 Agent 并注册到 Team
- **THEN** Router Agent 自动具备向该 Agent 分发请求的能力

### Requirement: 跨域失败聚合一致性
Router Agent SHALL 在跨域协作场景下对各子 Agent 的失败结果进行一致化聚合，确保用户获得明确状态与下一步动作。

#### Scenario: 单子域失败
- **WHEN** 跨域流程中某个子 Agent 返回权限不足或参数不足
- **THEN** Router Agent 在汇总结果中标注失败子域、失败原因，并给出可执行下一步建议

#### Scenario: 部分成功部分失败
- **WHEN** 跨域流程中至少一个子 Agent 成功、至少一个子 Agent 失败
- **THEN** Router Agent 先返回已完成事项，再列出未完成事项与处理建议，避免整体失败式回复
