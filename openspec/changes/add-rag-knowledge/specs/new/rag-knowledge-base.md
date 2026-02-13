## ADDED Requirements

### Requirement: 向量数据库配置
系统 SHALL 使用 LanceDB 作为本地向量数据库，数据存储在 `data/knowledge/lancedb/` 目录。

#### Scenario: LanceDB 初始化
- **WHEN** 应用首次启动
- **THEN** 系统在 `VECTOR_DB_DIR` 路径创建 LanceDB 实例，table_name 为 `company_docs`

#### Scenario: 向量库目录不存在
- **WHEN** `VECTOR_DB_DIR` 目录不存在
- **THEN** 系统自动创建该目录

### Requirement: Embedding 模型配置
系统 SHALL 使用智谱 embedding-3 模型，通过 Agno `OpenAIEmbedder` 调用。

#### Scenario: Embedder 初始化
- **WHEN** Knowledge 实例创建时
- **THEN** 使用 `OpenAIEmbedder(id=EMBEDDING_MODEL, api_key=EMBEDDING_API_KEY, base_url=EMBEDDING_BASE_URL)` 配置 Embedder

#### Scenario: 默认复用 LLM 配置
- **WHEN** 未设置 `EMBEDDING_API_KEY` 或 `EMBEDDING_BASE_URL`
- **THEN** 分别使用 `LLM_API_KEY` 和 `LLM_BASE_URL` 作为默认值

### Requirement: Knowledge 实例
系统 SHALL 创建全局 `company_knowledge` 实例供 Router Team 使用。

#### Scenario: Knowledge 创建
- **WHEN** `app/knowledge/__init__.py` 被导入
- **THEN** 创建 `Knowledge(vector_db=LanceDb(...), num_documents=5)` 实例

### Requirement: 文档加载
系统 SHALL 从 `KNOWLEDGE_DIR` 目录加载 PDF 和 Markdown 文档到向量库。

#### Scenario: 首次加载
- **WHEN** 应用启动且向量库为空
- **THEN** 系统读取 `KNOWLEDGE_DIR` 下所有 `.pdf` 和 `.md` 文件，切片后写入向量库

#### Scenario: 增量加载
- **WHEN** 应用启动且向量库已有数据
- **THEN** 系统调用 `knowledge.aload(recreate=False)`，仅新增文档不重建已有数据

#### Scenario: 文档目录为空
- **WHEN** `KNOWLEDGE_DIR` 目录无文件
- **THEN** 系统正常启动，Knowledge 可用但无检索结果

### Requirement: 全量重建脚本
系统 SHALL 提供 `scripts/rebuild_knowledge.py` 脚本用于全量重建向量库。

#### Scenario: 执行重建
- **WHEN** 运行 `uv run python scripts/rebuild_knowledge.py`
- **THEN** 清空向量库并重新导入 `KNOWLEDGE_DIR` 下所有文档

### Requirement: 配置项
系统 SHALL 在 `app/config.py` 中新增 RAG 相关配置项。

#### Scenario: 配置加载
- **WHEN** 应用启动
- **THEN** 从环境变量读取以下配置（均有默认值）：`EMBEDDING_MODEL`（默认 `embedding-3`）、`EMBEDDING_API_KEY`（默认空，复用 LLM_API_KEY）、`EMBEDDING_BASE_URL`（默认空，复用 LLM_BASE_URL）、`KNOWLEDGE_DIR`（默认 `data/knowledge/docs`）、`VECTOR_DB_DIR`（默认 `data/knowledge/lancedb`）
