## ADDED Requirements

### Requirement: 请假申请
系统 SHALL 提供 apply_leave Tool，收集请假信息后返回审批系统链接。

#### Scenario: 发起请假申请
- **WHEN** Agent 调用 apply_leave(leave_type="年假", start_date="2026-02-15", end_date="2026-02-16", reason="个人事务")
- **THEN** 返回包含审批系统链接的 action 对象，链接中预填 employee_id 及请假参数

#### Scenario: 参数不完整
- **WHEN** Agent 调用 apply_leave 但缺少必要参数（如 leave_type 或 start_date）
- **THEN** 返回提示信息，告知缺少哪些必要信息

### Requirement: 加班登记
系统 SHALL 提供 apply_overtime Tool，收集加班信息后返回审批系统链接。

#### Scenario: 发起加班登记
- **WHEN** Agent 调用 apply_overtime(date="2026-02-15", start_time="19:00", end_time="22:00", type="工作日")
- **THEN** 返回包含审批系统链接的 action 对象

### Requirement: 报销申请
系统 SHALL 提供 apply_reimbursement Tool，收集报销信息后返回报销系统链接。

#### Scenario: 发起报销申请
- **WHEN** Agent 调用 apply_reimbursement(type="差旅", amount=1500, description="北京出差交通费")
- **THEN** 返回包含报销系统链接的 action 对象

### Requirement: Action 响应格式
所有 Action Tool SHALL 返回统一格式的 action 对象。

#### Scenario: 响应格式
- **WHEN** 任何 Action Tool 成功执行
- **THEN** 返回 `{"type": "redirect", "url": "<审批系统链接>", "message": "<引导文案>"}`
