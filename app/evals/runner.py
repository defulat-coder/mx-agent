from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


@dataclass(slots=True)
class EvalCase:
    case_id: str
    file_path: str
    section: str
    subsection: str
    user_input: str
    expected_tool: str
    expected_behavior: str
    raw: dict[str, str]


def _split_md_row(row: str) -> list[str]:
    stripped = row.strip()
    if not (stripped.startswith("|") and stripped.endswith("|")):
        return []
    return [cell.strip() for cell in stripped[1:-1].split("|")]


def _is_separator_row(cells: list[str]) -> bool:
    return all(cell and set(cell) <= {"-", ":"} for cell in cells)


def parse_eval_markdown(file_path: str | Path) -> list[EvalCase]:
    path = Path(file_path)
    lines = path.read_text(encoding="utf-8").splitlines()

    cases: list[EvalCase] = []
    section = ""
    subsection = ""
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if line.startswith("## "):
            section = line[3:].strip()
        elif line.startswith("### "):
            subsection = line[4:].strip()

        if line.startswith("|"):
            header_cells = _split_md_row(line)
            if i + 1 >= len(lines):
                i += 1
                continue
            sep_cells = _split_md_row(lines[i + 1])
            if not header_cells or not sep_cells or len(header_cells) != len(sep_cells):
                i += 1
                continue
            if not _is_separator_row(sep_cells):
                i += 1
                continue
            if "ID" not in header_cells:
                i += 1
                continue

            j = i + 2
            while j < len(lines):
                row = lines[j].strip()
                if not row.startswith("|"):
                    break
                row_cells = _split_md_row(row)
                if len(row_cells) != len(header_cells):
                    j += 1
                    continue
                data = dict(zip(header_cells, row_cells, strict=True))
                case_id = data.get("ID", "").strip()
                if not case_id or case_id == "ID":
                    j += 1
                    continue
                if "-" not in case_id:
                    j += 1
                    continue
                user_input = data.get("用户输入") or data.get("场景", "")
                expected_tool = data.get("期望工具") or data.get("期望工具组合", "")
                expected_behavior = data.get("预期行为") or data.get("验证点", "")
                cases.append(
                    EvalCase(
                        case_id=case_id,
                        file_path=str(path),
                        section=section,
                        subsection=subsection,
                        user_input=user_input,
                        expected_tool=expected_tool,
                        expected_behavior=expected_behavior,
                        raw=data,
                    )
                )
                j += 1
            i = j
            continue
        i += 1
    return cases


def collect_eval_cases(target_dir: str | Path, pattern: str = "test_evaluation_*.md") -> list[EvalCase]:
    root = Path(target_dir)
    all_cases: list[EvalCase] = []
    for file_path in sorted(root.glob(pattern)):
        all_cases.extend(parse_eval_markdown(file_path))
    return all_cases


def summarize_cases(cases: Iterable[EvalCase]) -> dict[str, int]:
    summary: dict[str, int] = {}
    for case in cases:
        prefix = case.case_id.split("-", 1)[0]
        summary[prefix] = summary.get(prefix, 0) + 1
    return dict(sorted(summary.items(), key=lambda item: item[0]))


def normalize_prefixes(prefixes: str | Iterable[str]) -> set[str]:
    if isinstance(prefixes, str):
        raw_items = prefixes.split(",")
    else:
        raw_items = list(prefixes)
    normalized: set[str] = set()
    for item in raw_items:
        value = item.strip().upper().rstrip("-")
        if value:
            normalized.add(value)
    return normalized


def filter_cases_by_prefixes(cases: Iterable[EvalCase], prefixes: str | Iterable[str]) -> list[EvalCase]:
    selected = normalize_prefixes(prefixes)
    if not selected:
        return list(cases)
    return [case for case in cases if case.case_id.split("-", 1)[0].upper() in selected]
