import argparse
import json
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.evals.runner import collect_eval_cases, summarize_cases


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="解析 tests 下的评估 Markdown 用例并输出统计")
    parser.add_argument("--tests-dir", default="tests", help="评估文件目录")
    parser.add_argument("--pattern", default="test_evaluation_*.md", help="评估文件 glob")
    parser.add_argument("--id-prefix", default="", help="按用例 ID 前缀过滤，如 EMP/ADM/CD")
    parser.add_argument("--output-json", default="", help="输出完整用例 JSON 文件路径")
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    cases = collect_eval_cases(args.tests_dir, args.pattern)
    if args.id_prefix:
        prefix = f"{args.id_prefix}-"
        cases = [case for case in cases if case.case_id.startswith(prefix)]

    print(f"评估文件目录: {args.tests_dir}")
    print(f"匹配模式: {args.pattern}")
    print(f"总用例数: {len(cases)}")
    print("按 ID 前缀统计:")
    for key, value in summarize_cases(cases).items():
        print(f"- {key}: {value}")

    if args.output_json:
        output_path = Path(args.output_json)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(
            json.dumps(
                [
                    {
                        "id": case.case_id,
                        "file": case.file_path,
                        "section": case.section,
                        "subsection": case.subsection,
                        "user_input": case.user_input,
                        "expected_tool": case.expected_tool,
                        "expected_behavior": case.expected_behavior,
                        "raw": case.raw,
                    }
                    for case in cases
                ],
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
        print(f"已输出 JSON: {output_path}")


if __name__ == "__main__":
    main()
