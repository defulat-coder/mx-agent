## Why

当前多 Agent 的 instructions 与已实现能力和既有需求存在偏差：HR 缺少 talent_dev 发现类工具的使用指引，IT 缺少角色-工具映射与权限失败处理规则。这些偏差会导致工具选择不稳定、结果不一致，影响可预期性与可维护性。

## What Changes

- 补齐 HR Agent 的人才发现提示词，明确 talent_dev 场景下 discovery tools 的选择策略与输出期望。
- 补齐 IT Agent 的提示词约束，明确 `it_*` 与 `it_admin_*` 的职责边界、权限失败不重试策略。
- 统一跨 Agent 的失败处理语义（权限失败、参数不足、工具异常）以提升回复一致性。
- 将上述要求沉淀到 OpenSpec delta specs，作为后续实现与验收依据。

## Capabilities

### New Capabilities
- `it-agent-impl`: 定义 IT Agent 的提示词基线，包含角色-工具映射与权限失败处理规则。

### Modified Capabilities
- `hr-agent-impl`: 扩展 HR Agent requirements，补充 talent_dev discovery 工具选择与分析输出指引。
- `router-agent`: 明确 Router/子 Agent 交互中的失败处理一致性约束，避免跨域协作时行为分叉。

## Impact

- Affected code:
  - `app/agents/hr_agent.py`
  - `app/agents/it_agent.py`
  - `app/agents/router_agent.py`
- Affected specs:
  - `openspec/specs/hr-agent-impl/spec.md`（modified）
  - `openspec/specs/router-agent/spec.md`（modified）
  - `openspec/specs/it-agent-impl/spec.md`（new）
- API 与数据模型无变更，仅提示词与行为规范变更。
