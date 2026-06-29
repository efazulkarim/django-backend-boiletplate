# PR description template

## Summary

<one-paragraph description of what this PR does and why>

## Changes

- <bullet per file or per logical change
- `<path>:<line>` — <what>

## API impact

- New endpoints: <list with paths, methods, status codes>
- Changed endpoints: <list with old → new behavior>
- Removed endpoints: <list, if any>
- Response shape changes: <list, if any>

## Test plan

- [ ] `pytest -q -m unit` passes
- [ ] `pytest -q -m database` passes
- [ ] `ruff check .` clean
- [ ] `mypy --strict` passes (if type-checking enabled)
- [ ] Manual test: <describe>

## Migrations

- [ ] New migration added: `<app>/migrations/NNNN_<slug>.py`
- [ ] `python manage.py migrate` ✓
- [ ] `python manage.py migrate <app> <previous>` ✓ (reverse)
- [ ] `python manage.py migrate` ✓ (round-trip)
- [ ] Model in `apps/<app>/models.py` updated

## Risks & rollout

- Backwards-incompatible? yes / no
- Feature flag needed? yes / no
- Rollback plan: <describe>

## Screenshots

(if UI-touching — usually N/A for this backend)
