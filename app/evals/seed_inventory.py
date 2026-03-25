from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


class SeedInventoryLookupError(LookupError):
    pass


_NUMBER_RE = re.compile(r"^-?\d+(?:\.\d+)?$")


def _split_sql_statements(sql_text: str) -> list[str]:
    statements: list[str] = []
    current: list[str] = []
    in_string = False
    i = 0
    while i < len(sql_text):
        char = sql_text[i]
        if in_string:
            if char == "'":
                if i + 1 < len(sql_text) and sql_text[i + 1] == "'":
                    current.append("'")
                    i += 2
                    continue
                in_string = False
                current.append(char)
                i += 1
                continue
            current.append(char)
            i += 1
            continue
        if char == "'":
            in_string = True
            current.append(char)
            i += 1
            continue
        if char == ";":
            statement = "".join(current).strip()
            if statement:
                statements.append(statement)
            current = []
            i += 1
            continue
        current.append(char)
        i += 1
    tail = "".join(current).strip()
    if tail:
        statements.append(tail)
    return statements


def _strip_leading_sql_comments(statement: str) -> str:
    lines = statement.splitlines()
    while lines:
        stripped = lines[0].lstrip()
        if not stripped or stripped.startswith("--"):
            lines.pop(0)
            continue
        break
    return "\n".join(lines).strip()


def _split_sql_values(values_text: str) -> list[str]:
    values: list[str] = []
    current: list[str] = []
    in_string = False
    i = 0
    while i < len(values_text):
        char = values_text[i]
        if in_string:
            if char == "'":
                if i + 1 < len(values_text) and values_text[i + 1] == "'":
                    current.append("'")
                    i += 2
                    continue
                in_string = False
                i += 1
                continue
            current.append(char)
            i += 1
            continue
        if char == "'":
            in_string = True
            i += 1
            continue
        if char == ",":
            values.append("".join(current).strip())
            current = []
            i += 1
            continue
        current.append(char)
        i += 1
    values.append("".join(current).strip())
    return values


def _coerce_sql_value(raw_value: str) -> Any:
    if raw_value.upper() == "NULL":
        return None
    if len(raw_value) >= 2 and raw_value[0] == "'" and raw_value[-1] == "'":
        return raw_value[1:-1].replace("''", "'")
    if _NUMBER_RE.fullmatch(raw_value):
        return float(raw_value) if "." in raw_value else int(raw_value)
    return raw_value


def parse_insert_values(sql_text: str, table_name: str) -> list[dict[str, Any]]:
    pattern = re.compile(
        rf"^\s*INSERT\s+INTO\s+{re.escape(table_name)}\s*\((?P<columns>.*?)\)\s*VALUES\s*(?P<values>.+?)\s*$",
        flags=re.IGNORECASE | re.DOTALL,
    )
    rows: list[dict[str, Any]] = []
    for statement in _split_sql_statements(sql_text):
        statement = _strip_leading_sql_comments(statement)
        match = pattern.match(statement)
        if not match:
            continue
        columns = [column.strip() for column in match.group("columns").split(",")]
        values_block = match.group("values").strip()
        tuple_texts: list[str] = []
        current: list[str] = []
        depth = 0
        in_string = False
        i = 0
        while i < len(values_block):
            char = values_block[i]
            if in_string:
                current.append(char)
                if char == "'":
                    if i + 1 < len(values_block) and values_block[i + 1] == "'":
                        current.append(values_block[i + 1])
                        i += 2
                        continue
                    in_string = False
                i += 1
                continue
            if char == "'":
                in_string = True
                current.append(char)
                i += 1
                continue
            if char == "(":
                depth += 1
                if depth == 1:
                    current = []
                    i += 1
                    continue
            elif char == ")":
                depth -= 1
                if depth == 0:
                    tuple_texts.append("".join(current).strip())
                    current = []
                    i += 1
                    continue
            if depth >= 1:
                current.append(char)
            i += 1
        for tuple_text in tuple_texts:
            values = [_coerce_sql_value(value) for value in _split_sql_values(tuple_text)]
            if len(columns) != len(values):
                raise ValueError(f"Column/value count mismatch for table {table_name}")
            rows.append(dict(zip(columns, values)))
    return rows


