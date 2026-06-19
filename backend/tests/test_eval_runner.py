from app.evals.runner import (
    collect_eval_cases,
    filter_cases_by_prefixes,
    normalize_prefixes,
    parse_eval_markdown,
    summarize_cases,
)


def test_parse_single_markdown_file():
    cases = parse_eval_markdown("tests/archived/test_evaluation_employee_role.md")
    ids = {case.case_id for case in cases}
    assert "EMP-01" in ids
    assert "EDGE-05" in ids
    assert len(cases) >= 30


def test_collect_all_eval_cases():
    cases = collect_eval_cases("tests/archived")
    assert len(cases) >= 300
    prefixes = summarize_cases(cases)
    assert prefixes["EMP"] > 0
    assert prefixes["ADM"] > 0
    assert prefixes["CD"] > 0


def test_normalize_prefixes():
    prefixes = normalize_prefixes(" emp, adm-, cd ")
    assert prefixes == {"EMP", "ADM", "CD"}


def test_filter_cases_by_prefixes():
    cases = collect_eval_cases("tests/archived")
    filtered = filter_cases_by_prefixes(cases, "emp,adm")
    filtered_prefixes = summarize_cases(filtered)
    assert set(filtered_prefixes) <= {"EMP", "ADM"}
    assert filtered_prefixes["EMP"] > 0
    assert filtered_prefixes["ADM"] > 0
