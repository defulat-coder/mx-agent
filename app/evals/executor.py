from dataclasses import dataclass
from typing import Any, Callable, Iterable

from app.evals.runner import EvalCase


@dataclass(slots=True)
class HttpEvalResponse:
    status_code: int
    body: dict[str, Any]
    headers: dict[str, str]


@dataclass(slots=True)
class EvalResult:
    case_id: str
    ok: bool
    status_code: int | None
    tool_match: bool | None
    error: str | None
    fail_reason: str | None
    response_preview: str


def _extract_expected_tool_candidates(expected_tool: str) -> list[str]:
    if not expected_tool or expected_tool.strip() in {"—", "-"}:
        return []
    return [expected_tool.strip().lower()]


def _collect_response_text(response_json: dict[str, Any]) -> str:
    values: list[str] = []

    def walk(node: Any) -> None:
        if isinstance(node, str):
            values.append(node)
            return
        if isinstance(node, list):
            for item in node:
                walk(item)
            return
        if isinstance(node, dict):
            for key, value in node.items():
                if key in {"reply", "content", "message", "result", "response", "output", "text"}:
                    walk(value)
                elif key in {"member_responses", "messages", "choices", "delta"}:
                    walk(value)

    walk(response_json)
    return " ".join(values).strip()


def _collect_tool_names(response_json: dict[str, Any]) -> set[str]:
    """从响应体结构化字段收集完整工具名。

    ``"name"`` 仅在 ``"function"`` / ``"tool_call"`` 内部时才被采集。
    """
    names: set[str] = set()

    def walk(node: Any, *, inside_tool: bool = False) -> None:
        if isinstance(node, list):
            for item in node:
                walk(item, inside_tool=inside_tool)
            return
        if isinstance(node, dict):
            for key, value in node.items():
                if key in {"tool", "tool_name"}:
                    if isinstance(value, str):
                        names.add(value.strip().lower())
                    else:
                        walk(value, inside_tool=True)
                elif key in {"function", "tool_call", "tool_calls"}:
                    walk(value, inside_tool=True)
                elif key == "name" and inside_tool:
                    if isinstance(value, str):
                        names.add(value.strip().lower())
                elif key in {"member_responses", "messages", "choices", "delta"}:
                    walk(value, inside_tool=False)

    walk(response_json)
    return names


def _map_http_status_reason(status_code: int) -> str:
    if status_code == 401:
        return "http_401_unauthorized"
    if status_code == 403:
        return "http_403_forbidden"
    if status_code == 404:
        return "http_404_not_found"
    if status_code == 422:
        return "http_422_validation"
    if status_code == 429:
        return "http_429_rate_limited"
    if 500 <= status_code <= 599:
        return "http_5xx_upstream"
    return "http_status"


def _map_exception_reason(exc: Exception) -> str:
    message = str(exc).lower()
    if "timeout" in message:
        return "request_timeout"
    if "connect" in message or "connection" in message:
        return "request_connection_error"
    return "request_error"


def score_case(case: EvalCase, status_code: int, response_json: dict[str, Any]) -> EvalResult:
    response_text = _collect_response_text(response_json)
    candidates = _extract_expected_tool_candidates(case.expected_tool)
    observed_tools = _collect_tool_names(response_json)
    tool_match: bool | None = None
    if candidates:
        tool_match = any(c in observed_tools for c in candidates)
    ok = status_code == 200 and (tool_match is None or tool_match)
    fail_reason: str | None = None
    if not ok:
        if status_code != 200:
            fail_reason = _map_http_status_reason(status_code)
        elif tool_match is False:
            fail_reason = "tool_mismatch"
        else:
            fail_reason = "unknown"
    return EvalResult(
        case_id=case.case_id,
        ok=ok,
        status_code=status_code,
        tool_match=tool_match,
        error=None,
        fail_reason=fail_reason,
        response_preview=response_text[:160],
    )


def execute_cases(
    cases: Iterable[EvalCase],
    requester: Callable[[EvalCase], HttpEvalResponse],
) -> list[EvalResult]:
    results: list[EvalResult] = []
    for case in cases:
        try:
            eval_response = requester(case)
            results.append(score_case(case, eval_response.status_code, eval_response.body))
        except Exception as exc:
            results.append(
                EvalResult(
                    case_id=case.case_id,
                    ok=False,
                    status_code=None,
                    tool_match=None,
                    error=str(exc),
                    fail_reason=_map_exception_reason(exc),
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
        request_mode: str = "auto",
    ) -> None:
        import httpx

        headers: dict[str, str] = {}
        if auth_token:
            headers["Authorization"] = f"Bearer {auth_token}"
        self._client = httpx.AsyncClient(base_url=base_url, timeout=timeout, headers=headers)
        self.endpoint = endpoint
        self.message_field = message_field
        self.request_mode = request_mode

    def _resolved_mode(self) -> str:
        if self.request_mode in {"json", "form"}:
            return self.request_mode
        if "/runs" in self.endpoint and "/teams/" in self.endpoint:
            return "form"
        return "json"

    async def __call__(self, case: EvalCase) -> HttpEvalResponse:
        payload = {self.message_field: case.user_input}
        mode = self._resolved_mode()
        if mode == "form":
            payload["stream"] = "false"
            payload["monitor"] = "false"
            response = await self._client.post(self.endpoint, data=payload)
        else:
            response = await self._client.post(self.endpoint, json=payload)
        try:
            body = response.json()
        except Exception:
            body = {"message": response.text}
        return HttpEvalResponse(
            status_code=response.status_code,
            body=body,
            headers=dict(response.headers),
        )

    async def close(self) -> None:
        await self._client.aclose()
