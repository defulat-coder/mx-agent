# Eval Dataset Rebuild Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 重建一套面向业务验收的评测数据集生成与发布链路，覆盖 `router_team` 和各子 agent，并能基于当前 seed 数据稳定重建与发布到 Langfuse。

**Architecture:** 新链路分为四层：数据模型与 schema、seed 解析与 resolver、模板实例化生成器、Langfuse 发布器。`router_team` 和各子 agent 使用独立数据集目录与统一 case 结构，生成时绑定标准身份与真实 seed 实体，运行时继续复用现有评测执行器。

**Tech Stack:** Python 3.13, `uv`, FastAPI 项目现有结构, Pydantic, Langfuse SDK, SQL seed 文件解析, `PyYAML`, pytest

---

## File Structure

**Create:**
- `evals/profiles.yaml`
- `evals/datasets/router/templates.yaml`
- `evals/datasets/hr/templates.yaml`
- `evals/datasets/it/templates.yaml`
- `evals/datasets/admin/templates.yaml`
- `evals/datasets/finance/templates.yaml`
- `evals/datasets/legal/templates.yaml`
- `evals/datasets/talent/templates.yaml`
- `app/evals/dataset_models.py`
- `app/evals/dataset_loader.py`
- `app/evals/seed_inventory.py`
- `app/evals/template_engine.py`
- `app/evals/generator.py`
- `app/evals/publisher.py`
- `scripts/build_eval_datasets.py`
- `scripts/publish_eval_datasets.py`
- `tests/test_eval_dataset_models.py`
- `tests/test_eval_seed_inventory.py`
- `tests/test_eval_generator.py`
- `tests/test_eval_publisher.py`

**Modify:**
- `pyproject.toml`
- `app/evals/__init__.py`
- `scripts/migrate_evals.py`
- `scripts/run_evals.py`
- `app/evals/langfuse_eval.py`
- `app/evals/runner.py`

**Responsibilities:**
- `evals/profiles.yaml`: 标准身份档案，定义员工、主管、admin、finance、legal、it_admin、talent_dev 等 persona。
- `evals/datasets/*/templates.yaml`: 各层业务模板，区分 `smoke/core/workflow/forbidden/edge`。
- `app/evals/dataset_models.py`: 统一 case schema、断言 schema、模板 schema。
- `app/evals/dataset_loader.py`: 读取 YAML 模板与 profiles，做 schema 校验。
- `app/evals/seed_inventory.py`: 从 `scripts/*.sql` 建立 seed 实体库存与按条件查询的 resolver。
- `app/evals/template_engine.py`: 将模板与 seed 实体绑定，实例化最终 case。
- `app/evals/generator.py`: 对外暴露 `build_eval_datasets()`，负责组装全流程。
- `app/evals/publisher.py`: 将生成好的 case 发布到 Langfuse dataset。
- `scripts/build_eval_datasets.py`: 本地生成入口。
- `scripts/publish_eval_datasets.py`: 发布入口。

### Task 1: Add Dataset Schema And Dependency

**Files:**
- Modify: `pyproject.toml`
- Create: `app/evals/dataset_models.py`
- Test: `tests/test_eval_dataset_models.py`

- [ ] **Step 1: Write the failing schema tests**

```python
from app.evals.dataset_models import EvalDatasetCase


def test_case_schema_accepts_router_case():
    case = EvalDatasetCase.model_validate(
        {
            "meta": {
                "case_id": "RTR-SMOKE-001",
                "title": "工资问题应路由到 HR",
                "layer": "router",
                "domain": "hr",
                "scenario_type": "smoke",
                "priority": "p0",
            },
            "auth": {
                "employee_id": 1,
                "roles": [],
                "department_id": 7,
                "persona_label": "employee",
            },
            "input": {"user_input": "我上个月工资多少"},
            "expectation": {
                "expected_agents": ["hr-assistant"],
                "expected_agent_mode": "all",
                "expected_tools": [],
                "expected_tool_mode": "none",
                "forbidden_tools": [],
                "response_must_include": ["工资"],
                "response_must_not_include": [],
                "business_assertions": [],
            },
            "seed": {"depends_on_entities": [], "seed_version": "current", "notes": ""},
        }
    )
    assert case.meta.case_id == "RTR-SMOKE-001"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_eval_dataset_models.py -v`
Expected: FAIL with `ModuleNotFoundError` or missing schema definitions

- [ ] **Step 3: Add `PyYAML` dependency**

```toml
dev = [
    "httpx>=0.28.1",
    "pytest>=9.0.2",
    "pytest-asyncio>=0.24",
    "pyyaml>=6.0.2",
]
```

