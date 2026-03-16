import argparse
import json
from pathlib import Path
import sys
from collections import Counter

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.evals.executor import HttpEvalRequester, execute_cases
from app.evals.runner import collect_eval_cases, filter_cases_by_prefixes, summarize_cases


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="解析 tests 下的评估 Markdown 用例并输出统计")
    parser.add_argument("--mode", choices=["summary", "execute"], default="summary", help="执行模式")
    parser.add_argument("--tests-dir", default="tests", help="评估文件目录")
    parser.add_argument("--pattern", default="test_evaluation_*.md", help="评估文件 glob")
    parser.add_argument(
        "--id-prefix",
        default="",
        help="按用例 ID 前缀过滤，支持逗号分隔，如 EMP 或 EMP,ADM,CD",
    )
    parser.add_argument("--limit", type=int, default=0, help="限制执行前 N 条用例，0 为不限制")
    parser.add_argument("--base-url", default="http://localhost:8000", help="评估接口地址")
    parser.add_argument("--endpoint", default="/teams/router-team/runs", help="评估接口路径")
    parser.add_argument(
        "--request-mode",
        choices=["auto", "json", "form"],
        default="auto",
        help="请求编码方式，auto 会按 endpoint 自动选择",
    )
    parser.add_argument("--message-field", default="message", help="请求体中的输入字段名")
    parser.add_argument("--auth-token", default="", help="Bearer Token")
    parser.add_argument("--timeout", type=float, default=30.0, help="接口超时秒数")
    parser.add_argument("--show-failed", type=int, default=5, help="打印前 N 条失败样例，0 表示不打印")
    parser.add_argument("--output-json", default="", help="输出完整用例 JSON 文件路径")
    return parser


def case_to_dict(case: object) -> dict:
    from app.evals.runner import EvalCase

    eval_case = case if isinstance(case, EvalCase) else None
    if eval_case is None:
        raise TypeError("invalid case")
    return {
        "id": eval_case.case_id,
        "file": eval_case.file_path,
        "section": eval_case.section,
        "subsection": eval_case.subsection,
        "user_input": eval_case.user_input,
        "expected_tool": eval_case.expected_tool,
        "expected_behavior": eval_case.expected_behavior,
        "raw": eval_case.raw,
    }


def print_summary(cases: list) -> None:
    print(f"总用例数: {len(cases)}")
    print("按 ID 前缀统计:")
    for key, value in summarize_cases(cases).items():
        print(f"- {key}: {value}")


def run_execute_mode(args: argparse.Namespace, cases: list) -> list[dict]:
    requester = HttpEvalRequester(
        base_url=args.base_url,
        endpoint=args.endpoint,
        timeout=args.timeout,
        auth_token=args.auth_token,
        message_field=args.message_field,
        request_mode=args.request_mode,
    )
    try:
        results = execute_cases(cases, requester)
    finally:
        requester.close()
    passed = sum(1 for result in results if result.ok)
    errors = sum(1 for result in results if result.error)
    tool_miss = sum(1 for result in results if result.tool_match is False)
    status_counter = Counter(result.status_code for result in results if result.status_code is not None)
    reason_counter = Counter(result.fail_reason for result in results if result.fail_reason)
    print(f"执行用例数: {len(results)}")
    print(f"通过数: {passed}")
    print(f"失败数: {len(results) - passed}")
    print(f"请求异常数: {errors}")
    print(f"工具匹配失败数: {tool_miss}")
    if status_counter:
        print("状态码分布:")
        for code, count in sorted(status_counter.items(), key=lambda item: item[0]):
            print(f"- {code}: {count}")
    if reason_counter:
        print("失败原因分布:")
        for reason, count in sorted(reason_counter.items(), key=lambda item: item[0]):
            print(f"- {reason}: {count}")
    if args.show_failed > 0:
        failed_results = [result for result in results if not result.ok]
        if failed_results:
            print(f"失败样例 Top {min(args.show_failed, len(failed_results))}:")
            for result in failed_results[: args.show_failed]:
                print(
                    f"- {result.case_id} | reason={result.fail_reason} | status={result.status_code} | preview={result.response_preview[:60]}"
                )
    return [
        {
            "id": result.case_id,
            "ok": result.ok,
            "status_code": result.status_code,
            "tool_match": result.tool_match,
            "error": result.error,
            "fail_reason": result.fail_reason,
            "response_preview": result.response_preview,
        }
        for result in results
    ]


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    cases = collect_eval_cases(args.tests_dir, args.pattern)
    if args.id_prefix:
        cases = filter_cases_by_prefixes(cases, args.id_prefix)
    if args.limit > 0:
        cases = cases[: args.limit]

    print(f"模式: {args.mode}")
    print(f"评估文件目录: {args.tests_dir}")
    print(f"匹配模式: {args.pattern}")
    print_summary(cases)

    output_items: list[dict] = [case_to_dict(case) for case in cases]
    if args.mode == "execute":
        output_items = run_execute_mode(args, cases)

    if args.output_json:
        output_path = Path(args.output_json)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(
            json.dumps(output_items, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        print(f"已输出 JSON: {output_path}")


if __name__ == "__main__":
    main()
