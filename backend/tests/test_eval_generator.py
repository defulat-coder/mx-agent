from pathlib import Path
from subprocess import run

import pytest
import yaml

from app.evals import load_profiles
from app.evals.dataset_loader import load_dataset_templates
from app.evals.generator import build_eval_datasets, validate_dataset_balance
from app.evals.template_engine import render_template_text
from app.evals.seed_inventory import SeedInventory
from app.tools.admin import adm_admin_tools, adm_employee_tools
from app.tools.finance import fin_admin_tools, fin_employee_tools, fin_manager_tools
from app.tools.hr import admin_tools as hr_admin_tools
from app.tools.hr import discovery_tools as hr_discovery_tools
from app.tools.hr import employee_tools as hr_employee_tools
from app.tools.hr import manager_tools as hr_manager_tools
from app.tools.hr import talent_dev_tools as hr_talent_dev_tools
from app.tools.it import it_admin_tools, it_employee_tools
from app.tools.legal import leg_admin_tools, leg_employee_tools

REPO_ROOT = Path(__file__).resolve().parents[1]
ROUTER_TEMPLATES = REPO_ROOT / "evals" / "datasets" / "router" / "templates.yaml"
PROFILES_PATH = REPO_ROOT / "evals" / "profiles.yaml"
DOMAIN_TEMPLATES = {
    "hr": REPO_ROOT / "evals" / "datasets" / "hr" / "templates.yaml",
    "it": REPO_ROOT / "evals" / "datasets" / "it" / "templates.yaml",
    "admin": REPO_ROOT / "evals" / "datasets" / "admin" / "templates.yaml",
    "finance": REPO_ROOT / "evals" / "datasets" / "finance" / "templates.yaml",
    "legal": REPO_ROOT / "evals" / "datasets" / "legal" / "templates.yaml",
    "talent": REPO_ROOT / "evals" / "datasets" / "talent" / "templates.yaml",
}
REQUIRED_SCENARIO_TYPES = {"smoke", "core", "workflow", "forbidden", "edge"}
REGISTERED_TOOL_NAMES = {
    tool.__name__
    for tool in (
        *hr_employee_tools,
        *hr_manager_tools,
        *hr_admin_tools,
        *hr_talent_dev_tools,
        *hr_discovery_tools,
        *it_employee_tools,
        *it_admin_tools,
        *adm_employee_tools,
        *adm_admin_tools,
        *fin_employee_tools,
        *fin_manager_tools,
        *fin_admin_tools,
        *leg_employee_tools,
        *leg_admin_tools,
    )
}


def test_load_dataset_templates_loads_router_templates():
    templates = load_dataset_templates(ROUTER_TEMPLATES)

    assert len(templates) >= 5


def test_router_templates_cover_required_scenario_types():
    templates = load_dataset_templates(ROUTER_TEMPLATES)
    scenario_types = {template.meta.scenario_type for template in templates}

    assert {"smoke", "core", "workflow", "forbidden", "edge"} <= scenario_types


def test_router_templates_include_expected_agents():
    templates = load_dataset_templates(ROUTER_TEMPLATES)
    expected_agents = {
        agent
        for template in templates
        for agent in template.expectation.expected_agents
    }

    assert {
        "hr-assistant",
        "it-assistant",
        "admin-assistant",
        "finance-assistant",
        "legal-assistant",
    } <= expected_agents


def test_router_core_002_is_it_scenario():
    templates = load_dataset_templates(ROUTER_TEMPLATES)
    template = next(item for item in templates if item.meta.case_id == "RTR-CORE-002")

    assert template.meta.domain == "it"
    assert template.expectation.expected_agents == ["it-assistant"]
    assert "admin-assistant" not in template.expectation.expected_agents


@pytest.mark.parametrize(("domain", "path"), list(DOMAIN_TEMPLATES.items()))
def test_domain_templates_exist_and_cover_required_scenario_types(domain, path):
    assert path.exists()

    templates = load_dataset_templates(path)
    scenario_types = {template.meta.scenario_type for template in templates}

    assert REQUIRED_SCENARIO_TYPES <= scenario_types


