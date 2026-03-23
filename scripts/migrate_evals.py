"""Markdown 评测用例 → Langfuse Dataset 一次性迁移脚本"""
import argparse
import re
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.core.tracing import get_langfuse_client, setup_tracing
from app.evals.runner import EvalCase, collect_eval_cases

# 文件名 → 域前缀映射，用于构造全局唯一 case_id
_DOMAIN_MAP: dict[str, str] = {
    "employee_role": "emp",
    "admin_role": "adm",
    "manager_role": "mgr",
    "cross_domain": "cd",
    "admin_assistant": "aa",
    "finance_assistant": "fa",
    "it_assistant": "ita",
    "legal_assistant": "la",
    "talent_dev_role": "td",
    "talent_discovery": "tdi",
}


def _extract_domain(file_path: str) -> str:
    """从文件路径提取域前缀。"""
    name = Path(file_path).stem  # e.g. "test_evaluation_admin_assistant"
    # 移除 test_evaluation_ 前缀
    key = re.sub(r"^test_evaluation_", "", name)
    return _DOMAIN_MAP.get(key, key)


def _make_unique_id(case: EvalCase) -> str:
    """构造全局唯一 ID: {domain}_{case_id}，例如 fa_RT-01。"""
    domain = _extract_domain(case.file_path)
    return f"{domain}_{case.case_id}"


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
        for case in cases[:10]:
            uid = _make_unique_id(case)
            print(f"  [dry-run] {uid}: {case.user_input[:50]}")
        if len(cases) > 10:
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
        unique_id = _make_unique_id(case)
        try:
            # id=unique_id 是幂等 key，Langfuse v4 用 id 字段去重
            # 重复执行迁移脚本时不会创建重复 item
            client.create_dataset_item(
                dataset_name=args.dataset_name,
                input={
                    "user_input": case.user_input,
                    "case_id": unique_id,
                    "original_case_id": case.case_id,
                    "domain": _extract_domain(case.file_path),
                    "section": case.section,
                    "subsection": case.subsection,
                },
                expected_output={
                    "expected_tool": case.expected_tool,
                    "expected_behavior": case.expected_behavior,
                },
                id=unique_id,
            )
            success += 1
        except Exception as e:
            print(f"  写入失败 {unique_id}: {e}", file=sys.stderr)
            errors += 1

    print(f"迁移完成: 成功 {success}，失败 {errors}")
    if errors == 0:
        print(f"所有用例已写入 Langfuse Dataset '{args.dataset_name}'")


if __name__ == "__main__":
    main()
