## MODIFIED Requirements

### Requirement: 意图识别与路由分发
Router Agent SHALL 接收用户消息，识别意图，将请求分发到对应的子 Agent（HR/Finance/Legal/IT）。

#### Scenario: HR 相关问题路由
- **WHEN** 用户消息涉及考勤、请假、薪资、社保、入离职、报销、培训等 HR 话题
- **THEN** Router Agent 将请求分发到 HR Agent 处理

#### Scenario: IT 运维相关问题路由
- **WHEN** 用户消息涉及设备报修、密码重置、权限申请、软件安装、设备查询、WiFi/VPN/打印机问题等 IT 话题
- **THEN** Router Agent 将请求分发到 IT Agent 处理

#### Scenario: 财务相关问题路由
- **WHEN** 用户消息涉及财务相关话题
- **THEN** Router Agent 将请求分发到 Finance Agent（Phase 2，当前返回"功能开发中"）

#### Scenario: 法务相关问题路由
- **WHEN** 用户消息涉及法务相关话题
- **THEN** Router Agent 将请求分发到 Legal Agent（Phase 3，当前返回"功能开发中"）
