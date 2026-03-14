## Context

马喜智能助手基于 Agno AgentOS 运行时，包含一个 Router Team 和五个子 Agent（HR/IT/Admin/Finance/Legal）。当前 AgentOS 已开启 `tracing=True`，但追踪数据仅输出到控制台，缺乏持久化和分析能力。

项目已安装 `openinference-instrumentation-agno` 和 OpenTelemetry 相关依赖，为集成 Langfuse 奠定了基础。用户已在 `.env` 中配置了 Langfuse 的认证信息。

## Goals / Non-Goals

**Goals:**
- 自动追踪所有 Agent 调用链（Router Team → 子 Agent）
- 记录 Tool 调用的输入输出和延迟
- 记录 LLM 请求的 token 消耗、延迟和成本
- 支持用户级追踪（关联 employee_id）
- 失败时优雅降级，不阻断应用启动

**Non-Goals:**
- 不实现自定义的追踪 UI 或存储
- 不修改 Agno 或 AgentOS 的源码
- 不追踪业务数据库查询（SQLAlchemy）
- 不实现实时告警或通知

## Decisions

### 1. 使用 OpenTelemetry OTLP 协议而非 Langfuse Python SDK

**决策**: 通过 OpenTelemetry OTLP exporter 将追踪数据发送到 Langfuse，而非直接使用 `langfuse` SDK。

**理由**:
- Agno 原生支持 OpenTelemetry，`OpenInferenceInstrumentor` 可直接启用
- Langfuse 原生支持 OTLP 接收，无需额外适配层
- 保持与 Agno 生态的一致性，未来可轻松切换其他 OTLP 后端

**替代方案**: 使用 `langfuse` SDK 手动创建追踪，需要更多代码且与 Agno 集成不够原生。

### 2. 在 lifespan 中初始化 tracing

**决策**: 在 `app/main.py` 的 `lifespan` 函数中初始化 tracing 系统。

**理由**:
- 与现有初始化逻辑（日志、数据库、知识库）保持一致
- 确保在 AgentOS 启动前完成 tracer 配置
- 支持异步初始化

### 3. 失败时警告而非阻断

**决策**: 如果 Langfuse 连接失败，记录警告日志但允许应用继续启动。

**理由**:
- 避免外部服务故障导致应用不可用
- 符合"优雅降级"原则
- 便于本地开发（可能无 Langfuse 服务）

### 4. 复用现有 .env 配置

**决策**: 直接使用用户已配置的 `LANGFUSE_SECRET_KEY`、`LANGFUSE_PUBLIC_KEY`、`LANGFUSE_BASE_URL`。

**理由**:
- 用户已完成配置，无需变更
- 保持与 Langfuse 官方文档的命名一致

## Risks / Trade-offs

| Risk | Mitigation |
|------|------------|
| 追踪数据包含敏感查询内容 | 确保 Langfuse Cloud/自建实例的访问控制；未来可考虑敏感字段脱敏 |
| Langfuse 服务不可用导致启动延迟 | 设置 OTLP exporter 的超时时间；失败时快速降级 |
| 大量请求产生高额追踪成本 | Langfuse Cloud 有免费额度；可配置采样率（未来优化） |
| OpenTelemetry 依赖版本冲突 | 使用与 Agno 兼容的版本；在 requirements 中明确版本约束 |

## Migration Plan

1. **添加依赖**: `uv add langfuse` 或更新 `pyproject.toml`
2. **配置更新**: 确认 `.env` 中 Langfuse 配置正确
3. **代码变更**: 按 tasks.md 实现 tracing 模块和初始化逻辑
4. **验证**: 启动应用，发送测试请求，检查 Langfuse 控制台是否收到追踪数据
5. **回滚**: 如遇到问题，移除 `app/core/tracing.py` 引用，应用恢复正常运行

## Open Questions

（无，方案已明确）