@pytest.mark.parametrize(("domain", "path"), list(DOMAIN_TEMPLATES.items()))
def test_domain_templates_use_known_auth_profiles(domain, path):
    profiles = load_profiles(PROFILES_PATH)
    templates = load_dataset_templates(path)

    assert {template.auth_profile for template in templates} <= set(profiles)


@pytest.mark.parametrize(("domain", "path"), list(DOMAIN_TEMPLATES.items()))
def test_domain_template_tools_are_registered(domain, path):
    templates = load_dataset_templates(path)
    used_tools = {
        tool
        for template in templates
        for tool in (
            *template.expectation.expected_tools,
            *template.expectation.forbidden_tools,
        )
    }

    assert used_tools <= REGISTERED_TOOL_NAMES


def test_hr_forbidden_template_blocks_employee_approval_tool():
    templates = load_dataset_templates(DOMAIN_TEMPLATES["hr"])
    template = next(item for item in templates if item.meta.case_id == "HR-FORBIDDEN-001")

    assert "approve_leave_request" in template.expectation.forbidden_tools
    assert "admin_approve_leave_request" in template.expectation.forbidden_tools


def test_legal_edge_template_requires_clarification():
    templates = load_dataset_templates(DOMAIN_TEMPLATES["legal"])
    template = next(item for item in templates if item.meta.case_id == "LEG-EDGE-001")

    assert template.input.user_input == "帮我下载那个模板"
    assert template.expectation.expected_tools == []


def test_load_dataset_templates_rejects_non_list_top_level(tmp_path):
    path = tmp_path / "templates.yaml"
    path.write_text("meta:\n  case_id: X\n", encoding="utf-8")

    with pytest.raises(ValueError, match="top level"):
        load_dataset_templates(path)


def test_build_eval_datasets_includes_router_and_hr_and_binds_auth():
    datasets = build_eval_datasets()

    assert set(datasets) == {"router", "hr", "it", "admin", "finance", "legal", "talent"}
    assert datasets["router"]
    assert datasets["hr"]
    assert REQUIRED_SCENARIO_TYPES <= {case.meta.scenario_type for case in datasets["router"]}
    assert REQUIRED_SCENARIO_TYPES <= {case.meta.scenario_type for case in datasets["hr"]}
    assert all(case.auth.employee_id > 0 for case in datasets["router"])
    assert all(case.auth.employee_id > 0 for case in datasets["hr"])


def test_validate_dataset_balance_rejects_imbalanced_cases():
    datasets = build_eval_datasets()
    cases = list(datasets["router"]) + [datasets["router"][0], datasets["router"][0]]

    with pytest.raises(ValueError, match="imbalanced"):
        validate_dataset_balance(cases)


def test_build_eval_datasets_cli_generates_output_files(tmp_path: Path):
    result = run(
        ["uv", "run", "python", "scripts/build_eval_datasets.py", "--output-dir", str(tmp_path)],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    for domain in ("router", "hr", "it", "admin", "finance", "legal", "talent"):
        generated_path = tmp_path / domain / "generated.yaml"
        assert generated_path.exists()
        payload = yaml.safe_load(generated_path.read_text(encoding="utf-8"))
        assert isinstance(payload, list)
        assert payload
        assert {"meta", "auth", "input", "expectation", "seed"} <= set(payload[0])


def test_render_template_text_resolves_seed_placeholders():
    inventory = SeedInventory.from_project_seed_files()
    room = inventory.find_available_room()
    reimbursement = inventory.find_pending_reimbursement()
    ticket = inventory.find_open_it_ticket()
    employee = inventory.find_employee(employee_id=1)
    department = inventory.find_department(department_id=7)

    rendered = render_template_text(
        "room={{available_room.id}}, reimbursement={{pending_reimbursement.id}}, "
        "ticket={{open_it_ticket.id}}, employee={{employee:1.name}}, department={{department:7.name}}",
        inventory,
    )

    assert rendered == (
        f"room={room['id']}, reimbursement={reimbursement['id']}, "
        f"ticket={ticket['id']}, employee={employee['name']}, department={department['name']}"
    )


def test_render_template_text_resolves_target_employee_placeholder():
    inventory = SeedInventory.from_project_seed_files()

    rendered = render_template_text("target={{target_employee.name}}", inventory)

    assert rendered == f"target={inventory.employees[0]['name']}"
