from app.evals.executor import execute_cases, score_case
from app.evals.runner import EvalCase


def make_case(case_id: str, expected_tool: str) -> EvalCase:
    return EvalCase(
        case_id=case_id,
        file_path="tests/demo.md",
        section="s",
        subsection="ss",
        user_input="你好",
        expected_tool=expected_tool,
        expected_behavior="",
        raw={},
    )


def test_score_case_tool_match():
    case = make_case("EMP-01", "get_salary_info")
    result = score_case(case, 200, {"reply": "将调用 get_salary_info 获取数据"})
    assert result.ok is True
    assert result.tool_match is True


def test_score_case_tool_mismatch():
    case = make_case("EMP-01", "get_salary_info")
    result = score_case(case, 200, {"reply": "返回普通文本"})
    assert result.ok is False
    assert result.tool_match is False


def test_execute_cases_collects_errors():
    case = make_case("EMP-02", "get_attendance_summary")

    def requester(_: EvalCase) -> tuple[int, dict]:
        raise RuntimeError("boom")

    results = execute_cases([case], requester)
    assert len(results) == 1
    assert results[0].ok is False
    assert results[0].error == "boom"
