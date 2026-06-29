---
paths:
  - "apps/*/migrations/**"
  - "apps/*/models.py"
---

# Database migration rules

These rules apply to Django migrations and Django models.

## Reversibility

- Every migration must be reversible. If `RunPython` is used, provide a reverse function or `migrations.RunPython.noop`.
- If a reverse is genuinely impossible (e.g., irreversible data transformation), say so in the PR description and get explicit reviewer sign-off.

## No destructive ops on populated tables

- Adding a `NOT NULL` column → provide a `default` or split into (a) add nullable, (b) backfill, (c) set NOT NULL.
- Dropping a column → deprecate in code first, then drop in a later migration. Two-step.
- Changing a type → add new column, backfill, switch, drop old.
- Truncate / drop table → never in a migration.

## Indexes

- Every new FK gets `db_index=True` on the field.
- Every new column used in `WHERE` or `ORDER BY` gets an index.
- Composite indexes: name `ix_<table>_<col1>_<col2>`. Add to `Meta.indexes`.
- Don't add indexes that duplicate an existing FK index.

## Constraints

- Unique constraints get a matching unique index.
- Foreign keys: explicit `on_delete` (`CASCADE` for owned children, `SET_NULL` for optional links).
- Don't use `PROTECT` for owned children; it blocks parent deletion.

## Data migrations

- `RunPython` is a data migration. Put it in a separate migration file from schema changes.
- One migration = one schema change. One migration = one data backfill. Never mix.
- Use `apps.get_model()` inside `RunPython`, never import models directly.

## Model sync

- The model in `apps/<app>/models.py` MUST be updated alongside the migration.
- Field names in serializer = field names in model. No renaming.
- `db_table` explicitly set for non-auth models.

## History

- Never edit an applied migration. Write a new one.
- Use sequential, descriptive names. Don't reuse migration names.

## Don't

- Don't disable FK checks.
- Don't import models inside `RunPython`. Use `apps.get_model()`.
- Don't drop data without a deprecation window.
