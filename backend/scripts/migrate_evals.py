"""兼容旧入口的评测数据集发布脚本"""
from __future__ import annotations
import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from publish_eval_datasets import run as run_publish_eval_datasets


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="将评测数据集发布到 Langfuse")
    parser.add_argument("--tests-dir", default="tests", help="兼容旧参数，已不再使用")
    parser.add_argument("--pattern", default="test_evaluation_*.md", help="兼容旧参数，已不再使用")
    parser.add_argument("--dataset-name", default="mx-agent-evals", help="兼容旧参数，已不再使用")
    parser.add_argument("--dataset-prefix", default="mx", help="数据集名前缀")
    parser.add_argument("--dry-run", action="store_true", help="仅打印，不实际写入")
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    run_publish_eval_datasets(dataset_prefix=args.dataset_prefix, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
