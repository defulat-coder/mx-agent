# database

MODIFIED — lifespan 新增知识库初始化

## Changes

### CHG-DB-RAG-1: 知识库加载

`app/main.py` 的 `lifespan` 函数中，在 `init_db()` 之后新增 `await load_knowledge()` 调用，启动时自动加载文档到向量库。
