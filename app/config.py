"""应用配置 — 从环境变量/.env 读取，包括 API、数据库、LLM、认证、日志等。"""

import os

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """应用全局配置，基于 pydantic-settings 从 .env 或环境变量加载。

    Attributes:
        API_PREFIX: API 路由前缀
        APP_NAME: 应用名称
        DEBUG: 是否开启调试模式
        DATABASE_URL: 异步 PostgreSQL 连接串
        LLM_MODEL: 大模型名称
        LLM_API_KEY: LLM API 密钥
        LLM_BASE_URL: LLM API 地址
        AUTH_SECRET: JWT 签名密钥
        LOG_LEVEL: 日志级别
        LOG_FILE: 日志文件路径，为空则仅输出到控制台
        LOG_ROTATION: 日志轮转大小
        LOG_RETENTION: 日志保留时长
    """

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # API
    API_PREFIX: str = "/v1"
    APP_NAME: str = "马喜智能助手"
    DEBUG: bool = False

    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///data/mx_agent.db"

    # LLM
    LLM_MODEL: str = "glm-4-plus"
    LLM_API_KEY: str = ""
    LLM_BASE_URL: str = "https://open.bigmodel.cn/api/paas/v4"

    # Embedding / Knowledge
    EMBEDDING_MODEL: str = "embedding-3"
    EMBEDDING_API_KEY: str = ""
    EMBEDDING_BASE_URL: str = ""
    KNOWLEDGE_DIR: str = "data/knowledge/docs"
    VECTOR_DB_DIR: str = "data/knowledge/lancedb"

    @property
    def embedding_api_key(self) -> str:
        """Embedding API Key，未设置则回退到 LLM_API_KEY"""
        return self.EMBEDDING_API_KEY or self.LLM_API_KEY

    @property
    def embedding_base_url(self) -> str:
        """Embedding Base URL，未设置则回退到 LLM_BASE_URL"""
        return self.EMBEDDING_BASE_URL or self.LLM_BASE_URL

    # Auth
    AUTH_SECRET: str = "dev-secret-change-me"

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str | None = None
    LOG_ROTATION: str = "500 MB"
    LOG_RETENTION: str = "10 days"


settings = Settings()

