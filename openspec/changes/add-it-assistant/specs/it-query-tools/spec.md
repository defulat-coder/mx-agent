## ADDED Requirements

### Requirement: 员工工单列表查询
系统 SHALL 提供 it_get_my_tickets Tool，查询当前员工提交的 IT 工单列表。

#### Scenario: 查询自己的工单
- **WHEN** Agent 调用 it_get_my_tickets
- **THEN** 返回当前 employee_id 作为 submitter_id 的所有工单（ticket_no, type, title, status, priority, created_at）

#### Scenario: 按状态筛选
- **WHEN** Agent 调用 it_get_my_tickets(status="open")
- **THEN** 仅返回状态为 open 的工单

#### Scenario: 数据隔离
- **WHEN** Agent 调用 it_get_my_tickets
- **THEN** 只返回 submitter_id = 当前 employee_id 的工单，不可查看他人工单

### Requirement: 工单详情查询
系统 SHALL 提供 it_get_ticket_detail Tool，查询单个工单的完整信息。

#### Scenario: 查询自己的工单详情
- **WHEN** Agent 调用 it_get_ticket_detail(ticket_id=123)
- **THEN** 返回该工单的全部字段（含 description, resolution, handler 信息）

#### Scenario: 查询他人工单
- **WHEN** 普通员工调用 it_get_ticket_detail 查询非自己提交的工单
- **THEN** 返回权限不足提示

### Requirement: 员工设备查询
系统 SHALL 提供 it_get_my_assets Tool，查询当前员工名下的 IT 设备。

#### Scenario: 查询我的设备
- **WHEN** Agent 调用 it_get_my_assets
- **THEN** 返回 employee_id = 当前用户 的所有在用设备（asset_no, type, brand, model_name, purchase_date, warranty_expire）

#### Scenario: 无设备
- **WHEN** 当前员工名下无设备
- **THEN** 返回空列表

### Requirement: IT 管理员工单列表查询
系统 SHALL 提供 it_admin_get_tickets Tool，IT 管理员查询全部工单。

#### Scenario: 查询全部工单
- **WHEN** IT 管理员调用 it_admin_get_tickets
- **THEN** 返回所有工单列表

#### Scenario: 多条件筛选
- **WHEN** IT 管理员调用 it_admin_get_tickets(status="open", type="repair", priority="high")
- **THEN** 仅返回符合所有筛选条件的工单

#### Scenario: 权限校验
- **WHEN** 非 it_admin 角色调用 it_admin_get_tickets
- **THEN** 返回权限不足提示

### Requirement: IT 管理员设备查询
系统 SHALL 提供 it_admin_get_assets Tool，IT 管理员查询全部设备资产。

#### Scenario: 查询全部设备
- **WHEN** IT 管理员调用 it_admin_get_assets
- **THEN** 返回所有设备列表

#### Scenario: 按状态筛选
- **WHEN** IT 管理员调用 it_admin_get_assets(status="idle")
- **THEN** 仅返回空闲设备

#### Scenario: 按类型筛选
- **WHEN** IT 管理员调用 it_admin_get_assets(type="laptop")
- **THEN** 仅返回笔记本电脑

### Requirement: 工单统计报表
系统 SHALL 提供 it_admin_ticket_stats Tool，统计工单数据。

#### Scenario: 工单统计
- **WHEN** IT 管理员调用 it_admin_ticket_stats
- **THEN** 返回各状态工单数量、各类型工单数量、各优先级工单数量、平均处理时长

### Requirement: 设备统计报表
系统 SHALL 提供 it_admin_asset_stats Tool，统计设备资产数据。

#### Scenario: 设备统计
- **WHEN** IT 管理员调用 it_admin_asset_stats
- **THEN** 返回各状态设备数量、各类型设备数量、各部门设备分配数量

### Requirement: 故障趋势分析
系统 SHALL 提供 it_admin_fault_trend Tool，分析故障趋势。

#### Scenario: 故障趋势
- **WHEN** IT 管理员调用 it_admin_fault_trend(months=3)
- **THEN** 返回近 N 个月每月各类型工单数量趋势、高频故障部门 TOP5
