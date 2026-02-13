## Context

项目当前使用 Agno LocalSkills 提供精确知识（22 个手写 Markdown），覆盖核心制度规则。但企业实际有大量文档（员工手册、财务制度等）无法全部手写。Agno 原生支持 Knowledge Base（向量检索），可与 Skills 共存。

项目技术栈：FastAPI + Agno + SQLite（轻量本地），LLM 为智谱 GLM-4（OpenAI 兼容 API）。

## Goals / Non-Goals

**Goals:**
- 在 Router Team 级别挂载共享 Knowledge Base，所有子 Agent 获得文档检索能力
- 使用 LanceDB（本地文件向量库）+ 智谱 embedding-3，零外部服务依赖
- 提供文档导入脚本，支持 PDF / Markdown 批量导入
- 生成 5 份模拟企业制度文档用于测试
- 应用启动时自动检测并加载新文档
- 与现有 Skills 共存，互不干扰

**Non-Goals:**
- 不做文档管理 UI（后续可通过 AgentOS 自带 UI 管理）
- 不做实时文档更新（需手动重启或调用脚本重建索引）
- 不做文档权限控制（所有文档对所有用户可见，敏感文档不入库）
- 不做 hybrid search（先用纯向量搜索，后续按需加关键词搜索）

## Decisions

### D1: 向量数据库 — LanceDB

**选择**: LanceDB（本地文件存储）

**替代方案**:
- PgVector：需要 PostgreSQL，运维成本高
- ChromaDB：需额外进程，且 API 稳定性不如 LanceDB

**理由**: 与项目 SQLite 轻量路线一致，纯文件存储，`data/knowledge/lancedb/` 目录即数据库，零运维。

### D2: Embedding 模型 — 智谱 embedding-3

**选择**: 智谱 `embedding-3`，通过 Agno `OpenAIEmbedder` + 自定义 `base_url` 调用

**理由**: 复用现有智谱 API 账号，无需额外开通服务。OpenAIEmbedder 支持自定义 `api_key` 和 `base_url`。

**配置**:
```python
OpenAIEmbedder(
    id="embedding-3",
    api_key=settings.EMBEDDING_API_KEY,  # 默认复用 LLM_API_KEY
    base_url=settings.EMBEDDING_BASE_URL,  # 默认复用 LLM_BASE_URL
)
```

### D3: Knowledge 挂载层级 — Team 共享

**选择**: 挂在 `router_team` 上，`search_knowledge=True`

**替代方案**: 每个 Agent 独立知识库

**理由**: Router 已做意图路由，不需要在知识库层再分域。Team 共享一个库，管理最简单。Agno Team 的 `search_knowledge=True` 让 Team Leader 在需要时自动搜索。

### D4: 模块结构

```
app/knowledge/
├── __init__.py          # 导出 company_knowledge 实例
├── config.py            # LanceDB + Embedder 配置
└── loader.py            # 文档加载/重建索引逻辑

data/knowledge/
├── docs/                # 企业文档存放目录（PDF/MD）
└── lancedb/             # LanceDB 数据文件（自动生成）
```

### D5: 文档加载策略

- 应用启动时（lifespan）调用 `knowledge.aload(recreate=False)`
- `recreate=False` 表示只新增，不重建已有文档
- 提供独立脚本 `scripts/rebuild_knowledge.py` 用于全量重建
- 文档通过 Agno 内置 Reader 自动解析（PDF → `PDFReader`，MD → 直接读取）

### D6: 模拟文档

生成 5 份 Markdown 文件（模拟企业制度），放入 `data/knowledge/docs/`：

| 文档 | 内容 | 约页数 |
|------|------|--------|
| 员工手册.md | 公司简介/组织架构/行为规范/奖惩制度/员工福利 | ~5 页 |
| 财务管理制度.md | 预算管理/费用报销/资产管理/审计监督 | ~4 页 |
| IT管理规范.md | 信息安全/设备管理/网络使用/数据备份/应急响应 | ~4 页 |
| 行政管理制度.md | 办公管理/会议管理/车辆管理/档案管理 | ~4 页 |
| 法务合规手册.md | 合同管理/知识产权/反腐败/数据隐私/争议解决 | ~4 页 |

用 Markdown 而非 PDF，简化生成流程，Agno Knowledge 同样支持。

## Risks / Trade-offs

- **[首次启动慢]** → 首次 embedding 计算需要时间（5 份文档约 30 秒），后续启动跳过已有数据
- **[Embedding 成本]** → 智谱 embedding-3 按 token 计费，5 份模拟文档成本可忽略；真实部署时大量文档需评估成本
- **[检索质量]** → 纯向量搜索可能不如混合搜索精确，但对制度文档类场景够用
- **[LanceDB 并发]** → LanceDB 单写多读，高并发写入场景需注意；当前场景只在启动时写入，运行时只读，无问题