- [ ] **Step 4: Implement dataset schema**

```python
from typing import Literal
from pydantic import BaseModel, Field


class EvalMeta(BaseModel):
    case_id: str
    title: str
    layer: Literal["router", "agent"]
    domain: Literal["hr", "it", "admin", "finance", "legal", "talent", "cross_domain"]
    scenario_type: Literal["smoke", "core", "workflow", "forbidden", "edge"]
    priority: Literal["p0", "p1", "p2"]


class EvalAuth(BaseModel):
    employee_id: int
    roles: list[str] = Field(default_factory=list)
    department_id: int | None = None
    persona_label: str
```

- [ ] **Step 5: Add top-level case/container models**

```python
class EvalDatasetCase(BaseModel):
    meta: EvalMeta
    auth: EvalAuth
    input: EvalInput
    expectation: EvalExpectation
    seed: EvalSeed
```

- [ ] **Step 6: Run schema tests**

Run: `uv run pytest tests/test_eval_dataset_models.py -v`
Expected: PASS

- [ ] **Step 7: Commit**

```bash
git add pyproject.toml app/evals/dataset_models.py tests/test_eval_dataset_models.py
git commit -m "feat: add eval dataset schema models"
```

### Task 2: Add Profiles And YAML Loader

**Files:**
- Create: `evals/profiles.yaml`
- Create: `app/evals/dataset_loader.py`
- Modify: `app/evals/__init__.py`
- Test: `tests/test_eval_dataset_models.py`

- [ ] **Step 1: Write failing loader tests**

```python
from app.evals.dataset_loader import load_profiles


def test_load_profiles_returns_named_personas():
    profiles = load_profiles("evals/profiles.yaml")
    assert "employee" in profiles
    assert profiles["manager"].department_id == 2
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_eval_dataset_models.py::test_load_profiles_returns_named_personas -v`
Expected: FAIL with missing loader or file

- [ ] **Step 3: Add canonical auth profiles**

```yaml
employee:
  employee_id: 1
  roles: []
  department_id: 7
  persona_label: employee

manager:
  employee_id: 9
  roles: [manager]
  department_id: 2
  persona_label: manager
```

- [ ] **Step 4: Implement YAML loading helpers**

```python
import yaml
from pathlib import Path


def load_yaml(path: str | Path) -> dict:
    return yaml.safe_load(Path(path).read_text(encoding="utf-8"))
```

- [ ] **Step 5: Implement profile mapping**

```python
from app.evals.dataset_models import EvalAuth


def load_profiles(path: str | Path) -> dict[str, EvalAuth]:
    data = load_yaml(path)
    return {name: EvalAuth.model_validate(value) for name, value in data.items()}
```

- [ ] **Step 6: Export loader utilities**

```python
from app.evals.dataset_loader import load_profiles
```

- [ ] **Step 7: Run loader tests**

Run: `uv run pytest tests/test_eval_dataset_models.py -v`
Expected: PASS

- [ ] **Step 8: Commit**

```bash
git add evals/profiles.yaml app/evals/dataset_loader.py app/evals/__init__.py tests/test_eval_dataset_models.py
git commit -m "feat: add eval profiles and yaml loader"
```

### Task 3: Build Seed Inventory From SQL Files

**Files:**
- Create: `app/evals/seed_inventory.py`
- Test: `tests/test_eval_seed_inventory.py`

- [ ] **Step 1: Write failing inventory tests**

```python
from app.evals.seed_inventory import SeedInventory


def test_inventory_can_load_employee_and_department_seed():
    inventory = SeedInventory.from_project_seed_files()
    employee = inventory.find_employee(employee_id=1)
    assert employee["name"] == "张三"
    assert inventory.find_department(department_id=7)["name"] == "后端组"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_eval_seed_inventory.py -v`
Expected: FAIL with missing inventory implementation

- [ ] **Step 3: Implement low-level SQL line parsing**

```python
def parse_insert_values(sql_text: str, table_name: str) -> list[dict[str, str]]:
    # parse INSERT INTO ... VALUES (...) lines into dict rows
    ...
```

- [ ] **Step 4: Add inventory model and constructors**

```python
@dataclass
class SeedInventory:
    employees: list[dict[str, object]]
    departments: list[dict[str, object]]
    meeting_rooms: list[dict[str, object]]
    reimbursements: list[dict[str, object]]
```

- [ ] **Step 5: Add domain query helpers**

```python
def find_employee(self, *, employee_id: int | None = None, name: str | None = None) -> dict[str, object]:
    ...

def find_available_room(self) -> dict[str, object]:
    ...
```

