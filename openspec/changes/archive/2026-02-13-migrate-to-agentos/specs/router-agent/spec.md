## MODIFIED Requirements

### Requirement: 路由智能体
系统 SHALL 使用静态 router_team 实例注册到 AgentOS，包含 HR/财务/法务子 Agent。

#### Scenario: 请求路由
- **WHEN** 用户通过 `/teams/router-team/runs` 发送消息
- **THEN** router_team 将请求分发到合适的子 Agent
