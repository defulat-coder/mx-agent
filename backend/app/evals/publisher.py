from __future__ import annotations

from collections.abc import Iterable
from collections.abc import Mapping
from typing import Any, Protocol

from app.evals.dataset_models import EvalDatasetCase


class LangfuseDatasetClient(Protocol):
    def create_dataset(
        self,
        *,
        name: str,
        description: str | None = None,
        metadata: Any = None,
        input_schema: Any = None,
        expected_output_schema: Any = None,
    ) -> Any: ...

    def create_dataset_item(
        self,
        *,
        dataset_name: str,
        input: Any = None,
        expected_output: Any = None,
        metadata: Any = None,
        source_trace_id: str | None = None,
        source_observation_id: str | None = None,
        status: Any = None,
        id: str | None = None,
    ) -> Any: ...


def build_dataset_name(domain: str, prefix: str = "mx") -> str:
    clean_prefix = prefix.rstrip("-")
    if domain == "router":
        return f"{clean_prefix}-router-acceptance"
    return f"{clean_prefix}-agent-{domain}-acceptance"


def build_langfuse_payload(case: EvalDatasetCase) -> dict[str, Any]:
    auth_profile = case.auth.model_dump()
    auth_profile["label"] = case.auth.persona_label
    source_dataset = "router" if case.meta.layer == "router" else case.meta.domain
    source_file = f"evals/datasets/{source_dataset}/templates.yaml"

    expected_tools = list(case.expectation.expected_tools)
    forbidden_tools = list(case.expectation.forbidden_tools)
    expected_agents = list(case.expectation.expected_agents)

    input_payload = {
        "case_id": case.meta.case_id,
        "original_case_id": case.meta.case_id,
        "domain": case.meta.domain,
        "source_file": source_file,
        "section": case.meta.layer,
        "subsection": case.meta.scenario_type,
        "user_input": case.input.user_input,
        "auth_profile": auth_profile,
        "meta": case.meta.model_dump(),
        "seed": case.seed.model_dump(),
    }

    expected_tool_mode = case.expectation.expected_tool_mode
    expected_agent_mode = case.expectation.expected_agent_mode
    expected_output = {
        **case.expectation.model_dump(),
        "expected_behavior": _build_expected_behavior(case),
        "expected_tool": _join_expectation_values(expected_tools, expected_tool_mode),
        "expected_tools": expected_tools,
        "expected_tool_mode": expected_tool_mode,
        "expected_tool_counts": _build_expected_counts(expected_tools),
        "forbidden_tool": _join_expectation_values(forbidden_tools, "all"),
        "forbidden_tools": forbidden_tools,
        "expected_route": _join_expectation_values(expected_agents, expected_agent_mode),
        "expected_agents": expected_agents,
        "expected_agent_mode": expected_agent_mode,
    }
    return {
        "input": input_payload,
        "expected_output": expected_output,
        "metadata": {
            "meta": case.meta.model_dump(),
            "seed": case.seed.model_dump(),
        },
    }


def _join_expectation_values(values: list[str], mode: str) -> str:
    if not values:
        return ""
    if mode == "ordered":
        return " -> ".join(values)
    if mode == "any":
        return " or ".join(values)
    return "、".join(values)


def _build_expected_counts(values: list[str]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for value in values:
        counts[value] = counts.get(value, 0) + 1
    return counts


def _build_expected_behavior(case: EvalDatasetCase) -> str:
    parts: list[str] = []
    if case.expectation.response_must_include:
        parts.append(f"必须包含: {'、'.join(case.expectation.response_must_include)}")
    if case.expectation.response_must_not_include:
        parts.append(f"不能包含: {'、'.join(case.expectation.response_must_not_include)}")
    if case.expectation.business_assertions:
        parts.append(f"业务断言: {'；'.join(case.expectation.business_assertions)}")
    return "；".join(parts)


def _is_conflict_error(exc: Exception) -> bool:
    status_code = getattr(exc, "status_code", None)
    if status_code == 409:
        return True

    response = getattr(exc, "response", None)
    if getattr(response, "status_code", None) == 409:
        return True

    name = exc.__class__.__name__.lower()
    message = str(exc).lower()
    markers = ("conflict", "already exists", "already exist", "duplicate")
    return any(marker in name for marker in markers) or any(marker in message for marker in markers)


def publish_dataset(
    client: LangfuseDatasetClient,
    dataset_name: str,
    cases: Iterable[EvalDatasetCase],
) -> int:
    try:
        client.create_dataset(name=dataset_name)
    except Exception as exc:
        if not _is_conflict_error(exc):
            raise

    published = 0
    for case in cases:
        payload = build_langfuse_payload(case)
        try:
            client.create_dataset_item(
                dataset_name=dataset_name,
                input=payload["input"],
                expected_output=payload["expected_output"],
                metadata=payload["metadata"],
                id=case.meta.case_id,
            )
        except Exception as exc:
            if not _is_conflict_error(exc):
                raise
        published += 1
    return published


def publish_eval_datasets(
    client: LangfuseDatasetClient,
    datasets: Mapping[str, Iterable[EvalDatasetCase]],
    *,
    dataset_prefix: str = "mx",
) -> dict[str, int]:
    published_counts: dict[str, int] = {}
    for domain, cases in sorted(datasets.items()):
        dataset_name = build_dataset_name(domain, dataset_prefix)
        published_counts[domain] = publish_dataset(client, dataset_name, cases)
    return published_counts
