"""RAG 知识库模块 — 企业文档向量检索"""

from agno.knowledge import Knowledge

from app.knowledge.config import get_vector_db

company_knowledge = Knowledge(
    vector_db=get_vector_db(),
)
