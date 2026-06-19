from collections import Counter
from dataclasses import dataclass, field
from functools import lru_cache
from typing import Any, Callable, Iterable

from app.evals.runner import EvalCase, _parse_tool_expectation

_TEXT_KEYS = {"reply", "content", "message", "result", "response", "output", "text"}
_RECURSE_KEYS = {"member_responses", "messages", "choices", "delta"}
_AGENT_ALIASES = {
    "hr assistant": "hr-assistant",
    "hr-assistant": "hr-assistant",
    "hr": "hr-assistant",
    "it assistant": "it-assistant",
    "it-assistant": "it-assistant",
    "it": "it-assistant",
    "admin assistant": "admin-assistant",
    "admin-assistant": "admin-assistant",
    "admin": "admin-assistant",
    "finance assistant": "finance-assistant",
    "finance-assistant": "finance-assistant",
    "finance": "finance-assistant",
    "legal assistant": "legal-assistant",
    "legal-assistant": "legal-assistant",
    "legal": "legal-assistant",
}


@dataclass(slots=True)
class HttpEvalResponse:
    status_code: int
    body: dict[str, Any]
    headers: dict[str, str]


@dataclass(slots=True)
class EvalObservation:
    response_text: str
    observed_tools: list[str] = field(default_factory=list)
    observed_agents: list[str] = field(default_factory=list)


@dataclass(slots=True)
class EvalResult:
    case_id: str
    ok: bool
    status_code: int | None
    tool_match: bool | None
    route_match: bool | None
    forbidden_tool_hit: bool | None
    error: str | None
    fail_reason: str | None
    response_preview: str
    observed_tools: list[str] = field(default_factory=list)
    observed_agents: list[str] = field(default_factory=list)


