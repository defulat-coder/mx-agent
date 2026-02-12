"""LLM 模型工厂 — 统一创建 OpenAI 兼容模型实例"""

from agno.models.openai.like import OpenAILike

from app.config import settings


def get_model() -> OpenAILike:
    """创建 LLM 模型实例，基于 settings 中的配置。

    Returns:
        OpenAILike 模型实例
    """
    return OpenAILike(
        id=settings.LLM_MODEL,
        api_key=settings.LLM_API_KEY,
        base_url=settings.LLM_BASE_URL,
    )
