## MODIFIED Requirements

### Requirement: HR Agent tools 加载
HR Agent SHALL 加载全量 tools（employee_tools + manager_tools），不按角色过滤。

#### Scenario: 全量 tools 注册
- **WHEN** HR Agent 初始化
- **THEN** 包含所有员工 tools 和主管 tools

### Requirement: Tool 层权限校验
主管专用 Tools SHALL 通过 session_state.roles 校验权限，拒绝无权调用。

#### Scenario: 主管调用主管 Tool
- **WHEN** session_state.roles 包含 "manager" 的用户调用主管 Tool
- **THEN** Tool 正常执行

#### Scenario: 非主管调用主管 Tool
- **WHEN** session_state.roles 不包含 "manager" 的用户调用主管 Tool
- **THEN** Tool 返回 "该功能仅限部门主管使用"
