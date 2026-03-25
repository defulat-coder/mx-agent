"""langfuse_eval 核心逻辑单元测试"""
from app.evals.executor import HttpEvalResponse
from app.evals.langfuse_eval import (
    EvalRunSummary,
    FailedItem,
    _compute_tool_match,
    _extract_trace_id,
)
from app.evals.runner import EvalCase


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


def test_compute_tool_match_hit():
    case = make_case(expected_tool="get_salary_info")
    resp = HttpEvalResponse(
        status_code=200,
        body={"tool_calls": [{"function": {"name": "get_salary_info"}}]},
        headers={},
    )
    assert _compute_tool_match(case, resp) is True


def test_compute_tool_match_miss():
    case = make_case(expected_tool="get_salary_info")
    resp = HttpEvalResponse(status_code=200, body={"reply": "普通回答"}, headers={})
    assert _compute_tool_match(case, resp) is False


def test_compute_tool_match_no_expected_tool():
    case = make_case(expected_tool="—")
    resp = HttpEvalResponse(status_code=200, body={"reply": "任何回答"}, headers={})
    assert _compute_tool_match(case, resp) is None


def test_compute_tool_match_ignores_name_outside_tool_context():
    """'name' 出现在非工具上下文（如用户名）不应被匹配。"""
    case = make_case(expected_tool="get_salary_info")
    resp = HttpEvalResponse(
        status_code=200,
        body={"name": "get_salary_info", "reply": "普通回答"},
        headers={},
    )
    assert _compute_tool_match(case, resp) is False


def test_compute_tool_match_text_mention_not_counted():
    """响应文本中提到工具名但未实际调用，不应匹配。"""
    case = make_case(expected_tool="get_salary_info")
    resp = HttpEvalResponse(
        status_code=200,
        body={"reply": "我无法调用 get_salary_info"},
        headers={},
    )
    assert _compute_tool_match(case, resp) is False
