from __future__ import annotations

import pytest

from app.evals.dataset_models import EvalDatasetCase
from app.evals.publisher import build_dataset_name, build_langfuse_payload, publish_dataset


def _make_case() -> EvalDatasetCase:
    return EvalDatasetCase.model_validate(
        {
            "meta": {
                "case_id": "RTR-SMOKE-001",
                "title": "工资问题应路由到 HR",
                "layer": "router",
                "domain": "hr",
                "scenario_type": "smoke",
                "priority": "p0",
            },
            "auth": {
                "employee_id": 1,
                "roles": [],
                "department_id": 7,
                "persona_label": "employee",
            },
            "input": {"user_input": "我上个月工资多少"},
            "expectation": {
                "expected_tools": ["salary_tool"],
                "expected_tool_mode": "all",
                "expected_agents": ["hr-assistant"],
                "expected_agent_mode": "all",
                "forbidden_tools": ["debug_tool"],
                "response_must_include": ["工资"],
                "response_must_not_include": ["电话"],
                "business_assertions": ["必须脱敏"],
            },
            "seed": {"depends_on_entities": [], "seed_version": "current", "notes": ""},
        }
    )


def test_build_langfuse_payload_keeps_structured_expectations() -> None:
    payload = build_langfuse_payload(_make_case())
    assert payload["input"]["original_case_id"] == "RTR-SMOKE-001"
    assert payload["input"]["domain"] == "hr"
    assert payload["input"]["source_file"] == "evals/datasets/router/templates.yaml"
    assert payload["input"]["section"] == "router"
    assert payload["input"]["subsection"] == "smoke"
    assert payload["input"]["auth_profile"]["label"] == "employee"
    assert payload["input"]["auth_profile"]["persona_label"] == "employee"
    assert payload["expected_output"]["expected_behavior"] == "必须包含: 工资；不能包含: 电话；业务断言: 必须脱敏"
    assert payload["expected_output"]["expected_tool"] == "salary_tool"
    assert payload["expected_output"]["expected_tools"] == ["salary_tool"]
    assert payload["expected_output"]["expected_tool_mode"] == "all"
    assert payload["expected_output"]["expected_tool_counts"] == {"salary_tool": 1}
    assert payload["expected_output"]["forbidden_tool"] == "debug_tool"
    assert payload["expected_output"]["forbidden_tools"] == ["debug_tool"]
    assert payload["expected_output"]["expected_route"] == "hr-assistant"
    assert payload["expected_output"]["expected_agents"] == ["hr-assistant"]
    assert payload["expected_output"]["expected_agent_mode"] == "all"
    assert payload["input"]["auth_profile"]["employee_id"] == 1


def test_publish_dataset_calls_langfuse_client() -> None:
    calls: list[tuple[str, dict]] = []

    class FakeClient:
        def create_dataset(self, **kwargs):
            calls.append(("create_dataset", kwargs))

        def create_dataset_item(self, **kwargs):
            calls.append(("create_dataset_item", kwargs))

    published = publish_dataset(FakeClient(), "mx-router-acceptance", [_make_case()])

    assert published == 1
    assert calls[0] == ("create_dataset", {"name": "mx-router-acceptance"})
    assert calls[1][0] == "create_dataset_item"
    assert calls[1][1]["dataset_name"] == "mx-router-acceptance"
    assert calls[1][1]["expected_output"]["expected_agents"] == ["hr-assistant"]
    assert calls[1][1]["input"]["auth_profile"]["employee_id"] == 1


def test_publish_dataset_allows_existing_dataset_conflict() -> None:
    calls: list[tuple[str, dict]] = []

    class FakeClient:
        def create_dataset(self, **kwargs):
            raise RuntimeError("dataset already exists")

        def create_dataset_item(self, **kwargs):
            calls.append(("create_dataset_item", kwargs))

    published = publish_dataset(FakeClient(), "mx-router-acceptance", [_make_case()])

    assert published == 1
    assert calls[0][0] == "create_dataset_item"


def test_publish_dataset_allows_existing_item_conflict() -> None:
    class FakeClient:
        def create_dataset(self, **kwargs):
            return kwargs

        def create_dataset_item(self, **kwargs):
            raise RuntimeError("dataset item already exists")

    published = publish_dataset(FakeClient(), "mx-router-acceptance", [_make_case()])

    assert published == 1


def test_publish_dataset_raises_on_unexpected_create_dataset_error() -> None:
    class FakeClient:
        def create_dataset(self, **kwargs):
            raise ValueError("boom")

        def create_dataset_item(self, **kwargs):
            raise AssertionError("should not publish items")

    with pytest.raises(ValueError, match="boom"):
        publish_dataset(FakeClient(), "mx-router-acceptance", [_make_case()])


def test_publish_dataset_raises_on_unexpected_create_dataset_item_error() -> None:
    class FakeClient:
        def create_dataset(self, **kwargs):
            return kwargs

        def create_dataset_item(self, **kwargs):
            raise ValueError("boom")

    with pytest.raises(ValueError, match="boom"):
        publish_dataset(FakeClient(), "mx-router-acceptance", [_make_case()])


def test_build_dataset_name_smoke() -> None:
    assert build_dataset_name("router") == "mx-router-acceptance"
    assert build_dataset_name("hr") == "mx-agent-hr-acceptance"
    assert build_dataset_name("router", prefix="acme") == "acme-router-acceptance"
