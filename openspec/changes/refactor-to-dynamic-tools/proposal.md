## Why

当前项目通过**提示词 + Tool 层运行时校验**控制权限：所有 tools 都注册到 Agent，LLM 可见全部 tools，用户调用越权工具时在 Tool 内部返回权限错误。这存在三个问题：
1. LLM 困惑于相似工具的选择（如 `get_team_members` vs `admin_get_all_employees`）
2. Function calling 传递全量 tools 浪费 token
3. 权限错误在运行时才发现，用户体验差

Agno 原生支持动态 tools（`tools` 参数传入工厂函数），可在运行时根据 `run_context.session_state` 动态返回用户有权限的 tools，实现更优雅的权限隔离。

## What Changes

- 各 Agent 的 `tools` 从静态列表改为**工厂函数**，根据用户 roles 动态返回可用 tools
- **移除 Tool 层权限校验逻辑**（`get_manager_info`、`get_admin_id`、`get_talent_dev_id` 等校验函数仅保留身份提取功能）
- **简化 Agent instructions**，移除权限说明部分（LLM 只能看到它有权限的 tools，无需再提示"主管可以..."）
- 涉及 5 个 Agent：HR、IT、Admin、Finance、Legal

## Capabilities

### New Capabilities
- `dynamic-tools`: 动态 tools 工厂函数机制，根据用户 roles 在运行时组装 tools 列表

### Modified Capabilities
- `hr-agent-impl`: Tools 改为动态加载，instructions 简化
- `finance-agent-impl`: Tools 改为动态加载，instructions 简化
- `legal-agent-impl`: Tools 改为动态加载，instructions 简化

## Impact

- **修改文件**：
  - `app/agents/hr_agent.py` - tools 改为工厂函数
  - `app/agents/it_agent.py` - tools 改为工厂函数
  - `app/agents/admin_agent.py` - tools 改为工厂函数
  - `app/agents/finance_agent.py` - tools 改为工厂函数
  - `app/agents/legal_agent.py` - tools 改为工厂函数
  - `app/tools/hr/utils.py` - 简化权限校验函数
- **无 API 变更**：对外接口不变
- **无数据模型变更**：仅内部实现调整
