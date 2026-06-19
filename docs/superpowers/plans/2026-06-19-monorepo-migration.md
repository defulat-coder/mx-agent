# Monorepo Migration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Move the current Python backend into `backend/` and create a placeholder `frontend/` directory without changing backend behavior.

**Architecture:** The repository root becomes the monorepo coordination layer. `backend/` becomes the Python project root and owns `uv`, `app/`, backend scripts, backend tests, runtime data, logs, and backend environment files. `frontend/` is a documented placeholder only.

**Tech Stack:** Python 3.13, uv, FastAPI, Agno AgentOS, SQLite, Markdown documentation.

---

## Files And Responsibilities

- `backend/pyproject.toml`: backend Python project metadata and dependencies.
- `backend/uv.lock`: backend lockfile.
- `backend/main.py`: backend development entry point.
- `backend/app/`: backend application package, unchanged as `app`.
- `backend/scripts/`: backend maintenance and seed scripts.
- `backend/tests/`: backend test suite.
- `backend/evals/`: backend evaluation fixtures and datasets.
- `backend/.env.example`: backend environment template.
- `backend/.env`: local ignored backend environment file, moved if it exists.
- `backend/data/`: local ignored backend runtime databases and knowledge data, moved if it exists.
- `backend/log/`: local ignored backend logs, moved if it exists.
- `frontend/README.md`: placeholder frontend documentation.
- `.gitignore`: ignore backend-local virtualenv, data, logs, and env files.
- `README.md`: monorepo entrypoint and updated backend quick start.

## Task 1: Create Monorepo Directories And Move Backend Files

**Files:**
- Create: `backend/`
- Create: `frontend/`
- Move: `pyproject.toml` -> `backend/pyproject.toml`
- Move: `uv.lock` -> `backend/uv.lock`
- Move: `main.py` -> `backend/main.py`
- Move: `app/` -> `backend/app/`
- Move: `scripts/` -> `backend/scripts/`
- Move: `tests/` -> `backend/tests/`
- Move: `evals/` -> `backend/evals/`
- Move: `.env.example` -> `backend/.env.example`
- Move if present: `.env` -> `backend/.env`
- Move if present: `data/` -> `backend/data/`
- Move if present: `log/` -> `backend/log/`

- [ ] **Step 1: Create top-level monorepo directories**

Run from repository root:

```bash
mkdir -p backend frontend
```

Expected: `backend/` and `frontend/` exist.

- [ ] **Step 2: Move tracked backend project files with Git**

Run from repository root:

```bash
git mv pyproject.toml backend/pyproject.toml
git mv uv.lock backend/uv.lock
git mv main.py backend/main.py
git mv app backend/app
git mv scripts backend/scripts
git mv tests backend/tests
git mv evals backend/evals
git mv .env.example backend/.env.example
```

Expected: `git status --short` shows renames into `backend/` for these paths.

- [ ] **Step 3: Move ignored local backend runtime files without staging them**

Run from repository root:

```bash
test ! -f .env || mv .env backend/.env
test ! -d data || mv data backend/data
test ! -d log || mv log backend/log
```

Expected: existing local runtime files are under `backend/`; Git still treats them as ignored.

- [ ] **Step 4: Verify backend package imports from the new root**

Run from repository root:

```bash
cd backend
uv run python -c "from app.main import app; print(app.title)"
```

Expected: command exits 0 and prints `马喜智能助手`.

## Task 2: Update Ignore Rules For The Monorepo Layout

**Files:**
- Modify: `.gitignore`

- [ ] **Step 1: Replace root-only backend ignore rules with root and backend variants**

Edit `.gitignore` so the virtualenv, data, env, and log sections contain these rules:

```gitignore
# Virtual environments
.venv
backend/.venv

# Data (SQLite databases)
data/
backend/data/

# Environment variables
.env
backend/.env

# Logs
log/
backend/log/
```

Keep the existing Python, Cursor, and IDE ignore sections unchanged.

- [ ] **Step 2: Verify ignored backend runtime files are not staged**

Run from repository root:

```bash
git status --short --ignored backend/.env backend/data backend/log backend/.venv
```

Expected: ignored runtime files appear with `!!` when present and do not appear as staged or untracked files.

## Task 3: Create Frontend Placeholder

**Files:**
- Create: `frontend/README.md`

- [ ] **Step 1: Add placeholder README**

Create `frontend/README.md` with this content:

```markdown
# Frontend

This directory is reserved for the future frontend application.

No frontend framework, package manager, build tooling, or runtime has been selected yet. The current application is served by the backend AgentOS API in `../backend`.

When the frontend is added, document its setup, development server, environment variables, and backend API integration here.
```

- [ ] **Step 2: Verify frontend remains tooling-free**

Run from repository root:

