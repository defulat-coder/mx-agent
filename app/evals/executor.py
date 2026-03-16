from dataclasses import dataclass
from typing import Any, Callable, Iterable
import re

from app.evals.runner import EvalCase


@dataclass(slots=True)
class EvalResult:
    case_id: str
    ok: bool
    status_code: int | None
    tool_match: bool | None
    error: str | None
    response_preview: str


def _extract_expected_tool_candidates(expected_tool: str) -> list[str]:
    if not expected_tool or expected_tool.strip() in {"—", "-"}:
        return []
    return [token.lower() for token in re.findall(r"[a-zA-Z_]{3,}", expected_tool)]


def _collect_response_text(response_json: dict[str, Any]) -> str:
    values: list[str] = []
    for key in ("reply", "content", "message", "result", "response"):
        value = response_json.get(key)
        if isinstance(value, str):
            values.append(value)
    return " ".join(values).strip()


def score_case(case: EvalCase, status_code: int, response_json: dict[str, Any]) -> EvalResult:
    response_text = _collect_response_text(response_json)
    candidates = _extract_expected_tool_candidates(case.expected_tool)
    tool_match: bool | None = None
    if candidates:
        lower_text = response_text.lower()
        tool_match = any(candidate in lower_text for candidate in candidates)
    ok = status_code == 200 and (tool_match is None or tool_match)
    return EvalResult(
        case_id=case.case_id,
        ok=ok,
        status_code=status_code,
        tool_match=tool_match,
        error=None,
        response_preview=response_text[:160],
    )


def execute_cases(
    cases: Iterable[EvalCase],
    requester: Callable[[EvalCase], tuple[int, dict[str, Any]]],
) -> list[EvalResult]:
    results: list[EvalResult] = []
    for case in cases:
        try:
            status_code, response_json = requester(case)
            results.append(score_case(case, status_code, response_json))
        except Exception as exc:
            results.append(
                EvalResult(
                    case_id=case.case_id,
                    ok=False,
                    status_code=None,
                    tool_match=None,
                    error=str(exc),
                    response_preview="",
                )
            )
    return results


class HttpEvalRequester:
    def __init__(
        self,
        base_url: str,
        endpoint: str,
        timeout: float = 30.0,
        auth_token: str = "",
        message_field: str = "message",
    ) -> None:
        import httpx

        headers: dict[str, str] = {}
        if auth_token:
            headers["Authorization"] = f"Bearer {auth_token}"
        self._client = httpx.Client(base_url=base_url, timeout=timeout, headers=headers)
        self.endpoint = endpoint
        self.message_field = message_field

    def __call__(self, case: EvalCase) -> tuple[int, dict[str, Any]]:
        payload = {self.message_field: case.user_input}
        response = self._client.post(self.endpoint, json=payload)
        try:
            response_json = response.json()
        except Exception:
            response_json = {"message": response.text}
        return response.status_code, response_json

    def close(self) -> None:
        self._client.close()
