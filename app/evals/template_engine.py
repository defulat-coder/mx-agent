from __future__ import annotations

import re
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from app.evals.dataset_models import EvalTemplate
from app.evals.seed_inventory import SeedInventory

_PLACEHOLDER_RE = re.compile(r"{{\s*([^{}]+?)\s*}}")


def _resolve_entity(reference: str, inventory: SeedInventory) -> Any:
    entity_spec, _, path = reference.partition(".")
    entity_name, _, entity_id_text = entity_spec.partition(":")
    if entity_name == "target_employee":
        if not inventory.employees:
            raise ValueError("target_employee placeholder requires at least one employee")
        value: Any = inventory.employees[0]
    elif entity_name == "available_room":
        value: Any = inventory.find_available_room()
    elif entity_name == "pending_reimbursement":
        value = inventory.find_pending_reimbursement()
    elif entity_name == "open_it_ticket":
        value = inventory.find_open_it_ticket()
    elif entity_name == "employee":
        if not entity_id_text:
            raise ValueError("employee placeholder requires an id")
        value = inventory.find_employee(employee_id=int(entity_id_text))
    elif entity_name == "department":
        if not entity_id_text:
            raise ValueError("department placeholder requires an id")
        value = inventory.find_department(department_id=int(entity_id_text))
    else:
        raise ValueError(f"Unsupported placeholder entity: {entity_name}")

    if path:
        return _resolve_path(value, path)
    return value


def _resolve_path(value: Any, path: str) -> Any:
    current: Any = value
    for part in path.split("."):
        if isinstance(current, Mapping):
            if part not in current:
                raise ValueError(f"Missing placeholder field: {part}")
            current = current[part]
            continue
        if hasattr(current, part):
            current = getattr(current, part)
            continue
        raise ValueError(f"Unsupported placeholder path: {path}")
    return current


def render_template_text(text: str, inventory: SeedInventory) -> str:
    if "{{" not in text:
        return text

    def replace(match: re.Match[str]) -> str:
        value = _resolve_entity(match.group(1).strip(), inventory)
        return "" if value is None else str(value)

    return _PLACEHOLDER_RE.sub(replace, text)


def render_template_value(value: Any, inventory: SeedInventory) -> Any:
    if isinstance(value, str):
        return render_template_text(value, inventory)
    if isinstance(value, list):
        return [render_template_value(item, inventory) for item in value]
    if isinstance(value, dict):
        return {key: render_template_value(item, inventory) for key, item in value.items()}
    return value


def resolve_seed_placeholders(template: EvalTemplate, inventory: SeedInventory) -> EvalTemplate:
    payload = template.model_dump()
    return EvalTemplate.model_validate(render_template_value(payload, inventory))


__all__ = [
    "render_template_text",
    "render_template_value",
    "resolve_seed_placeholders",
]
