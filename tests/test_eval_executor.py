from app.evals.executor import HttpEvalRequester, HttpEvalResponse, execute_cases, score_case
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
    response = {
        "content": "已处理",
        "tool_calls": [{"function": {"name": "get_salary_info"}}],
    }
    result = score_case(case, 200, response)
    assert result.ok is True
    assert result.tool_match is True
    assert result.fail_reason is None


def test_score_case_tool_mismatch():
    case = make_case("EMP-01", "get_salary_info")
    result = score_case(case, 200, {"reply": "返回普通文本"})
    assert result.ok is False
    assert result.tool_match is False
    assert result.fail_reason == "tool_mismatch"


def test_score_case_http_status_failure():
    case = make_case("EMP-01", "get_salary_info")
    result = score_case(case, 401, {"message": "未认证"})
    assert result.ok is False
    assert result.fail_reason == "http_401_unauthorized"


def test_execute_cases_collects_errors():
    case = make_case("EMP-02", "get_attendance_summary")

    def requester(_: EvalCase) -> HttpEvalResponse:
        raise RuntimeError("boom")

    results = execute_cases([case], requester)
    assert len(results) == 1
    assert results[0].ok is False
    assert results[0].error == "boom"
    assert results[0].fail_reason == "request_error"


def test_execute_cases_classifies_timeout_error():
    case = make_case("EMP-09", "get_salary_info")

    def requester(_: EvalCase) -> HttpEvalResponse:
        raise RuntimeError("request timeout after 30s")

    results = execute_cases([case], requester)
    assert results[0].fail_reason == "request_timeout"


def test_score_case_http_5xx_failure_reason():
    case = make_case("EMP-10", "get_salary_info")
    result = score_case(case, 502, {"message": "upstream error"})
    assert result.ok is False
    assert result.fail_reason == "http_5xx_upstream"


def test_score_case_matches_nested_tool_calls():
    case = make_case("EMP-03", "get_salary_info")
    response = {
        "content": "已处理你的请求",
        "member_responses": [
            {"tool_calls": [{"function": {"name": "get_salary_info"}}]},
        ],
    }
    result = score_case(case, 200, response)
    assert result.ok is True
    assert result.tool_match is True


def test_score_case_name_outside_tool_context_no_match():
    """顶层 'name' 字段（非工具上下文）不应被当做工具名。"""
    case = make_case("EMP-04", "get_salary_info")
    response = {"name": "get_salary_info", "reply": "普通文本"}
    result = score_case(case, 200, response)
    assert result.ok is False
    assert result.tool_match is False


def test_requester_auto_mode_for_team_runs():
    requester = HttpEvalRequester(
        base_url="http://localhost:8000",
        endpoint="/teams/router-team/runs",
        request_mode="auto",
    )
    assert requester._resolved_mode() == "form"
    requester.close()
