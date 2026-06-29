---
name: test-driven-development
description: TDD workflow adapted to Django + DRF in my-api-project. Use when adding a new endpoint, service method, or business rule. Red → Green → Refactor, with the project's test layout and markers.
---

# TDD — `my-api-project`

## Cycle

1. **Red** — write the smallest failing test for the new behavior.
2. **Green** — write the minimum code to make it pass.
3. **Refactor** — clean up, keep tests green.

## Layout reminder

- Model tests → `tests/test_<model>.py`, marked `@pytest.mark.django_db`.
- View tests → `tests/test_<resource>.py`, marked `@pytest.mark.django_db`.
- Service tests → `tests/test_<service>.py`, marked `@pytest.mark.django_db`.
- External-touching tests → mock with `unittest.mock.patch`, marked `@pytest.mark.external`.

## Recipe: add a new endpoint

1. **Red (model)** — write a test that creates the model instance. Don't define the model yet; let the import fail.
2. **Green (model)** — add the model to `apps/<app>/models.py` minimally. Generate migration. Test passes.
3. **Red (serializer)** — write a test that validates input/output with the serializer. Let the import fail.
4. **Green (serializer)** — add the serializer to `apps/<app>/serializers.py`. Test passes.
5. **Red (view)** — write a view test using `APIClient` + `auth_client`. Assert status code + response shape.
6. **Green (view)** — add the view in `apps/<app>/views.py`. Wire URL in `apps/<app>/urls.py`. Test passes.
7. **Refactor** — extract repeated code; tighten types; check the layered rule is intact (no complex logic in views).

## Recipe: add a new model field

1. **Red (model)** — model test: create instance, assert the field exists and has the right default.
2. **Green (model)** — add the field to `apps/<app>/models.py`. Make it nullable OR give a `default`.
3. **Red (migration)** — run `python manage.py makemigrations`. Verify the migration file. Run `migrate`.
4. **Green (migration)** — the test for the model is now actually exercised against the migrated schema.
5. **Refactor** — update serializer, view, service if needed.

## Recipe: add a new Celery task

1. **Red (task)** — write a test that calls the task with `CELERY_TASK_ALWAYS_EAGER=True`. Assert the side effect.
2. **Green (task)** — add the task in `apps/<app>/tasks.py`. Test passes.
3. **Refactor** — add error handling, logging, retry logic.

## What "minimum" means here

- Don't add error handling for cases the code can't reach yet.
- Don't add type hints to every local variable; annotate public API only.
- Don't write a docstring for a one-line function.
- Don't pre-optimize.

## When to break the cycle

- A bug in a third-party SDK — write a regression test, then patch the wrapper, not the SDK.
- A perf issue — write a failing perf test if you can, then optimize.
- A security finding — fix the line, write a test that would have caught the regression, then move on.

## Don't do

- Don't write the implementation first, "to get the shape right," then write tests. The test tells you the shape.
- Don't skip refactor because "the test passes." Refactor is part of green.
- Don't disable a failing test to merge. Fix or delete it.
