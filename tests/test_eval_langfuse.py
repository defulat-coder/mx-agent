"""langfuse_eval 核心逻辑单元测试"""
import asyncio
from types import SimpleNamespace

from app.evals.executor import HttpEvalResponse, score_case
from app.evals.judge import JudgeResult
from app.evals.langfuse_eval import (
    EvalRunSummary,
    FailedItem,
    _make_run_name,
    _extract_trace_id,
    _build_case_from_dataset_item,
    run_eval_experiment,
)
from app.evals.publisher import build_dataset_name
from app.evals.runner import EvalCase
from scripts.run_evals import build_parser


def make_case(case_id: str = "EMP-01", expected_tool: str = "get_salary_info") -> EvalCase:
    return EvalCase(
        case_id=case_id,
        file_path="tests/demo.md",
        section="HR",
        subsection="薪资",
        user_input="查薪资",
        expected_tool=expected_tool,
        expected_behavior="调用薪资工具",
        raw={},
    )


def test_extract_trace_id_from_header():
    resp = HttpEvalResponse(
        status_code=200,
        body={},
        headers={"x-trace-id": "trace-abc"},
    )
    assert _extract_trace_id(resp) == "trace-abc"


def test_extract_trace_id_from_body():
    resp = HttpEvalResponse(
        status_code=200,
        body={"trace_id": "trace-xyz"},
        headers={},
    )
    assert _extract_trace_id(resp) == "trace-xyz"


def test_extract_trace_id_returns_none_when_missing():
    resp = HttpEvalResponse(status_code=200, body={}, headers={})
    assert _extract_trace_id(resp) is None


def test_build_case_from_generated_dataset_item() -> None:
    item = SimpleNamespace(
        input={
            "case_id": "RTR-SMOKE-001",
            "original_case_id": "RTR-SMOKE-001",
            "source_file": "evals/datasets/router/templates.yaml",
            "section": "router",
            "subsection": "smoke",
            "user_input": "我上个月工资多少",
            "auth_profile": {
                "employee_id": 1,
                "roles": [],
                "department_id": 7,
                "label": "employee",
                "persona_label": "employee",
            },
        },
        expected_output={
            "expected_agents": ["hr-assistant"],
            "expected_agent_mode": "all",
            "expected_tools": ["get_salary_info"],
            "expected_tool_mode": "all",
            "expected_tool_counts": {},
            "forbidden_tools": ["debug_tool"],
            "expected_behavior": "必须包含: 工资",
        },
    )

    case = _build_case_from_dataset_item(item)

    assert case.expected_agents == ["hr-assistant"]
    assert case.expected_tools == ["get_salary_info"]
    assert case.expected_tool_mode == "all"
    assert case.forbidden_tools == ["debug_tool"]
    assert case.auth_profile.employee_id == 1
    assert case.auth_profile.label == "employee"


def test_run_eval_experiment_filters_object_input_by_id_prefix(monkeypatch) -> None:
    item = SimpleNamespace(
        id="item-1",
        input=SimpleNamespace(
            original_case_id="RTR-SMOKE-001",
            case_id="RTR-SMOKE-001",
            source_file="evals/datasets/router/templates.yaml",
            section="router",
            subsection="smoke",
            user_input="我上个月工资多少",
            auth_profile=SimpleNamespace(
                employee_id=1,
                roles=[],
                department_id=7,
                label="employee",
            ),
        ),
        expected_output={},
        metadata={},
    )
    skipped_item = SimpleNamespace(
        id="item-2",
        input=SimpleNamespace(
            original_case_id="HR-SMOKE-001",
            case_id="HR-SMOKE-001",
        ),
        expected_output={},
        metadata={},
    )

    class FakeDataset:
        items = [item, skipped_item]

    class FakeClient:
        def get_dataset(self, dataset_name: str):
            assert dataset_name == build_dataset_name("router")
            return FakeDataset()

    async def requester(_: EvalCase) -> HttpEvalResponse:
        return HttpEvalResponse(status_code=200, body={"reply": "ok"}, headers={})

    async def judge_fn(*_args):
        return JudgeResult(score=None, reason="")

    monkeypatch.setattr("app.evals.langfuse_eval.get_langfuse_client", lambda: FakeClient())

    summary = asyncio.run(
        run_eval_experiment(
            dataset_name=build_dataset_name("router"),
            run_name=None,
            requester=requester,
            judge_fn=judge_fn,
            id_prefix="RTR",
        )
    )

    assert summary.total == 1
    assert summary.passed == 1


def test_run_evals_default_dataset_name_comes_from_helper() -> None:
    args = build_parser().parse_args([])
    assert args.dataset_name == build_dataset_name("router")


def test_make_run_name_appends_timestamp_for_prefix() -> None:
    run_name = _make_run_name("daily")
    assert run_name.startswith("daily-")


def test_compute_tool_match_hit():
    case = make_case(expected_tool="get_salary_info")
    resp = HttpEvalResponse(
        status_code=200,
        body={"tool_calls": [{"function": {"name": "get_salary_info"}}]},
        headers={},
    )
    assert score_case(case, resp.status_code, resp.body).tool_match is True


def test_compute_tool_match_miss():
    case = make_case(expected_tool="get_salary_info")
    resp = HttpEvalResponse(status_code=200, body={"reply": "普通回答"}, headers={})
    assert score_case(case, resp.status_code, resp.body).tool_match is False


def test_compute_tool_match_no_expected_tool():
    case = make_case(expected_tool="—")
    resp = HttpEvalResponse(status_code=200, body={"reply": "任何回答"}, headers={})
    assert score_case(case, resp.status_code, resp.body).tool_match is None


def test_compute_tool_match_ignores_name_outside_tool_context():
    """'name' 出现在非工具上下文（如用户名）不应被匹配。"""
    case = make_case(expected_tool="get_salary_info")
    resp = HttpEvalResponse(
        status_code=200,
        body={"name": "get_salary_info", "reply": "普通回答"},
        headers={},
    )
    assert score_case(case, resp.status_code, resp.body).tool_match is False


def test_compute_tool_match_text_mention_not_counted():
    """响应文本中提到工具名但未实际调用，不应匹配。"""
    case = make_case(expected_tool="get_salary_info")
    resp = HttpEvalResponse(
        status_code=200,
        body={"reply": "我无法调用 get_salary_info"},
        headers={},
    )
    assert score_case(case, resp.status_code, resp.body).tool_match is False
