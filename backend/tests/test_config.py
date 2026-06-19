"""配置测试"""

from app.config import settings


def test_default_settings():
    assert settings.API_PREFIX == "/v1"
    assert settings.APP_NAME == "马喜智能助手"
    assert settings.LOG_LEVEL == "INFO"


def test_database_url_format():
    assert settings.DATABASE_URL.startswith("postgresql+asyncpg://")