```bash
find frontend -maxdepth 2 -type f -print
```

Expected output:

```text
frontend/README.md
```

## Task 4: Update Root README For Monorepo Usage

**Files:**
- Modify: `README.md`

- [ ] **Step 1: Update the project structure section**

Replace the current project structure code block that starts with `app/` with this monorepo-oriented block:

```markdown
```
.
├── backend/                 # FastAPI + Agno AgentOS 后端
│   ├── app/                 # 后端应用包
│   ├── scripts/             # 数据初始化、评测、维护脚本
│   ├── tests/               # 后端测试
│   ├── evals/               # 评测数据集
│   ├── data/                # 本地运行数据（被 Git 忽略）
│   ├── log/                 # 本地日志（被 Git 忽略）
│   ├── pyproject.toml       # 后端 Python 依赖
│   ├── uv.lock              # 后端 Python 锁文件
│   └── main.py              # 后端启动入口
├── frontend/                # 前端占位目录
│   └── README.md
├── docs/                    # 项目文档和实施计划
└── openspec/                # OpenSpec 需求和变更记录
```
```

- [ ] **Step 2: Update quick-start commands**

Replace the quick-start command block with:

```markdown
```bash
# 克隆后进入后端项目
cd backend

# 安装依赖
uv sync

# 配置环境变量
cp .env.example .env  # 按需修改

# 启动服务
uv run python main.py
```
```

Keep the line `服务默认运行在 `http://localhost:8000`。` after the command block.

- [ ] **Step 3: Check for stale root-level command references**

Run from repository root:

```bash
rg -n "uv run python main.py|uv sync|cp \\.env\\.example \\.env|app/main.py|pyproject.toml|uv.lock" README.md
```

Expected: any remaining references either point to `backend/` or are clearly describing files inside `backend/`.

## Task 5: Validate Backend From The New Location

**Files:**
- No source edits expected.

- [ ] **Step 1: Sync backend dependencies**

Run from repository root:

```bash
cd backend
uv sync
```

Expected: command exits 0.

- [ ] **Step 2: Verify imports and AgentOS route registration**

Run from repository root:

```bash
cd backend
uv run python - <<'PY'
from app.main import app

paths = {getattr(route, "path", None) for route in app.routes}
for required in ["/health", "/info", "/config", "/teams"]:
    assert required in paths, f"missing route: {required}"

print("routes ok")
PY
```

Expected: command prints `routes ok`.

- [ ] **Step 3: Start the backend for HTTP verification**

Run from repository root:

```bash
cd backend
uv run python main.py
```

Expected: backend starts on port 8000. Keep it running for the next step.

- [ ] **Step 4: Verify key HTTP endpoints from another shell**

Run from repository root in a separate shell:

```bash
for path in /health /info /config; do
  printf '\n### %s\n' "$path"
  curl -sS -i "http://127.0.0.1:8000$path" -H 'Origin: https://os.agno.com' | sed -n '1,20p'
done
```

Expected: each endpoint returns `HTTP/1.1 200 OK`, and the response headers include `access-control-allow-private-network: true`.

- [ ] **Step 5: Stop the backend process**

Press `Ctrl-C` in the shell running `uv run python main.py`.

Expected: backend exits cleanly.

## Task 6: Run Tests And Record Known Failures

**Files:**
- No source edits expected.

- [ ] **Step 1: Run the backend test suite**

Run from repository root:

```bash
cd backend
uv run pytest -q
```

Expected: the current suite may still show pre-existing failures unrelated to the monorepo move, including legacy `/v1/chat`, `/health` status expectations, database URL expectations, and historical absolute `/Users/cy/...` eval fixture paths.

- [ ] **Step 2: Verify migration-specific behavior even if legacy tests fail**

Run from repository root:

```bash
cd backend
uv run python -c "from app.main import app; print(any(getattr(r, 'path', None) == '/info' for r in app.routes))"
```

Expected output:

```text
True
```

## Task 7: Review Git Status

**Files:**
- No source edits expected.

- [ ] **Step 1: Review tracked changes**

Run from repository root:

```bash
git status --short
```

Expected tracked changes include:

- `R` or delete/add pairs for moved backend files under `backend/`
- `M .gitignore`
- `M README.md`
- `A frontend/README.md`
- existing modified backend files from prior work, now under `backend/`

Expected ignored local runtime files may include:

- `!! backend/.env`
- `!! backend/data/`
- `!! backend/log/`
- `!! backend/.venv/`

- [ ] **Step 2: Confirm repository root no longer contains backend project files**

Run from repository root:

```bash
test ! -d app
test ! -d scripts
test ! -d tests
test ! -d evals
test ! -f pyproject.toml
test ! -f uv.lock
test ! -f main.py
```

Expected: all commands exit 0.
