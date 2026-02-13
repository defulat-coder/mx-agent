## Why

现有知识体系仅靠手写 Markdown Skills（22 个，~1300 行），无法覆盖企业几百页的制度文档（员工手册、财务制度、IT 规范等）。员工提问超出 Skills 覆盖范围时，Agent 只能回答"不清楚"。需要通过 RAG（向量检索增强生成）接入企业文档，扩展知识覆盖面。

## What Changes

- 新增 RAG 知识库模块，使用 LanceDB（本地向量库）+ 智谱 embedding-3 模型
- 在 Router Team 级别挂载共享 Knowledge，所有子 Agent 自动获得文档检索能力
- 新增知识库初始化脚本，支持从 `data/knowledge/docs/` 目录批量导入 PDF/Markdown 文档
- 新增配置项（embedding 模型、向量库路径、文档目录）
- 生成 5 份模拟企业制度 PDF 作为测试文档
- 与现有 Skills 共存：Skills 处理精确规则知识，RAG 覆盖长尾文档内容

## Capabilities

### New Capabilities
- `rag-knowledge-base`: RAG 知识库核心模块（LanceDB 向量库配置、Embedding 配置、Knowledge 实例创建、文档导入脚本）
- `mock-enterprise-docs`: 模拟企业制度文档生成（员工手册、财务管理制度、IT 管理规范、行政管理制度、法务合规手册）

### Modified Capabilities
- `router-agent`: Router Team 新增 `knowledge` 参数挂载共享知识库，`search_knowledge=True`
- `database`: `init_db` 中新增知识库初始化逻辑（首次启动自动导入文档）

## Impact

- 新增依赖：`lancedb`
- 新增目录：`app/knowledge/`、`data/knowledge/docs/`、`data/knowledge/lancedb/`
- 修改文件：`app/agents/router_agent.py`、`app/config.py`、`app/main.py`
- 新增配置项：`EMBEDDING_MODEL`、`EMBEDDING_API_KEY`、`EMBEDDING_BASE_URL`、`KNOWLEDGE_DIR`、`VECTOR_DB_DIR`