def _unique_preserve_order(values: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for value in values:
        if not value or value in seen:
            continue
        seen.add(value)
        ordered.append(value)
    return ordered


@lru_cache(maxsize=1)
def _tool_agent_map() -> dict[str, str]:
    from app.tools.admin import adm_admin_tools, adm_employee_tools
    from app.tools.finance import fin_admin_tools, fin_employee_tools, fin_manager_tools
    from app.tools.hr import all_tools as hr_tools
    from app.tools.it import it_admin_tools, it_employee_tools
    from app.tools.legal import leg_admin_tools, leg_employee_tools

    mapping: dict[str, str] = {}
    for tool in hr_tools:
        mapping[tool.__name__.lower()] = "hr-assistant"
    for tool in adm_employee_tools + adm_admin_tools:
        mapping[tool.__name__.lower()] = "admin-assistant"
    for tool in fin_employee_tools + fin_manager_tools + fin_admin_tools:
        mapping[tool.__name__.lower()] = "finance-assistant"
    for tool in it_employee_tools + it_admin_tools:
        mapping[tool.__name__.lower()] = "it-assistant"
    for tool in leg_employee_tools + leg_admin_tools:
        mapping[tool.__name__.lower()] = "legal-assistant"
    mapping["get_current_user"] = "hr-assistant"
    return mapping


def _normalize_agent(value: str) -> str | None:
    normalized = value.strip().lower()
    return _AGENT_ALIASES.get(normalized)


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
                if key in _TEXT_KEYS or key in _RECURSE_KEYS:
                    walk(value)

    walk(response_json)
    return " ".join(values).strip()


def _collect_tool_names(response_json: dict[str, Any]) -> list[str]:
    names: list[str] = []

    def walk(node: Any, *, inside_tool: bool = False) -> None:
        if isinstance(node, list):
            for item in node:
                walk(item, inside_tool=inside_tool)
            return
        if isinstance(node, dict):
            for key, value in node.items():
                if key in {"tool", "tool_name"}:
                    if isinstance(value, str):
                        names.append(value.strip().lower())
                    else:
                        walk(value, inside_tool=True)
                elif key in {"function", "tool_call", "tool_calls"}:
                    walk(value, inside_tool=True)
                elif key == "name" and inside_tool:
                    if isinstance(value, str):
                        names.append(value.strip().lower())
                elif key in _RECURSE_KEYS:
                    walk(value, inside_tool=False)

    walk(response_json)
    return names


def _collect_agent_names(response_json: dict[str, Any]) -> list[str]:
    names: list[str] = []

    def walk(node: Any, *, inside_member: bool = False) -> None:
        if isinstance(node, list):
            for item in node:
                walk(item, inside_member=inside_member)
            return
        if isinstance(node, dict):
            for key, value in node.items():
                normalized: str | None = None
                if isinstance(value, str):
                    if key in {"agent", "agent_id", "assistant", "assistant_id", "agent_name"}:
                        normalized = _normalize_agent(value)
                    elif key in {"name", "id"} and inside_member:
                        normalized = _normalize_agent(value)
                if normalized:
                    names.append(normalized)

                if key == "member_responses":
                    walk(value, inside_member=True)
                elif key in {"messages", "choices", "delta"}:
                    walk(value, inside_member=inside_member)
                elif isinstance(value, (dict, list)):
                    walk(value, inside_member=inside_member)

    walk(response_json)
    return _unique_preserve_order(names)


def analyze_response(response_json: dict[str, Any]) -> EvalObservation:
    observed_tools = _collect_tool_names(response_json)
    explicit_agents = _collect_agent_names(response_json)
    tool_agents = [
        _tool_agent_map().get(tool)
        for tool in observed_tools
        if _tool_agent_map().get(tool) is not None
    ]
    return EvalObservation(
        response_text=_collect_response_text(response_json),
        observed_tools=observed_tools,
        observed_agents=_unique_preserve_order([*explicit_agents, *tool_agents]),
    )


def _contains_subsequence(values: list[str], expected: list[str]) -> bool:
    if not expected:
        return True
    idx = 0
    for value in values:
        if value == expected[idx]:
            idx += 1
            if idx == len(expected):
                return True
    return False


def _match_expected_tools(case: EvalCase, observed_tools: list[str]) -> bool | None:
    expected_tools = list(case.expected_tools)
    expected_tool_mode = case.expected_tool_mode
    expected_tool_counts = dict(case.expected_tool_counts)
    if not expected_tools and case.expected_tool:
        expected_tools, expected_tool_mode, expected_tool_counts = _parse_tool_expectation(
            case.expected_tool
        )
    if not expected_tools:
        return None
    counts = Counter(observed_tools)
    if expected_tool_mode == "any":
        return any(counts[tool] >= expected_tool_counts.get(tool, 1) for tool in expected_tools)
    if expected_tool_mode == "ordered":
        ordered_expected: list[str] = []
        for tool in expected_tools:
            ordered_expected.extend([tool] * expected_tool_counts.get(tool, 1))
        return _contains_subsequence(observed_tools, ordered_expected)
    return all(counts[tool] >= expected_tool_counts.get(tool, 1) for tool in expected_tools)


def _match_expected_agents(case: EvalCase, observed_agents: list[str]) -> bool | None:
    if not case.expected_agents:
        return None
    if not observed_agents:
        return None
    if case.expected_agent_mode == "any":
        return any(agent in observed_agents for agent in case.expected_agents)
    if case.expected_agent_mode == "ordered":
        return _contains_subsequence(observed_agents, case.expected_agents)
    return all(agent in observed_agents for agent in case.expected_agents)


def _hit_forbidden_tools(case: EvalCase, observed_tools: list[str]) -> bool | None:
    if not case.forbidden_tools:
        return None
    observed = set(observed_tools)
    return any(tool in observed for tool in case.forbidden_tools)


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
    observation = analyze_response(response_json)
    tool_match = _match_expected_tools(case, observation.observed_tools)
    route_match = _match_expected_agents(case, observation.observed_agents)
    forbidden_tool_hit = _hit_forbidden_tools(case, observation.observed_tools)

    ok = status_code == 200
    fail_reason: str | None = None
    if status_code != 200:
        ok = False
        fail_reason = _map_http_status_reason(status_code)
    elif forbidden_tool_hit:
        ok = False
        fail_reason = "forbidden_tool_called"
    elif tool_match is False:
        ok = False
        fail_reason = "tool_mismatch"
    elif route_match is False:
        ok = False
        fail_reason = "route_mismatch"

    return EvalResult(
        case_id=case.case_id,
        ok=ok,
        status_code=status_code,
        tool_match=tool_match,
        route_match=route_match,
        forbidden_tool_hit=forbidden_tool_hit,
        error=None,
        fail_reason=fail_reason,
        response_preview=observation.response_text[:160],
        observed_tools=observation.observed_tools,
        observed_agents=observation.observed_agents,
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
                    route_match=None,
                    forbidden_tool_hit=None,
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
        auth_token_resolver: Callable[[EvalCase], str] | None = None,
    ) -> None:
        import httpx

        self._client = httpx.AsyncClient(base_url=base_url, timeout=timeout)
        self._auth_token = auth_token
        self._auth_token_resolver = auth_token_resolver
        self.endpoint = endpoint
        self.message_field = message_field
        self.request_mode = request_mode

    def _resolved_mode(self) -> str:
        if self.request_mode in {"json", "form"}:
            return self.request_mode
        if "/runs" in self.endpoint and "/teams/" in self.endpoint:
            return "form"
        return "json"

    def _build_headers(self, case: EvalCase) -> dict[str, str]:
        token = self._auth_token_resolver(case) if self._auth_token_resolver else self._auth_token
        if not token:
            return {}
        return {"Authorization": f"Bearer {token}"}

    async def __call__(self, case: EvalCase) -> HttpEvalResponse:
        payload = {self.message_field: case.user_input}
        headers = self._build_headers(case)
        mode = self._resolved_mode()
        if mode == "form":
            payload["stream"] = "false"
            payload["monitor"] = "false"
            response = await self._client.post(self.endpoint, data=payload, headers=headers or None)
        else:
            response = await self._client.post(self.endpoint, json=payload, headers=headers or None)
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
