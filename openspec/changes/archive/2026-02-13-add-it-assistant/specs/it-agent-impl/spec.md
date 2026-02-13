## ADDED Requirements

### Requirement: IT Agent 定义
系统 SHALL 在 `app/agents/it_agent.py` 定义 IT 运维助手 Agent。

Agent 配置：
- id: "it-assistant"
- name: "IT Assistant"
- role: "马喜公司 IT 运维助手"
- model: get_model()
- skills: LocalSkills 加载 `app/skills/it/`
- tools: employee_tools + admin_tools（按角色分组）
- instructions: 包含能力说明、角色权限、工具对应关系、行为准则

#### Scenario: Agent 创建
- **WHEN** 应用启动加载 it_agent
- **THEN** Agent 实例化成功，包含 12 个 Tools 和 5 个 Skills

### Requirement: IT Agent 提示词
IT Agent instructions SHALL 包含以下内容：
1. 员工自助能力：工单查询、设备查询、创建工单、IT 制度咨询（Skills）
2. IT 管理员权限：全部工单管理、设备分配回收、统计报表
3. 工具与角色对应关系（it_* 前缀 → 员工，it_admin_* 前缀 → IT 管理员）
4. 行为准则：不编造数据、权限错误不重试、超出范围引导用户

#### Scenario: 员工咨询 WiFi 问题
- **WHEN** 员工询问 "WiFi 连不上怎么办"
- **THEN** Agent 使用 wifi-vpn Skill 返回排查指南

#### Scenario: 员工创建报修工单
- **WHEN** 员工说 "我的电脑屏幕闪烁"
- **THEN** Agent 收集信息后调用 it_create_ticket 创建报修工单

### Requirement: Skills 知识库
系统 SHALL 在 `app/skills/it/` 下提供 5 个 IT 知识库。

| 目录 | 描述 |
|------|------|
| wifi-vpn/ | WiFi/VPN 连接排查指南 |
| printer/ | 打印机安装和故障排查 |
| email/ | 邮箱配置（Outlook/手机端） |
| security/ | 信息安全制度和密码策略 |
| device-policy/ | 设备使用规范、借用归还流程 |

每个目录 MUST 包含 SKILL.md（元数据 + 使用说明）和 references/policy.md（制度内容）。

#### Scenario: Skill 加载
- **WHEN** IT Agent 初始化时加载 Skills
- **THEN** 5 个 Skill 全部成功加载

#### Scenario: 制度咨询
- **WHEN** 员工询问 "设备借用需要什么流程"
- **THEN** Agent 通过 device-policy Skill 返回设备借用流程说明