- [ ] **Step 6: Add seed-aware selectors for common business conditions**

```python
def find_pending_reimbursement(self) -> dict[str, object]:
    ...

def find_open_it_ticket(self) -> dict[str, object]:
    ...
```

- [ ] **Step 7: Run seed inventory tests**

Run: `uv run pytest tests/test_eval_seed_inventory.py -v`
Expected: PASS

- [ ] **Step 8: Commit**

```bash
git add app/evals/seed_inventory.py tests/test_eval_seed_inventory.py
git commit -m "feat: add eval seed inventory"
```

### Task 4: Add Template Format And Router Templates

**Files:**
- Create: `evals/datasets/router/templates.yaml`
- Test: `tests/test_eval_generator.py`

- [ ] **Step 1: Write failing router template tests**

```python
from app.evals.dataset_loader import load_dataset_templates


def test_router_templates_have_balanced_scenario_types():
    templates = load_dataset_templates("evals/datasets/router/templates.yaml")
    assert any(t.meta.scenario_type == "workflow" for t in templates)
    assert any(t.meta.scenario_type == "forbidden" for t in templates)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_eval_generator.py::test_router_templates_have_balanced_scenario_types -v`
Expected: FAIL with missing template loader or file

- [ ] **Step 3: Define router template file**

```yaml
- meta:
    case_id: RTR-SMOKE-001
    title: 工资问题应路由到 HR
    layer: router
    domain: hr
    scenario_type: smoke
    priority: p0
  auth_profile: employee
  input:
    user_input: 我上个月工资多少
  expectation:
    expected_agents: [hr-assistant]
    expected_agent_mode: all
```

- [ ] **Step 4: Add workflow and forbidden router templates**

```yaml
- meta:
    case_id: RTR-WF-001
    title: 新员工入职跨域流程
    layer: router
    domain: cross_domain
    scenario_type: workflow
```

- [ ] **Step 5: Implement template loader API**

```python
def load_dataset_templates(path: str | Path) -> list[EvalTemplate]:
    ...
```

- [ ] **Step 6: Run router template tests**

Run: `uv run pytest tests/test_eval_generator.py::test_router_templates_have_balanced_scenario_types -v`
Expected: PASS

- [ ] **Step 7: Commit**

```bash
git add evals/datasets/router/templates.yaml app/evals/dataset_loader.py tests/test_eval_generator.py
git commit -m "feat: add router eval templates"
```

### Task 5: Add Domain Templates For HR/IT/Admin/Finance/Legal/Talent

**Files:**
- Create: `evals/datasets/hr/templates.yaml`
- Create: `evals/datasets/it/templates.yaml`
- Create: `evals/datasets/admin/templates.yaml`
- Create: `evals/datasets/finance/templates.yaml`
- Create: `evals/datasets/legal/templates.yaml`
- Create: `evals/datasets/talent/templates.yaml`
- Test: `tests/test_eval_generator.py`

- [ ] **Step 1: Write failing domain template coverage tests**

```python
from app.evals.dataset_loader import load_dataset_templates


def test_hr_templates_cover_core_and_forbidden_cases():
    templates = load_dataset_templates("evals/datasets/hr/templates.yaml")
    scenario_types = {t.meta.scenario_type for t in templates}
    assert {"smoke", "core", "workflow", "forbidden", "edge"} <= scenario_types
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_eval_generator.py::test_hr_templates_cover_core_and_forbidden_cases -v`
Expected: FAIL because templates do not exist

- [ ] **Step 3: Add HR templates**

```yaml
- meta:
    case_id: HR-CORE-001
    title: 员工查询个人薪资
    layer: agent
    domain: hr
    scenario_type: core
    priority: p0
  auth_profile: employee
  input:
    user_input: 查一下我 2026 年 2 月的工资
  expectation:
    expected_tools: [get_salary_records]
    expected_tool_mode: all
```

- [ ] **Step 4: Add IT/Admin/Finance/Legal/Talent templates**

```yaml
- meta:
    case_id: IT-FORBIDDEN-001
    title: 普通员工不应拿到管理员工具
    layer: agent
    domain: it
    scenario_type: forbidden
```

- [ ] **Step 5: Ensure each domain includes `smoke/core/workflow/forbidden/edge`**

```yaml
# each templates.yaml contains at least one entry for each scenario_type
```

- [ ] **Step 6: Run template coverage tests**

Run: `uv run pytest tests/test_eval_generator.py -v`
Expected: PASS for template coverage checks

- [ ] **Step 7: Commit**

