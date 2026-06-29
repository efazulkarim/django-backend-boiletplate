---
description: Run the add-endpoint skill chain: analyze → plan → build → test → review.
argument-hint: "<path method, e.g. 'POST /ideas/{id}/share'>"
---

You are invoking the **add-endpoint** workflow. The workflow file is `.claude/workflows/add-endpoint.md` — read it first, then execute its phases in order, using the subagents it names.

Argument: pass `<path method>` (e.g. `POST /ideas/{id}/share`, `GET /reports/{id}.pdf`).

Execution:

1. **Analyze** — invoke the `drf-view-builder` subagent. It reads sibling views, serializers, and the related service to extract the local style.
2. **Plan** — emit an endpoint spec: path, method, request serializer, response serializer, status codes, permission classes, service function signature, and test plan.
3. **Build** — the `drf-view-builder` writes the view, serializer, URL pattern, service, and tests. Run `ruff check` on the new files.
4. **Test** — invoke the `pytest-runner` subagent with the new test path.
5. **Review** — invoke the `repo-reviewer` subagent on the diff.

If any phase fails, stop and report. Do not proceed to the next phase on failure.

Project rules enforced (from `.claude/CLAUDE.md` and `.claude/rules/`):

- POST → 201, DELETE → 204, PATCH/PUT → 200.
- `serializer_class` on every view/viewset.
- `permission_classes = [IsAuthenticated]` on every mutating view.
- `Idempotency-Key` on every non-idempotent POST.
- No DB calls in views — call services instead.
- Serializers in `apps/<app>/serializers.py`, not in the view file.
- Service-layer test with `@pytest.mark.django_db`, integration test in `tests/`.
