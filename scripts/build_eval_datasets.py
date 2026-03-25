"""本地生成评测数据集文件"""
import argparse
import sys
from pathlib import Path

import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.evals.generator import build_eval_datasets


def write_generated_yaml(path: Path, cases) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    ordered_cases = sorted(cases, key=lambda case: case.meta.case_id)
    payload = [case.model_dump() for case in ordered_cases]
    path.write_text(
        yaml.safe_dump(payload, allow_unicode=True, sort_keys=False, default_flow_style=False, width=120),
        encoding="utf-8",
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="生成本地评测数据集文件")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=PROJECT_ROOT / "evals" / "datasets",
        help="生成文件输出目录",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    datasets = build_eval_datasets()
    for domain, cases in sorted(datasets.items()):
        write_generated_yaml(args.output_dir / domain / "generated.yaml", cases)


if __name__ == "__main__":
    main()
