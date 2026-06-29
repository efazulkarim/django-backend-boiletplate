---
name: add-endpoint
description: Multi-agent pipeline to add a new DRF endpoint — analyze → plan → build → test → review. Stops on any phase failure.
phases: [Analyze, Plan, Build, Test, Review]
---

# add-endpoint workflow

Invoke via `/add-endpoint <path method>`. This is a deterministic pipeline; do not skip phases.

## Phase 1 — Analyze (subagent: `drf-view-builder`)

**Goal**: extract the local style so the new endpoint matches.

- Read 1-2 sibling views from `apps/*/views.py`.
- Read the related service in `apps/*/services.py`.
- Read the relevant serializer in `apps/*/serializers.py`.
- Read the URL conf in `apps/*/urls.py`.
- Output a short style report: signature shape, error pattern, status codes, test fixture names.

**Exit criteria**: style report present.

## Phase 2 — Plan

**Goal**: produce a concrete endpoint spec, no code yet.

- Path and method.
- Path params and query params.
- Request serializer (or `None`).
- Response serializer and `status_code`.
- Permission classes.
- Idempotency-Key requirement (yes for non-idempotent POST, no otherwise).
- Service function signature (no DB in view, remember).
- Test plan: which test file, what cases.
- Stop and ask the user if the spec is ambiguous.

**Exit criteria**: spec confirmed by the user.

## Phase 3 — Build (subagent: `drf-view-builder`)

**Goal**: write the code.

- Add request/response serializers to `apps/*/serializers.py` (extend, don't fork).
- Add or extend the service method in `apps/*/services.py`.
- Add the view to the appropriate `apps/*/views.py`.
- Register the URL in `apps/*/urls.py`.
- Write `tests/test_<resource>.py` for the service and API.
- Run `ruff check <new_files>` and fix what's safe.

**Exit criteria**: files added, ruff clean, working tree staged or unstaged.

## Phase 4 — Test (subagent: `pytest-runner`)

**Goal**: prove the new code works.

- Run `pytest -q tests/test_<resource>.py -x` first (fast).
- Then `pytest -q tests/test_<resource>.py -x --reuse-db` (DB).
- Capture failure tail and propose fixes.
- Do not modify the new code to make tests pass without telling the user.

**Exit criteria**: green, OR a clear failure with a fix proposal.

## Phase 5 — Review (subagent: `repo-reviewer`)

**Goal**: enforce project conventions on the new code.

- Run the reviewer on the diff (`git diff` against the last commit, or staged).
- Group findings by severity (BLOCKER > MAJOR > MINOR).
- Apply BLOCKER + MAJOR fixes; surface MINOR for the user.
- Re-run lint + tests after applying.

**Exit criteria**: no BLOCKER, no MAJOR, tests green.

## On any phase failure

Stop the pipeline. Report which phase failed and why. Do not roll back changes — let the user decide. Do not auto-proceed.
