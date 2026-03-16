from app.evals.runner import collect_eval_cases, parse_eval_markdown, summarize_cases


def test_parse_single_markdown_file():
    cases = parse_eval_markdown("tests/test_evaluation_employee_role.md")
    ids = {case.case_id for case in cases}
    assert "EMP-01" in ids
    assert "EDGE-05" in ids
    assert len(cases) >= 30


def test_collect_all_eval_cases():
    cases = collect_eval_cases("tests")
    assert len(cases) >= 300
    prefixes = summarize_cases(cases)
    assert prefixes["EMP"] > 0
    assert prefixes["ADM"] > 0
    assert prefixes["CD"] > 0