def _read_sql_file(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _index_by_id(rows: list[dict[str, Any]]) -> dict[int, dict[str, Any]]:
    indexed: dict[int, dict[str, Any]] = {}
    for row in rows:
        row_id = row.get("id")
        if isinstance(row_id, int):
            indexed[row_id] = row
    return indexed


@dataclass
class SeedInventory:
    employees: list[dict[str, Any]] = field(default_factory=list)
    departments: list[dict[str, Any]] = field(default_factory=list)
    meeting_rooms: list[dict[str, Any]] = field(default_factory=list)
    reimbursements: list[dict[str, Any]] = field(default_factory=list)
    it_tickets: list[dict[str, Any]] = field(default_factory=list)

    @classmethod
    def from_project_seed_files(cls) -> "SeedInventory":
        root = Path(__file__).resolve().parents[2]
        seed_files = [
            root / "scripts" / "seed.sql",
            root / "scripts" / "admin_seed.sql",
            root / "scripts" / "finance_seed.sql",
            root / "scripts" / "it_seed.sql",
            root / "scripts" / "legal_seed.sql",
        ]
        sql_texts = [_read_sql_file(path) for path in seed_files]
        combined_sql = "\n".join(sql_texts)
        inventory = cls(
            employees=parse_insert_values(combined_sql, "employees"),
            departments=parse_insert_values(combined_sql, "departments"),
            meeting_rooms=parse_insert_values(combined_sql, "meeting_rooms"),
            reimbursements=parse_insert_values(combined_sql, "reimbursements"),
            it_tickets=parse_insert_values(combined_sql, "it_tickets"),
        )
        inventory._ensure_required_tables_present()
        inventory._apply_department_manager_updates(sql_texts[0])
        return inventory

    def _ensure_required_tables_present(self) -> None:
        required_tables = {
            "employees": self.employees,
            "departments": self.departments,
            "meeting_rooms": self.meeting_rooms,
            "reimbursements": self.reimbursements,
            "it_tickets": self.it_tickets,
        }
        for table_name, rows in required_tables.items():
            if not rows:
                raise SeedInventoryLookupError(f"Seed inventory table is empty: {table_name}")

    def _apply_department_manager_updates(self, sql_text: str) -> None:
        departments_by_id = _index_by_id(self.departments)
        for line in sql_text.splitlines():
            match = re.match(
                r"^\s*UPDATE\s+departments\s+SET\s+manager_id\s*=\s*(?P<manager_id>\d+|NULL)\s+WHERE\s+id\s*=\s*(?P<department_id>\d+)\s*;\s*$",
                line,
                re.IGNORECASE,
            )
            if not match:
                continue
            department_id = int(match.group("department_id"))
            department = departments_by_id.get(department_id)
            if department is None:
                continue
            manager_id = match.group("manager_id")
            department["manager_id"] = None if manager_id.upper() == "NULL" else int(manager_id)

    def _find_one(self, rows: list[dict[str, Any]], *, entity_name: str, **criteria: Any) -> dict[str, Any]:
        for row in rows:
            if all(row.get(key) == value for key, value in criteria.items() if value is not None):
                return row
        criteria_text = ", ".join(f"{key}={value!r}" for key, value in criteria.items() if value is not None)
        raise SeedInventoryLookupError(f"找不到{entity_name}：{criteria_text}")

    def find_employee(self, *, employee_id: int | None = None, name: str | None = None) -> dict[str, Any]:
        return self._find_one(self.employees, entity_name="员工", id=employee_id, name=name)

    def find_department(self, *, department_id: int | None = None, name: str | None = None) -> dict[str, Any]:
        return self._find_one(self.departments, entity_name="部门", id=department_id, name=name)

    def find_available_room(self) -> dict[str, Any]:
        for room in self.meeting_rooms:
            if room.get("status") == "available":
                return room
        raise SeedInventoryLookupError("找不到可用会议室")

    def find_pending_reimbursement(self) -> dict[str, Any]:
        for reimbursement in self.reimbursements:
            if reimbursement.get("status") == "pending":
                return reimbursement
        raise SeedInventoryLookupError("找不到待审批报销单")

    def find_open_it_ticket(self) -> dict[str, Any]:
        for ticket in self.it_tickets:
            if ticket.get("status") == "open":
                return ticket
        raise SeedInventoryLookupError("找不到未处理 IT 工单")


__all__ = [
    "SeedInventory",
    "SeedInventoryLookupError",
    "parse_insert_values",
]
