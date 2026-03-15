## ADDED Requirements

### Requirement: IT Agent 提示词基线
IT Agent instructions MUST 明确能力边界、角色-工具映射和失败处理规则，以保证工具选择稳定且可解释。

#### Scenario: 角色与工具映射
- **WHEN** IT Agent 初始化并处理用户请求
- **THEN** instructions 明确 `it_*` 为员工自助工具、`it_admin_*` 为 IT 管理员工具，仅在有权限时可用

#### Scenario: 权限失败处理
- **WHEN** IT Agent 调用工具返回权限不足
- **THEN** Agent 不重试同一受限工具，明确告知权限限制并提供可执行替代路径

### Requirement: IT Agent 自助优先策略
IT Agent MUST 在常见运维问题中优先使用 Skills 提供自助排查，再引导创建工单。

#### Scenario: 常见问题排查
- **WHEN** 员工询问 WiFi/VPN/打印机/邮箱等常见故障
- **THEN** Agent 先基于对应 Skill 给出排查步骤，确认无效后再建议创建工单
