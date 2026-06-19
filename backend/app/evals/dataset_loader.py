from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
from typing import Any

import yaml
from pydantic import ValidationError

from app.evals.dataset_models import EvalAuth, EvalTemplate


def load_yaml(path: str | Path) -> Any:
    raw_text = Path(path).read_text(encoding="utf-8")
    if not raw_text.strip():
        raise ValueError(f"YAML file is empty: {Path(path)}")

    try:
        data = yaml.safe_load(raw_text)
    except yaml.YAMLError as exc:
        raise ValueError(f"Invalid YAML in {Path(path)}") from exc

    if data is None:
        raise ValueError(f"YAML file is empty: {Path(path)}")
    return data


def load_profiles(path: str | Path) -> dict[str, EvalAuth]:
    data = load_yaml(path)
    if data is None:
        raise ValueError(f"YAML file is empty: {Path(path)}")
    if not isinstance(data, Mapping):
        raise ValueError(f"Profiles YAML must contain a mapping at top level: {Path(path)}")
    return {name: EvalAuth.model_validate(value) for name, value in data.items()}


def load_dataset_templates(path: str | Path) -> list[EvalTemplate]:
    data = load_yaml(path)
    if not isinstance(data, list):
        raise ValueError(f"Template YAML must contain a list at top level: {Path(path)}")
    if not data:
        raise ValueError(f"Template YAML is empty: {Path(path)}")

    templates: list[EvalTemplate] = []
    for index, item in enumerate(data):
        try:
            template = EvalTemplate.model_validate(item)
        except ValidationError as exc:
            case_id = None
            if isinstance(item, Mapping):
                case_id = item.get("meta", {}).get("case_id") if isinstance(item.get("meta"), Mapping) else None
            location = f"index={index}"
            if case_id:
                location = f"{location}, case_id={case_id}"
            raise ValueError(f"Invalid template at {location}: {Path(path)}") from exc
        templates.append(template)
    return templates
