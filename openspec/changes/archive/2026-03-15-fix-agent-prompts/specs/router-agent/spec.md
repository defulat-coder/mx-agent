## ADDED Requirements

### Requirement: 跨域失败聚合一致性
Router Agent SHALL 在跨域协作场景下对各子 Agent 的失败结果进行一致化聚合，确保用户获得明确状态与下一步动作。

#### Scenario: 单子域失败
- **WHEN** 跨域流程中某个子 Agent 返回权限不足或参数不足
- **THEN** Router Agent 在汇总结果中标注失败子域、失败原因，并给出可执行下一步建议

#### Scenario: 部分成功部分失败
- **WHEN** 跨域流程中至少一个子 Agent 成功、至少一个子 Agent 失败
- **THEN** Router Agent 先返回已完成事项，再列出未完成事项与处理建议，避免整体失败式回复
