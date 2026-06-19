from __future__ import annotations

from pathlib import Path
from typing import Any

from app.evals.dataset_loader import load_dataset_templates, load_profiles
from app.evals.dataset_models import EvalAuth, EvalDatasetCase, EvalTemplate
from app.evals.seed_inventory import SeedInventory
from app.evals.template_engine import resolve_seed_placeholders, render_template_value

REPO_ROOT = Path(__file__).resolve().parents[2]
DATASET_ROOT = REPO_ROOT / "evals" / "datasets"
PROFILES_PATH = REPO_ROOT / "evals" / "profiles.yaml"
DATASET_NAMES = ("router", "hr", "it", "admin", "finance", "legal", "talent")
REQUIRED_SCENARIO_TYPES = {"smoke", "core", "workflow", "forbidden", "edge"}


def bind_auth_profile(template: EvalTemplate, profiles: dict[str, EvalAuth]) -> EvalAuth:
    try:
        return profiles[template.auth_profile]
    except KeyError as exc:
        raise ValueError(f"Unknown auth profile: {template.auth_profile}") from exc


def _template_to_case(template: EvalTemplate, profiles: dict[str, EvalAuth], inventory: SeedInventory) -> EvalDatasetCase:
    resolved_template = resolve_seed_placeholders(template, inventory)
    payload = resolved_template.model_dump()
    payload["auth"] = bind_auth_profile(template, profiles).model_dump()
    payload["input"] = render_template_value(resolved_template.input.model_dump(), inventory)
    payload["expectation"] = render_template_value(resolved_template.expectation.model_dump(), inventory)
    payload["seed"] = render_template_value(resolved_template.seed.model_dump(), inventory)
    payload.pop("auth_profile", None)
    return EvalDatasetCase.model_validate(payload)


def validate_dataset_balance(cases: list[EvalDatasetCase]) -> None:
    scenario_counts = {
        scenario_type: sum(1 for case in cases if case.meta.scenario_type == scenario_type)
        for scenario_type in REQUIRED_SCENARIO_TYPES
    }
    missing = {scenario_type for scenario_type, count in scenario_counts.items() if count == 0}
    if missing:
        raise ValueError(f"Dataset is missing scenario types: {sorted(missing)}")
    if max(scenario_counts.values()) - min(scenario_counts.values()) > 1:
        raise ValueError(f"Dataset scenario types are imbalanced: {scenario_counts}")


def build_eval_datasets() -> dict[str, list[EvalDatasetCase]]:
    profiles = load_profiles(PROFILES_PATH)
    inventory = SeedInventory.from_project_seed_files()
    datasets: dict[str, list[EvalDatasetCase]] = {}
    for name in DATASET_NAMES:
        templates = load_dataset_templates(DATASET_ROOT / name / "templates.yaml")
        cases = [_template_to_case(template, profiles, inventory) for template in templates]
        validate_dataset_balance(cases)
        datasets[name] = cases
    return datasets


__all__ = [
    "bind_auth_profile",
    "build_eval_datasets",
    "validate_dataset_balance",
]
