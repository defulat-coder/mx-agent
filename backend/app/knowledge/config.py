"""RAG 知识库配置 — LanceDB 向量库 + 智谱 Embedding"""

from agno.knowledge.embedder.openai import OpenAIEmbedder
from agno.vectordb.lancedb import LanceDb
from agno.vectordb.search import SearchType

from app.config import settings


def get_vector_db() -> LanceDb:
    """创建 LanceDB 向量数据库实例"""
    return LanceDb(
        uri=settings.VECTOR_DB_DIR,
        table_name="company_docs",
        search_type=SearchType.vector,
        embedder=get_embedder(),
    )


def get_embedder() -> OpenAIEmbedder:
    """创建智谱 embedding-3 Embedder 实例"""
    return OpenAIEmbedder(
        id=settings.EMBEDDING_MODEL,
        api_key=settings.embedding_api_key,
        base_url=settings.embedding_base_url,
    )