```bash
git add evals/datasets/hr/templates.yaml evals/datasets/it/templates.yaml evals/datasets/admin/templates.yaml evals/datasets/finance/templates.yaml evals/datasets/legal/templates.yaml evals/datasets/talent/templates.yaml tests/test_eval_generator.py
git commit -m "feat: add domain eval templates"
```

### Task 6: Build Template Engine And Dataset Generator

**Files:**
- Create: `app/evals/template_engine.py`
- Create: `app/evals/generator.py`
- Test: `tests/test_eval_generator.py`

- [ ] **Step 1: Write failing generator tests**

```python
from app.evals.generator import build_eval_datasets


def test_build_eval_datasets_resolves_router_and_hr_cases():
    datasets = build_eval_datasets()
    assert "router" in datasets
    assert "hr" in datasets
    assert datasets["router"][0].auth.employee_id > 0
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_eval_generator.py::test_build_eval_datasets_resolves_router_and_hr_cases -v`
Expected: FAIL with missing generator

- [ ] **Step 3: Implement auth profile binding**

```python
def bind_auth_profile(template: EvalTemplate, profiles: dict[str, EvalAuth]) -> EvalDatasetCase:
    ...
```

- [ ] **Step 4: Implement seed placeholder resolution**

```python
def resolve_seed_placeholders(template: EvalTemplate, inventory: SeedInventory) -> EvalDatasetCase:
    # replace placeholders like target_employee, pending_reimbursement, available_room
    ...
```

- [ ] **Step 5: Implement dataset build orchestration**

```python
def build_eval_datasets() -> dict[str, list[EvalDatasetCase]]:
    profiles = load_profiles("evals/profiles.yaml")
    inventory = SeedInventory.from_project_seed_files()
    return {
        "router": build_domain_dataset("router", profiles, inventory),
        "hr": build_domain_dataset("hr", profiles, inventory),
    }
```

- [ ] **Step 6: Add balance validation**

```python
def validate_dataset_balance(cases: list[EvalDatasetCase]) -> None:
    ...
```

- [ ] **Step 7: Run generator tests**

Run: `uv run pytest tests/test_eval_generator.py -v`
Expected: PASS

- [ ] **Step 8: Commit**

```bash
git add app/evals/template_engine.py app/evals/generator.py tests/test_eval_generator.py
git commit -m "feat: add eval dataset generator"
```

### Task 7: Add CLI Builder For Local Generated Files

**Files:**
- Create: `scripts/build_eval_datasets.py`
- Test: `tests/test_eval_generator.py`

- [ ] **Step 1: Write failing CLI smoke test**

```python
from pathlib import Path
from subprocess import run


def test_build_eval_datasets_cli_generates_output_files(tmp_path: Path):
    result = run(
        ["uv", "run", "python", "scripts/build_eval_datasets.py", "--output-dir", str(tmp_path)],
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert (tmp_path / "router" / "generated.yaml").exists()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_eval_generator.py::test_build_eval_datasets_cli_generates_output_files -v`
Expected: FAIL because script does not exist

- [ ] **Step 3: Implement builder script**

```python
datasets = build_eval_datasets()
for domain, cases in datasets.items():
    write_generated_yaml(output_dir / domain / "generated.yaml", cases)
```

- [ ] **Step 4: Add deterministic output ordering**

```python
cases = sorted(cases, key=lambda case: case.meta.case_id)
```

- [ ] **Step 5: Run CLI smoke test**

Run: `uv run pytest tests/test_eval_generator.py::test_build_eval_datasets_cli_generates_output_files -v`
Expected: PASS

- [ ] **Step 6: Commit**

```bash
git add scripts/build_eval_datasets.py tests/test_eval_generator.py
git commit -m "feat: add eval dataset builder cli"
```

### Task 8: Add Langfuse Publisher And Publish Script

**Files:**
- Create: `app/evals/publisher.py`
- Create: `scripts/publish_eval_datasets.py`
- Modify: `scripts/migrate_evals.py`
- Test: `tests/test_eval_publisher.py`

- [ ] **Step 1: Write failing publisher tests**

```python
from app.evals.publisher import build_langfuse_payload


def test_build_langfuse_payload_keeps_structured_expectations():
    payload = build_langfuse_payload(case)
    assert payload["expected_output"]["expected_agents"] == ["hr-assistant"]
    assert payload["input"]["auth_profile"]["employee_id"] == 1
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_eval_publisher.py -v`
Expected: FAIL with missing publisher module

- [ ] **Step 3: Implement publisher helpers**

```python
def build_langfuse_payload(case: EvalDatasetCase) -> dict[str, dict]:
    ...
```

