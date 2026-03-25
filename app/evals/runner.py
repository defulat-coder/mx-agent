import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable

_DOMAIN_MAP: dict[str, str] = {
    "employee_role": "employee_role",
    "manager_role": "manager_role",
    "admin_role": "admin_role",
    "cross_domain": "cross_domain",
    "admin_assistant": "admin_assistant",
    "finance_assistant": "finance_assistant",
    "it_assistant": "it_assistant",
    "legal_assistant": "legal_assistant",
    "talent_dev_role": "talent_dev_role",
    "talent_discovery": "talent_discovery",
}

_TOOL_TOKEN_RE = re.compile(r"[a-z][a-z0-9_]{2,}")
_REPEAT_RE = re.compile(r"^\s*[×xX]\s*(\d+)")
_AGENT_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"hr assistant|(?<![a-z])hr(?![a-z])", re.IGNORECASE), "hr-assistant"),
    (re.compile(r"it assistant|(?<![a-z])it(?![a-z])", re.IGNORECASE), "it-assistant"),
    (re.compile(r"admin assistant|(?<![a-z])admin(?![a-z])", re.IGNORECASE), "admin-assistant"),
    (re.compile(r"finance assistant|(?<![a-z])finance(?![a-z])", re.IGNORECASE), "finance-assistant"),
    (re.compile(r"legal assistant|(?<![a-z])legal(?![a-z])", re.IGNORECASE), "legal-assistant"),
]


@dataclass(slots=True)
class EvalAuthProfile:
    employee_id: int
    roles: list[str] = field(default_factory=list)
    department_id: int | None = None
    label: str = ""

    def to_payload(self) -> dict[str, Any]:
        return {
            "employee_id": self.employee_id,
            "roles": list(self.roles),
            "department_id": self.department_id,
            "label": self.label,
        }


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
    domain: str = ""
    auth_profile: EvalAuthProfile | None = None
    expected_tools: list[str] = field(default_factory=list)
    expected_tool_mode: str = "none"
    expected_tool_counts: dict[str, int] = field(default_factory=dict)
    forbidden_tools: list[str] = field(default_factory=list)
    expected_agents: list[str] = field(default_factory=list)
    expected_agent_mode: str = "none"


def _split_md_row(row: str) -> list[str]:
    stripped = row.strip()
    if not (stripped.startswith("|") and stripped.endswith("|")):
        return []
    return [cell.strip() for cell in stripped[1:-1].split("|")]


def _is_separator_row(cells: list[str]) -> bool:
    return all(cell and set(cell) <= {"-", ":"} for cell in cells)


def _extract_domain(file_path: str | Path) -> str:
    name = Path(file_path).stem
    key = re.sub(r"^test_evaluation_", "", name)
    return _DOMAIN_MAP.get(key, key)


def _default_auth_profile(domain: str) -> EvalAuthProfile:
    profiles: dict[str, EvalAuthProfile] = {
        "employee_role": EvalAuthProfile(employee_id=1, roles=[], department_id=7, label="employee"),
        "manager_role": EvalAuthProfile(
            employee_id=9, roles=["manager"], department_id=2, label="manager"
        ),
        "admin_role": EvalAuthProfile(
            employee_id=9, roles=["admin"], department_id=2, label="admin"
        ),
        "cross_domain": EvalAuthProfile(employee_id=1, roles=[], department_id=7, label="employee"),
        "admin_assistant": EvalAuthProfile(
            employee_id=6, roles=["admin_staff"], department_id=4, label="admin_staff"
        ),
        "finance_assistant": EvalAuthProfile(
            employee_id=7,
            roles=["manager", "finance"],
            department_id=5,
            label="finance_manager",
        ),
        "it_assistant": EvalAuthProfile(
            employee_id=9, roles=["it_admin"], department_id=2, label="it_admin"
        ),
        "legal_assistant": EvalAuthProfile(
            employee_id=8, roles=["legal"], department_id=6, label="legal"
        ),
        "talent_dev_role": EvalAuthProfile(
            employee_id=6, roles=["talent_dev"], department_id=4, label="talent_dev"
        ),
        "talent_discovery": EvalAuthProfile(
            employee_id=6, roles=["talent_dev"], department_id=4, label="talent_dev"
        ),
    }
    profile = profiles.get(domain)
    if profile is None:
        return EvalAuthProfile(employee_id=1, roles=[], department_id=7, label="employee")
    return EvalAuthProfile(
        employee_id=profile.employee_id,
        roles=list(profile.roles),
        department_id=profile.department_id,
        label=profile.label,
    )


