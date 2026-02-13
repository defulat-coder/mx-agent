## ADDED Requirements

### Requirement: IT 设备资产模型
系统 SHALL 提供 ITAsset ORM 模型，存储 IT 设备资产信息。

字段：
- `asset_no`: String(32), 唯一索引, 格式 `IT-A-xxxx`, comment="资产编号"
- `type`: String(32), comment="设备类型"（laptop/desktop/monitor/peripheral/other）
- `brand`: String(64), comment="品牌"
- `model_name`: String(128), comment="型号"
- `status`: String(16), comment="资产状态"（idle/in_use/maintenance/scrapped）
- `employee_id`: FK → employees.id, nullable, comment="当前使用人ID"
- `purchase_date`: Date, nullable, comment="采购日期"
- `warranty_expire`: Date, nullable, comment="保修到期日"

#### Scenario: 空闲设备
- **WHEN** 设备未分配给任何员工
- **THEN** status 为 "idle"，employee_id 为 null

#### Scenario: 在用设备
- **WHEN** 设备已分配给员工
- **THEN** status 为 "in_use"，employee_id 指向使用人

#### Scenario: 资产编号唯一
- **WHEN** 插入重复 asset_no
- **THEN** 数据库 SHALL 拒绝并抛出唯一约束异常

### Requirement: IT 工单模型
系统 SHALL 提供 ITTicket ORM 模型，存储 IT 服务工单。

字段：
- `ticket_no`: String(32), 唯一索引, 格式 `IT-T-xxxx`, comment="工单编号"
- `type`: String(32), comment="工单类型"（repair/password_reset/software_install/permission/other）
- `title`: String(256), comment="工单标题"
- `description`: Text, default="", comment="问题描述"
- `status`: String(16), comment="工单状态"（open/in_progress/resolved/closed）
- `priority`: String(16), default="medium", comment="优先级"（low/medium/high/urgent）
- `submitter_id`: FK → employees.id, comment="提交人ID"
- `handler_id`: FK → employees.id, nullable, comment="处理人ID"
- `resolution`: Text, default="", comment="处理结果"
- `resolved_at`: DateTime, nullable, comment="解决时间"

#### Scenario: 新建工单
- **WHEN** 员工创建工单
- **THEN** status 为 "open"，handler_id 为 null，resolved_at 为 null

#### Scenario: 工单已解决
- **WHEN** IT 管理员解决工单
- **THEN** status 为 "resolved"，resolved_at 记录解决时间，resolution 记录处理结果

### Requirement: IT 设备流转记录模型
系统 SHALL 提供 ITAssetHistory ORM 模型，记录设备分配/回收/调拨历史。

字段：
- `asset_id`: FK → it_assets.id, comment="设备ID"
- `action`: String(16), comment="操作类型"（assign/reclaim/transfer）
- `from_employee_id`: FK → employees.id, nullable, comment="原使用人ID"
- `to_employee_id`: FK → employees.id, nullable, comment="新使用人ID"
- `operated_by`: FK → employees.id, comment="操作人ID"
- `remark`: String(256), default="", comment="备注"

#### Scenario: 设备分配
- **WHEN** 从库存分配设备给员工
- **THEN** action 为 "assign"，from_employee_id 为 null，to_employee_id 为接收人

#### Scenario: 设备回收
- **WHEN** 从员工回收设备
- **THEN** action 为 "reclaim"，from_employee_id 为原使用人，to_employee_id 为 null

#### Scenario: 设备调拨
- **WHEN** 设备从 A 员工转给 B 员工
- **THEN** action 为 "transfer"，from_employee_id 为 A，to_employee_id 为 B

### Requirement: IT Schema 定义
系统 SHALL 提供 Pydantic Schema 用于 Tool 返回值序列化。

包含：
- `ITAssetResponse`: 设备信息响应
- `ITTicketResponse`: 工单信息响应
- `ITTicketCreateRequest`: 创建工单请求（type, title, description, priority）
- `ITTicketStatsResponse`: 工单统计响应
- `ITAssetStatsResponse`: 设备统计响应

#### Scenario: Schema 字段描述
- **WHEN** 定义 Schema 字段
- **THEN** 每个字段 MUST 使用 Field(description="中文说明")

### Requirement: Mock 数据种子
系统 SHALL 提供 `scripts/seed_it_data.py` 脚本生成约 100 条 IT 测试数据。

分布：
- ITAsset ~30 条：覆盖 laptop/desktop/monitor/peripheral 各类型，idle/in_use/maintenance/scrapped 各状态
- ITTicket ~60 条：覆盖所有 type 和 status 组合，priority 各级别，时间跨度近 3 个月
- ITAssetHistory ~15 条：分配和回收记录

#### Scenario: 数据引用一致性
- **WHEN** 种子脚本生成 Mock 数据
- **THEN** employee_id 和 department_id MUST 引用 employees 表中已存在的记录
