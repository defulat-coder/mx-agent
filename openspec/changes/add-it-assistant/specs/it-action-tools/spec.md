## ADDED Requirements

### Requirement: 员工创建工单
系统 SHALL 提供 it_create_ticket Tool，员工创建 IT 服务工单。

#### Scenario: 创建报修工单
- **WHEN** Agent 调用 it_create_ticket(type="repair", title="笔记本无法开机", description="按电源键无反应", priority="high")
- **THEN** 创建工单（status=open, submitter_id=当前员工），返回工单编号

#### Scenario: 创建密码重置工单
- **WHEN** Agent 调用 it_create_ticket(type="password_reset", title="邮箱密码重置")
- **THEN** 创建工单，priority 默认 medium

#### Scenario: 工单编号自动生成
- **WHEN** 创建工单
- **THEN** 系统 MUST 自动生成唯一的 ticket_no（格式 IT-T-xxxx）

### Requirement: IT 管理员处理工单
系统 SHALL 提供 it_admin_handle_ticket Tool，IT 管理员受理/处理/关闭/转派工单。

#### Scenario: 受理工单
- **WHEN** IT 管理员调用 it_admin_handle_ticket(ticket_id=1, action="accept")
- **THEN** 工单 status 变为 "in_progress"，handler_id 设为当前管理员

#### Scenario: 解决工单
- **WHEN** IT 管理员调用 it_admin_handle_ticket(ticket_id=1, action="resolve", resolution="已更换电源适配器")
- **THEN** 工单 status 变为 "resolved"，记录 resolution 和 resolved_at

#### Scenario: 关闭工单
- **WHEN** IT 管理员调用 it_admin_handle_ticket(ticket_id=1, action="close")
- **THEN** 工单 status 变为 "closed"

#### Scenario: 权限校验
- **WHEN** 非 it_admin 角色调用 it_admin_handle_ticket
- **THEN** 返回权限不足提示

### Requirement: IT 管理员分配设备
系统 SHALL 提供 it_admin_assign_asset Tool，将空闲设备分配给员工。

#### Scenario: 分配设备
- **WHEN** IT 管理员调用 it_admin_assign_asset(asset_id=1, employee_id=5)
- **THEN** 设备 status 变为 "in_use"，employee_id 设为目标员工，同时写入 ITAssetHistory（action=assign）

#### Scenario: 设备非空闲
- **WHEN** 调用 it_admin_assign_asset 但设备 status 不是 "idle"
- **THEN** 返回错误提示"设备当前不可分配"

### Requirement: IT 管理员回收设备
系统 SHALL 提供 it_admin_reclaim_asset Tool，从员工回收设备。

#### Scenario: 回收设备
- **WHEN** IT 管理员调用 it_admin_reclaim_asset(asset_id=1)
- **THEN** 设备 status 变为 "idle"，employee_id 设为 null，写入 ITAssetHistory（action=reclaim）

#### Scenario: 设备未被使用
- **WHEN** 调用 it_admin_reclaim_asset 但设备 status 不是 "in_use"
- **THEN** 返回错误提示"设备当前未被使用"
