"""LLM judge 单元测试"""

import pytest
from unittest.mock import AsyncMock, patch

from app.evals.judge import _judge_clients, llm_judge


@pytest.fixture(autouse=True)
def clear_judge_client_cache():
    """每个测试前清理 judge 客户端缓存，确保 mock 生效。"""
    _judge_clients.clear()
    yield
    _judge_clients.clear()


@pytest.mark.asyncio
async def test_llm_judge_returns_score_on_valid_json():
    mock_response = AsyncMock()
    mock_response.choices = [
        type("Choice", (), {"message": type("Msg", (), {"content": '{"score": 0.9, "reason": "回答准确"}'})()})()
    ]
    with patch("app.evals.judge.AsyncOpenAI") as mock_cls:
        mock_cls.return_value.chat.completions.create = AsyncMock(return_value=mock_response)
        result = await llm_judge(
            user_input="查薪资",
            expected_behavior="调用薪资工具",
            response_text="已调用 get_salary_info 返回数据",
            model="glm-4",
            api_key="test-key",
            base_url="https://example.com",
        )
    assert result.score == pytest.approx(0.9)
    assert result.reason == "回答准确"


@pytest.mark.asyncio
async def test_llm_judge_handles_parse_error():
    mock_response = AsyncMock()
    mock_response.choices = [
        type("Choice", (), {"message": type("Msg", (), {"content": "不是JSON格式的输出"})()})()
    ]
    with patch("app.evals.judge.AsyncOpenAI") as mock_cls:
        mock_cls.return_value.chat.completions.create = AsyncMock(return_value=mock_response)
        result = await llm_judge(
            user_input="查薪资",
            expected_behavior="调用薪资工具",
            response_text="回答",
            model="glm-4",
            api_key="test-key",
            base_url="https://example.com",
        )
    assert result.score is None
    assert result.reason.startswith("parse_error:")
