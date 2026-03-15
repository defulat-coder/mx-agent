## Context

当前系统已完成多 Agent 架构与动态 tools 工厂函数，但提示词内容与能力边界未完全同步，表现为：
- HR Agent 已挂载 discovery tools，但 instructions 未提供 talent_dev 场景下的工具选择策略。
- IT Agent 已按角色动态暴露工具，但 instructions 未明确 `it_*` / `it_admin_*` 映射与权限失败处理语义。
- Router Team 在跨域协作中缺少统一失败处理约束，导致子助手返回失败时聚合口径不稳定。

本次变更仅聚焦提示词与行为规范，不调整数据库、API、工具实现。

## Goals / Non-Goals

**Goals:**
- 对齐 HR Agent 提示词与 talent_dev 发现类能力。
- 建立 IT Agent 的角色-工具映射与权限失败处理基线。
- 为 Router Team 增加跨域失败聚合的统一规则。
- 形成可验收的 specs 与 tasks，为后续实现提供直接执行依据。

**Non-Goals:**
- 不新增或重命名现有 Tool。
- 不修改 Tool 层权限校验逻辑与数据模型。
- 不变更外部 API 契约与前端交互协议。

## Decisions

### Decision 1: 通过 OpenSpec delta specs 驱动提示词修复
- 决策：以 `hr-agent-impl`、`router-agent` 的 delta spec 及新增 `it-agent-impl` spec 明确行为要求，再由实现阶段修改 `app/agents/*.py`。
- 原因：当前问题本质是“行为契约不完整”，先补齐规范可避免后续改动偏离需求。
- 备选方案：直接改代码后补文档。未采用，因为容易出现“实现先行、验收口径缺失”。

### Decision 2: HR 采用“场景到工具”的显式映射表达
- 决策：在 HR requirement 中新增 talent_dev 常见分析意图与 `td_*` discovery tools 对应关系。
- 原因：可直接降低 function calling 选择歧义，提升输出稳定性。
- 备选方案：仅要求“按需选择 discovery tools”。未采用，因为可操作性和可测试性不足。

### Decision 3: IT 与 Router 统一失败处理语义
- 决策：在 IT 要求中规定“权限失败不重试、解释原因并给出替代动作”；在 Router 要求中规定“跨域聚合时标注失败域与下一步建议”。
- 原因：统一失败语义可减少多 Agent 回答风格分叉。
- 备选方案：仅在 Router 层兜底。未采用，因为单点兜底无法约束子 Agent 的首轮行为。

## Risks / Trade-offs

- [Risk] 规范变严格后，回复更保守，可能减少“猜测性帮助” → Mitigation：在 requirements 中明确“可给出下一步可执行建议”。
- [Risk] 仅改提示词，无法覆盖工具内部异常细节 → Mitigation：保持 Tool 层校验与错误码作为防御纵深。
- [Risk] 新增 capability `it-agent-impl` 与历史归档 spec 命名存在差异 → Mitigation：以当前主规格目录为准，后续归档时统一。

## Migration Plan

1. 合并本次 change 的 proposal/design/specs/tasks。
2. 在实现阶段按任务更新 `app/agents/hr_agent.py`、`app/agents/it_agent.py`、`app/agents/router_agent.py` 的 instructions。
3. 执行回归验证：单域问答、跨域协作、权限不足、参数不足、工具异常场景。
4. 通过验证后进入 verify/archive 流程。

## Open Questions

- 是否需要为所有子 Agent 统一一套“失败处理短语模板”，避免语气差异过大。
- Router 在跨域场景下是否应固定输出步骤编号格式（如“步骤 1/2/3”）以提升可读性。
