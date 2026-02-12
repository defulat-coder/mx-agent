## ADDED Requirements

### Requirement: 审批请假申请
系统 SHALL 提供 approve_leave_request Tool，主管可通过或拒绝下属的请假申请。

#### Scenario: 通过请假申请
- **WHEN** 主管调用 approve_leave_request(request_id=1, action="通过", comment="同意")
- **THEN** 将 leave_requests.status 从"待审批"更新为"已通过"，返回审批结果

#### Scenario: 拒绝请假申请
- **WHEN** 主管调用 approve_leave_request(request_id=1, action="拒绝", comment="该时段人手不足")
- **THEN** 将 leave_requests.status 从"待审批"更新为"已拒绝"，返回审批结果

#### Scenario: 审批非待审批状态的申请
- **WHEN** 主管对已通过/已拒绝/已撤销的请假申请调用审批
- **THEN** 返回错误提示"该申请当前状态为 XX，无法审批"

#### Scenario: 审批非管辖范围的申请
- **WHEN** 主管审批不属于其管辖范围内员工的请假申请
- **THEN** 返回错误提示"该员工不在您的管辖范围内，无权审批"

### Requirement: 审批加班申请
系统 SHALL 提供 approve_overtime_request Tool，主管可通过或拒绝下属的加班申请。

#### Scenario: 通过加班申请
- **WHEN** 主管调用 approve_overtime_request(record_id=1, action="通过", comment="")
- **THEN** 将 overtime_records.status 从"待审批"更新为"已通过"，返回审批结果

#### Scenario: 拒绝加班申请
- **WHEN** 主管调用 approve_overtime_request(record_id=1, action="拒绝", comment="无需加班")
- **THEN** 将 overtime_records.status 从"待审批"更新为"已拒绝"，返回审批结果

#### Scenario: 审批非待审批状态的加班记录
- **WHEN** 主管对非"待审批"状态的加班记录调用审批
- **THEN** 返回错误提示"该记录当前状态为 XX，无法审批"

### Requirement: 审批响应格式
所有审批 Tool SHALL 返回统一格式的审批结果。

#### Scenario: 审批成功响应
- **WHEN** 审批操作成功执行
- **THEN** 返回 `{"success": true, "request_id": <id>, "action": "通过|拒绝", "message": "<结果描述>"}`

#### Scenario: 审批失败响应
- **WHEN** 审批操作因权限或状态问题失败
- **THEN** 返回 `{"success": false, "message": "<错误原因>"}`
