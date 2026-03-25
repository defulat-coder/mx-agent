"""生成并发布评测数据集到 Langfuse"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.core.tracing import get_langfuse_client, setup_tracing
from app.evals.generator import build_eval_datasets
from app.evals.publisher import build_dataset_name, publish_eval_datasets


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="生成并发布评测数据集到 Langfuse")
    parser.add_argument("--dataset-prefix", default="mx", help="数据集名前缀")
    parser.add_argument("--dry-run", action="store_true", help="仅打印，不实际写入")
    return parser


def run(*, dataset_prefix: str, dry_run: bool) -> None:
    datasets = build_eval_datasets()

    if dry_run:
        for domain, cases in sorted(datasets.items()):
            print(f"{build_dataset_name(domain, dataset_prefix)}: {len(cases)}")
        return

    setup_tracing()
    client = get_langfuse_client()
    if client is None:
        print("错误: Langfuse 未初始化，请检查 LANGFUSE_* 环境变量", file=sys.stderr)
        sys.exit(1)

    published_counts = publish_eval_datasets(client, datasets, dataset_prefix=dataset_prefix)
    for domain, published in sorted(published_counts.items()):
        print(f"{build_dataset_name(domain, dataset_prefix)}: {published}")


def main() -> None:
    args = build_parser().parse_args()
    run(dataset_prefix=args.dataset_prefix, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
