"""LLM-as-a-judge — 使用 LLM 对 Agent 回答质量打分"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass

from openai import AsyncOpenAI

_JUDGE_PROMPT = """\
你是一个企业 AI 助手评测员。请根据以下信息给实际回答打分。

用户问题: {user_input}
预期行为: {expected_behavior}
实际回答: {response_text}

评分标准（综合以下维度）：
- 是否直接回答了用户问题
- 回答是否符合预期行为描述
- 回答是否准确完整，无明显错误

请只输出 JSON，不要其他内容：
{{"score": 0.85, "reason": "简要说明"}}

score 范围 0.0-1.0。\
"""


@dataclass(slots=True)
class JudgeResult:
    score: float | None
    reason: str


_judge_clients: dict[tuple[str, str], AsyncOpenAI] = {}


def _get_judge_client(api_key: str, base_url: str) -> AsyncOpenAI:
    key = (api_key, base_url)
    client = _judge_clients.get(key)
    if client is None:
        client = AsyncOpenAI(api_key=api_key, base_url=base_url)
        _judge_clients[key] = client
    return client


async def llm_judge(
    user_input: str,
    expected_behavior: str,
    response_text: str,
    model: str,
    api_key: str,
    base_url: str,
) -> JudgeResult:
    """使用 LLM 对 Agent 回答质量打分。

    Args:
        user_input: 用户原始输入
        expected_behavior: 用例中定义的预期行为
        response_text: Agent 实际回答文本
        model: LLM 模型名称
        api_key: LLM API Key
        base_url: LLM API Base URL

    Returns:
        JudgeResult，score=None 表示解析失败
    """
    client = _get_judge_client(api_key=api_key, base_url=base_url)
    prompt = _JUDGE_PROMPT.format(
        user_input=user_input,
        expected_behavior=expected_behavior,
        response_text=response_text[:2000],
    )
    try:
        response = await client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=256,
        )
        raw = response.choices[0].message.content or ""
        # 提取 JSON（容忍 LLM 在 JSON 前后输出少量文字）
        match = re.search(r"\{[^{}]+\}", raw, re.DOTALL)
        if not match:
            return JudgeResult(score=None, reason=f"parse_error: {raw[:200]}")
        data = json.loads(match.group())
        score = float(data["score"])
        score = max(0.0, min(1.0, score))
        return JudgeResult(score=score, reason=str(data.get("reason", "")))
    except (json.JSONDecodeError, KeyError, ValueError) as e:
        return JudgeResult(score=None, reason=f"parse_error: {e}")
    except Exception as e:
        return JudgeResult(score=None, reason=f"judge_error: {e}")
