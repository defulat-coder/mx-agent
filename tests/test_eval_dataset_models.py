import pytest
from pydantic import ValidationError

from app.evals import load_profiles, load_yaml
from app.evals.dataset_models import EvalDatasetCase


def make_valid_payload() -> dict:
    return {
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
        "input": {
            "user_input": "我上个月工资多少",
        },
        "expectation": {
            "expected_agents": ["hr-assistant"],
            "expected_agent_mode": "all",
            "expected_tools": [],
            "expected_tool_mode": "none",
            "forbidden_tools": [],
            "response_must_include": ["工资"],
            "response_must_not_include": [],
            "business_assertions": [],
        },
        "seed": {
            "depends_on_entities": [],
            "seed_version": "current",
            "notes": "",
        },
    }


def test_router_case_schema_validation():
    case = EvalDatasetCase.model_validate(make_valid_payload())

    assert case.meta.case_id == "RTR-SMOKE-001"
    assert case.expectation.expected_agent_mode == "all"


def test_load_yaml_returns_mapping():
    data = load_yaml("/Users/cy/PycharmProjects/mx-agent/evals/profiles.yaml")

    assert "employee" in data
    assert data["manager"]["department_id"] == 2


def test_load_profiles_returns_named_personas():
    profiles = load_profiles("/Users/cy/PycharmProjects/mx-agent/evals/profiles.yaml")

    assert "employee" in profiles
    assert profiles["manager"].department_id == 2
    assert profiles["finance_manager"].persona_label == "finance_manager"


@pytest.mark.parametrize(
    ("content", "error_text"),
    [
        ("", "YAML file is empty"),
        ("  \n\t", "YAML file is empty"),
        ("# comment only\n", "YAML file is empty"),
        ("---\n", "YAML file is empty"),
    ],
)
def test_load_yaml_rejects_empty_content(tmp_path, content, error_text):
    path = tmp_path / "empty.yaml"
    path.write_text(content, encoding="utf-8")

    with pytest.raises(ValueError, match=error_text):
        load_yaml(path)


def test_load_yaml_rejects_invalid_yaml(tmp_path):
    path = tmp_path / "broken.yaml"
    path.write_text("employee: [1, 2", encoding="utf-8")

    with pytest.raises(ValueError, match="Invalid YAML"):
        load_yaml(path)


def test_load_profiles_rejects_non_mapping_top_level(tmp_path):
    path = tmp_path / "profiles.yaml"
    path.write_text("- employee\n- manager\n", encoding="utf-8")

    with pytest.raises(ValueError, match="top level"):
        load_profiles(path)


@pytest.mark.parametrize(
    ("mutator", "error_text"),
    [
        (lambda payload: payload["meta"].__setitem__("title", ""), "String should have at least 1 character"),
        (
            lambda payload: payload["auth"].__setitem__("employee_id", 0),
            "Input should be greater than 0",
        ),
        (
            lambda payload: payload["meta"].__setitem__("extra_field", "x"),
            "Extra inputs are not permitted",
        ),
        (
            lambda payload: payload["expectation"].update(
                {"expected_agents": ["hr-assistant"], "expected_agent_mode": "none"}
            ),
            "expected_agents must be empty when expected_agent_mode is none",
        ),
    ],
)
def test_router_case_schema_rejects_invalid_payloads(mutator, error_text):
    payload = make_valid_payload()
    mutator(payload)

    with pytest.raises(ValidationError, match=error_text):
        EvalDatasetCase.model_validate(payload)