def _unique_preserve_order(values: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for value in values:
        if not value or value in seen:
            continue
        seen.add(value)
        ordered.append(value)
    return ordered


def _parse_tool_expectation(text: str) -> tuple[list[str], str, dict[str, int]]:
    cleaned = (text or "").strip()
    if not cleaned or cleaned in {"—", "-"}:
        return [], "none", {}

    ordered: list[str] = []
    counts: dict[str, int] = {}
    for match in _TOOL_TOKEN_RE.finditer(cleaned):
        token = match.group(0).lower()
        repeat = 1
        repeat_match = _REPEAT_RE.match(cleaned[match.end() : match.end() + 6])
        if repeat_match:
            repeat = max(1, int(repeat_match.group(1)))
        counts[token] = counts.get(token, 0) + repeat
        ordered.extend([token] * repeat)

    if not ordered:
        return [], "none", {}

    lowered = cleaned.lower()
    if "→" in cleaned or "->" in cleaned:
        mode = "ordered"
    elif "或" in cleaned or " or " in lowered:
        mode = "any"
    else:
        mode = "all"
    return _unique_preserve_order(ordered), mode, counts


def _parse_forbidden_tools(text: str) -> list[str]:
    tools, _, _ = _parse_tool_expectation(text)
    return tools


def _parse_agent_expectation(text: str, column_name: str) -> tuple[list[str], str]:
    cleaned = (text or "").strip()
    if not cleaned or cleaned in {"—", "-"}:
        return [], "none"

    matches: list[tuple[int, str]] = []
    for pattern, agent_id in _AGENT_PATTERNS:
        for match in pattern.finditer(cleaned):
            matches.append((match.start(), agent_id))
    agents = _unique_preserve_order(agent_id for _, agent_id in sorted(matches, key=lambda x: x[0]))
    if not agents:
        return [], "none"

    lowered = cleaned.lower()
    if column_name == "预期调度顺序" or "→" in cleaned or "->" in cleaned:
        mode = "ordered"
    elif column_name == "预期涉及 Agent":
        mode = "all"
    elif "或" in cleaned or " or " in lowered:
        mode = "any"
    else:
        mode = "all"
    return agents, mode


def parse_eval_markdown(file_path: str | Path) -> list[EvalCase]:
    path = Path(file_path)
    lines = path.read_text(encoding="utf-8").splitlines()
    domain = _extract_domain(path)

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
                expected_tools, expected_tool_mode, expected_tool_counts = _parse_tool_expectation(
                    expected_tool
                )
                forbidden_tools = _parse_forbidden_tools(data.get("不应调用", ""))
                route_text = (
                    data.get("预期调度顺序")
                    or data.get("预期涉及 Agent")
                    or data.get("预期路由")
                    or ""
                )
                expected_agents, expected_agent_mode = _parse_agent_expectation(
                    route_text,
                    "预期调度顺序"
                    if data.get("预期调度顺序")
                    else "预期涉及 Agent"
                    if data.get("预期涉及 Agent")
                    else "预期路由",
                )
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
                        domain=domain,
                        auth_profile=_default_auth_profile(domain),
                        expected_tools=expected_tools,
                        expected_tool_mode=expected_tool_mode,
                        expected_tool_counts=expected_tool_counts,
                        forbidden_tools=forbidden_tools,
                        expected_agents=expected_agents,
                        expected_agent_mode=expected_agent_mode,
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
