## 1. 依赖与配置

- [x] 1.1 `uv add lancedb` 安装 LanceDB 依赖
- [x] 1.2 `app/config.py` 新增 `EMBEDDING_MODEL`、`EMBEDDING_API_KEY`、`EMBEDDING_BASE_URL`、`KNOWLEDGE_DIR`、`VECTOR_DB_DIR` 配置项（含默认值和回退逻辑）

## 2. Knowledge 核心模块

- [x] 2.1 创建 `app/knowledge/__init__.py`，导出 `company_knowledge` 实例
- [x] 2.2 创建 `app/knowledge/config.py`，配置 LanceDB + OpenAIEmbedder（智谱 embedding-3）
- [x] 2.3 创建 `app/knowledge/loader.py`，实现 `load_knowledge()` 异步函数（从 KNOWLEDGE_DIR 扫描文档并加载到 Knowledge）

## 3. 模拟企业制度文档

- [x] 3.1 创建 `data/knowledge/docs/` 目录
- [x] 3.2 编写 `data/knowledge/docs/员工手册.md`（~200 行）
- [x] 3.3 编写 `data/knowledge/docs/财务管理制度.md`（~150 行）
- [x] 3.4 编写 `data/knowledge/docs/IT管理规范.md`（~150 行）
- [x] 3.5 编写 `data/knowledge/docs/行政管理制度.md`（~150 行）
- [x] 3.6 编写 `data/knowledge/docs/法务合规手册.md`（~150 行）

## 4. 集成到应用

- [x] 4.1 修改 `app/main.py` 的 `lifespan`，在 `init_db()` 后调用 `load_knowledge()`
- [x] 4.2 修改 `app/agents/router_agent.py`，Router Team 新增 `knowledge=company_knowledge` 和 `search_knowledge=True`
- [x] 4.3 Router Team instructions 新增知识库搜索说明

## 5. 工具脚本

- [x] 5.1 创建 `scripts/rebuild_knowledge.py`（全量重建向量库脚本）

## 6. 验证

- [x] 6.1 启动应用，验证知识库加载无报错
- [x] 6.2 通过对话测试知识库检索（如"公司组织架构是什么"应从员工手册检索到内容）
