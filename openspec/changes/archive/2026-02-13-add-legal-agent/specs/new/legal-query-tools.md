# legal-query-tools

员工 + 法务人员查询工具

## ADDED Requirements

### Requirement: leg_get_templates

员工查询合同模板列表。参数：type（可选，按类型筛选）。

#### Scenario: 查询全部模板
- **WHEN** 员工调用 leg_get_templates 不传 type
- **THEN** 返回全部合同模板列表

#### Scenario: 按类型筛选
- **WHEN** 员工调用 leg_get_templates 传 type="劳动合同"
- **THEN** 返回该类型的模板列表

### Requirement: leg_get_template_download

员工获取模板下载链接。参数：template_id。返回模板信息 + file_url（OA 下载链接）。

#### Scenario: 获取下载链接
- **WHEN** 员工调用 leg_get_template_download 传有效 template_id
- **THEN** 返回模板名称、类型、描述和 file_url

### Requirement: leg_get_my_contracts

员工查询自己提交的合同审批进度。参数：status（可选）。通过 get_employee_id 获取身份。

#### Scenario: 查询自己的合同
- **WHEN** 员工调用 leg_get_my_contracts
- **THEN** 返回 submitted_by = 当前员工的合同列表（含审批状态）

### Requirement: leg_admin_get_contracts

法务人员查询全公司合同台账。参数：type, status, department_id（均可选）。需 legal 角色。

#### Scenario: 全量查询
- **WHEN** 法务人员调用 leg_admin_get_contracts 不传参数
- **THEN** 返回全部合同列表

#### Scenario: 多条件筛选
- **WHEN** 法务人员传 status="pending" + type="采购合同"
- **THEN** 返回符合条件的合同列表

### Requirement: leg_admin_get_expiring

法务人员查询即将到期的合同（默认 30 天内到期）。参数：days（可选，默认 30）。需 legal 角色。

#### Scenario: 默认 30 天预警
- **WHEN** 法务人员调用 leg_admin_get_expiring 不传 days
- **THEN** 返回 end_date 在今天至 30 天后之间、status 为 approved 的合同

### Requirement: leg_admin_get_stats

法务人员查询合同统计报表。需 legal 角色。

返回：合同总数、各状态分布、各类型分布、总金额、即将到期数。

#### Scenario: 统计报表
- **WHEN** 法务人员调用 leg_admin_get_stats
- **THEN** 返回合同数量/金额/类型/状态的汇总统计
