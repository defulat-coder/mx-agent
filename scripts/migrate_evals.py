"""Markdown 评测用例 → Langfuse Dataset 一次性迁移脚本"""
import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.core.tracing import get_langfuse_client, setup_tracing
from app.evals.runner import collect_eval_cases


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="将 Markdown 评测用例迁移到 Langfuse Dataset")
    parser.add_argument("--tests-dir", default="tests", help="Markdown 用例目录")
    parser.add_argument("--pattern", default="test_evaluation_*.md", help="文件 glob")
    parser.add_argument("--dataset-name", default="mx-agent-evals", help="Langfuse Dataset 名称")
    parser.add_argument("--dry-run", action="store_true", help="仅打印，不实际写入")
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    setup_tracing()
    client = get_langfuse_client()
    if client is None:
        print("错误: Langfuse 未初始化，请检查 LANGFUSE_* 环境变量", file=sys.stderr)
        sys.exit(1)

    cases = collect_eval_cases(args.tests_dir, args.pattern)
    print(f"共发现 {len(cases)} 条用例，目标 Dataset: {args.dataset_name}")

    if args.dry_run:
        for case in cases[:5]:
            print(f"  [dry-run] {case.case_id}: {case.user_input[:40]}")
        if len(cases) > 5:
            print(f"  ... 共 {len(cases)} 条（dry-run 模式，未写入）")
        return

    # 确保 dataset 存在
    try:
        client.create_dataset(name=args.dataset_name)
        print(f"Dataset '{args.dataset_name}' 已创建")
    except Exception:
        print(f"Dataset '{args.dataset_name}' 已存在，继续写入")

    success = 0
    errors = 0
    for case in cases:
        try:
            # external_id=case.case_id 是幂等 key，Langfuse 用此字段去重
            # 重复执行迁移脚本时不会创建重复 item
            client.create_dataset_item(
                dataset_name=args.dataset_name,
                input={
                    "user_input": case.user_input,
                    "case_id": case.case_id,
                    "section": case.section,
                    "subsection": case.subsection,
                },
                expected_output={
                    "expected_tool": case.expected_tool,
                    "expected_behavior": case.expected_behavior,
                },
                external_id=case.case_id,
            )
            success += 1
        except Exception as e:
            print(f"  写入失败 {case.case_id}: {e}", file=sys.stderr)
            errors += 1

    print(f"迁移完成: 成功 {success}，失败 {errors}")
    if errors == 0:
        print(f"所有用例已写入 Langfuse Dataset '{args.dataset_name}'")
        print("建议执行: mkdir -p tests/archived && mv tests/test_evaluation_*.md tests/archived/")


if __name__ == "__main__":
    main()