- [ ] **Step 4: Implement dataset publish orchestration**

```python
def publish_dataset(client, dataset_name: str, cases: list[EvalDatasetCase]) -> None:
    ...
```

- [ ] **Step 5: Convert `scripts/migrate_evals.py` into compatibility wrapper**

```python
# load generated datasets and publish them instead of reading legacy markdown directly
```

- [ ] **Step 6: Add dedicated publish CLI**

```python
python scripts/publish_eval_datasets.py --dataset-prefix mx-agent
```

- [ ] **Step 7: Run publisher tests**

Run: `uv run pytest tests/test_eval_publisher.py -v`
Expected: PASS

- [ ] **Step 8: Commit**

```bash
git add app/evals/publisher.py scripts/publish_eval_datasets.py scripts/migrate_evals.py tests/test_eval_publisher.py
git commit -m "feat: add eval dataset publisher"
```

### Task 9: Bridge Generated Cases Into Runtime Eval Execution

**Files:**
- Modify: `app/evals/langfuse_eval.py`
- Modify: `app/evals/runner.py`
- Modify: `scripts/run_evals.py`
- Test: `tests/test_eval_langfuse.py`

- [ ] **Step 1: Write failing runtime compatibility tests**

```python
def test_runtime_can_read_router_case_with_expected_agents():
    case = _build_case_from_dataset_item(item)
    assert case.expected_agents == ["hr-assistant"]
    assert case.auth_profile.employee_id == 1
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_eval_langfuse.py -v`
Expected: FAIL because runtime does not fully consume generated dataset structure

- [ ] **Step 3: Ensure runtime accepts generated dataset payloads**

```python
case = EvalCase(
    expected_agents=list(exp.get("expected_agents", [])),
    expected_tools=list(exp.get("expected_tools", [])),
)
```

- [ ] **Step 4: Ensure `scripts/run_evals.py` defaults to generated datasets**

```python
parser.add_argument("--dataset-name", default="mx-router-acceptance")
```

- [ ] **Step 5: Run compatibility tests**

Run: `uv run pytest tests/test_eval_langfuse.py tests/test_eval_executor.py -v`
Expected: PASS

- [ ] **Step 6: Commit**

```bash
git add app/evals/langfuse_eval.py app/evals/runner.py scripts/run_evals.py tests/test_eval_langfuse.py
git commit -m "feat: bridge generated eval datasets into runtime"
```

### Task 10: End-To-End Validation And Docs Sync

**Files:**
- Modify: `scripts/build_eval_datasets.py`
- Modify: `scripts/publish_eval_datasets.py`
- Test: `tests/test_eval_dataset_models.py`
- Test: `tests/test_eval_seed_inventory.py`
- Test: `tests/test_eval_generator.py`
- Test: `tests/test_eval_publisher.py`
- Test: `tests/test_eval_langfuse.py`

- [ ] **Step 1: Run targeted unit tests**

Run: `uv run pytest tests/test_eval_dataset_models.py tests/test_eval_seed_inventory.py tests/test_eval_generator.py tests/test_eval_publisher.py tests/test_eval_langfuse.py -v`
Expected: PASS

- [ ] **Step 2: Build datasets locally**

Run: `uv run python scripts/build_eval_datasets.py --output-dir /tmp/mx-agent-evals`
Expected: 生成 router/hr/it/admin/finance/legal/talent 的 `generated.yaml`

- [ ] **Step 3: Dry-run publish**

Run: `uv run python scripts/publish_eval_datasets.py --dry-run`
Expected: 打印待发布 dataset 数量与 case 数量，不写 Langfuse

- [ ] **Step 4: Real publish to Langfuse**

Run: `uv run python scripts/publish_eval_datasets.py`
Expected: 成功创建或更新 7 个 dataset

- [ ] **Step 5: Smoke-run router dataset**

Run: `uv run python scripts/run_evals.py --dataset-name mx-router-acceptance --limit 10 --auth-mode auto`
Expected: 输出 `run_name`、通过数、路由命中率

- [ ] **Step 6: Commit**

```bash
git add scripts/build_eval_datasets.py scripts/publish_eval_datasets.py
git commit -m "test: validate rebuilt eval dataset pipeline"
```

## Notes For Execution

- 优先先做 Router + HR 的最小闭环，再扩到其他 domain。
- 新增 YAML 体系后，不要继续往旧 Markdown 体系里加新 case。
- 如果发布脚本需要兼容旧 dataset，请保持旧脚本入口可用，但内部迁移到新生成链路。
- 运行验证统一使用 `uv run ...`，不要依赖系统级 `python` 或 `pytest`。
