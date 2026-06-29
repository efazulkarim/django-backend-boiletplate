---
name: refactor-workflow
description: Safe refactoring pipeline — analyze → plan → refactor → test → verify. Preserves behavior while improving structure.
phases: [Analyze, Plan, Refactor, Test, Verify]
---

# refactor-workflow pipeline

Invoke directly or via `/refactor <target>`. Ensures refactoring never breaks existing behavior.

## Phase 1 — Analyze (subagent: `repo-reviewer`)

**Goal**: understand the current state before changing anything.

- Read the target file(s) or module.
- Identify all callers/consumers of the code being refactored.
- Read the existing tests for the target code.
- Map dependencies: what imports this? What does this import?
- Output: dependency graph, test coverage assessment, risk level (low/medium/high).

**Exit criteria**: dependency map present, risk level assigned.

## Phase 2 — Plan

**Goal**: define the refactoring steps with explicit safety checks.

- List each change as a discrete step (move function → extract class → rename → etc.).
- For each step, specify:
  - What changes
  - What MUST NOT change (behavior, API surface, response shapes)
  - Which tests validate this step
- Order steps from lowest risk to highest risk.
- If risk is HIGH, propose a feature flag or gradual migration path.

**Exit criteria**: plan confirmed by user. Each step has a test checkpoint.

## Phase 3 — Refactor

**Goal**: execute the plan one step at a time.

For each step in the plan:
1. Make the change.
2. Run `ruff check <changed_files>` — must be clean.
3. Run `mypy <changed_files>` — must be clean.
4. Run `pytest -q <related_tests> -x` — must pass.
5. If any check fails, revert that step and report.
6. Commit the step with message: `refactor(<scope>): <what changed>`

Do NOT batch all changes into one commit. Each logical step is its own commit.

**Exit criteria**: all steps applied, each step committed separately.

## Phase 4 — Test (subagent: `pytest-runner`)

**Goal**: prove the full test suite still passes.

- Run `pytest -q --durations=10` — full suite.
- If any test fails, identify which refactoring step caused it.
- Propose fix: either adjust the refactoring or update the test (if behavior intentionally changed).
- Run `ruff check .` and `mypy .` on the full project.

**Exit criteria**: full suite green, lint clean, types clean.

## Phase 5 — Verify (subagent: `repo-reviewer`)

**Goal**: confirm the refactoring achieved its goal without side effects.

- Review the full diff (all commits in the refactoring).
- Verify:
  - No behavior change (same inputs → same outputs)
  - No new dependencies introduced unnecessarily
  - No dead code left behind
  - No performance regression
  - Code is simpler/cleaner than before
- Report: summary of what changed, what didn't, quality improvement assessment.

**Exit criteria**: reviewer confirms no behavior change, quality improved.

## On any phase failure

Stop. Report which phase and which step failed. Do not auto-revert — let the user decide. Provide the specific commit hash where the failure occurred so they can `git reset --hard <hash>` if needed.

## What this workflow does NOT do

- Does not add new features (that's `/add-endpoint`)
- Does not change database schema (that's `/schema-change`)
- Does not change API contracts (those require deprecation paths)
- Does not optimize for performance (that's `/performance-audit`)
