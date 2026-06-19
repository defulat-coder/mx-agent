# AGENTS.md

This file gives repository-wide guidance for coding agents. Subtree-specific
instructions live closer to the code and should be read before editing that
area.

## Project Overview

MX Agent is a monorepo for an enterprise AI assistant covering HR, IT,
administration, finance, legal, evaluation, and RAG knowledge workflows.

- Backend: FastAPI + Agno AgentOS + SQLAlchemy async SQLite + LanceDB +
  Langfuse/OpenTelemetry tracing. See `backend/AGENTS.md`.
- Frontend: Next.js 16 App Router + React 19 + TypeScript + Tailwind CSS v4 +
  shadcn/ui + pnpm. See `frontend/AGENTS.md`.
- Product specs and change records live under `openspec/`.
- Supporting docs and implementation plans live under `docs/`.
- Project-local Codex skills live under `.codex/skills/`.

## Repository Layout

- `backend/`: Python backend project.
- `frontend/`: Next.js frontend project.
- `openspec/`: active and archived OpenSpec changes plus accepted specs.
- `docs/`: project docs, eval guide, and implementation plans.
- `.codex/skills/`: project-local Codex skills.

## Specs And Docs

- Check `openspec/changes/` before changing behavior that appears to be covered
  by an active proposal.
- Update accepted specs under `openspec/specs/` when behavior changes the
  documented contract.
- Use `docs/` for supporting implementation notes, eval guidance, and plans that
  are not formal OpenSpec specs.

## Change Management

- Preserve unrelated worktree changes. This repository may have user changes in
  progress; do not reset, checkout, clean, or overwrite files unless explicitly
  requested.
- Keep edits scoped to the requested area.
- When touching both frontend and backend integration behavior, verify both
  sides and document any manual checks performed.
- Prefer small, focused commits with descriptive messages.

## Agent Skills

- Use the project skill `.codex/skills/chinese-commit-conventions` for any work
  involving commits, commit messages, changelogs, release notes, or commit
  convention configuration. This applies even when the user does not explicitly
  invoke `/chinese-commit-conventions`.
