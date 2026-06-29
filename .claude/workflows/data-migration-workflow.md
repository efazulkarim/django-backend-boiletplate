---
name: data-migration-workflow
description: Safe data migration pipeline — design → validate → migrate → verify → rollback-ready. Handles data transformations without data loss.
phases: [Design, Validate, Migrate, Verify, RollbackReady]
---

# data-migration-workflow pipeline

Invoke via `/schema-change` with a data migration description, or directly when transforming existing data.

## When to use this

- Backfilling a new column with computed values
- Merging or splitting existing data
- Migrating data between tables or services
- Normalizing existing data (emails to lowercase, phone number format)
- Populating a new table from existing data

Do NOT use for schema-only changes (adding columns/indexes) — use the standard `db-schema-change` workflow for that.

## Phase 1 — Design

**Goal**: plan the data migration with zero data loss guarantees.

- Read the current model and table structure.
- Determine:
  - Source: which table/columns contain the data
  - Target: where the data needs to go
  - Transform: what computation is needed
  - Volume: how many rows (run `SELECT COUNT(*)`)
  - Dependencies: what other code reads/writes this data
- Write the migration in two parts:
  1. **Schema migration**: add new column/table (nullable or with default)
  2. **Data migration**: `RunPython` to backfill/transform
- The `RunPython` function must:
  - Use `apps.get_model()` (never import models directly)
  - Process in batches (1000-5000 rows) to avoid locking
  - Log progress every batch
  - Be idempotent (safe to run twice)
  - Have a reverse function that's a no-op or safe undo

**Exit criteria**: migration file written, batch size determined, estimated time calculated.

## Phase 2 — Validate

**Goal**: test the migration on a subset before running on all data.

- Run `python manage.py sqlmigrate <app> <migration>` — verify SQL looks correct.
- Create a test with a small dataset (10-50 rows):
  ```python
  @pytest.mark.django_db
  def test_data_migration_forward():
      # Create test data in old format
      # Run migration
      # Assert data is in new format correctly
  ```
- Run the test. If it fails, fix the migration.
- Estimate total runtime based on test timing.

**Exit criteria**: test passes, SQL looks correct, runtime estimated.

## Phase 3 — Migrate

**Goal**: execute the data migration safely.

**Pre-flight checks:**
- Confirm you're on the right database (not production accidentally).
- Confirm the migration is reversible or has a backup.
- Confirm no other process is writing to the target table.

**Execution:**
```bash
# 1. Apply schema migration
python manage.py migrate <app>

# 2. Apply data migration (this runs RunPython)
python manage.py migrate <app>
```

**If the migration fails mid-way:**
- Do NOT retry blindly. Check how many rows were processed.
- The `RunPython` function should be idempotent — identify where it stopped.
- Resume from the last successful batch.

**Exit criteria**: migration applied, no errors.

## Phase 4 — Verify

**Goal**: confirm data integrity after migration.

- Run verification queries:
  ```sql
  -- Check for NULL values in the new column
  SELECT COUNT(*) FROM <table> WHERE <new_column> IS NULL;

  -- Check row counts match
  SELECT COUNT(*) FROM <source_table>;
  SELECT COUNT(*) FROM <target_table>;

  -- Spot-check random rows
  SELECT * FROM <table> ORDER BY RANDOM() LIMIT 10;
  ```
- Compare counts: source rows should equal target rows.
- Spot-check 10-20 random rows: old value → new value mapping is correct.
- Run the full test suite: `pytest -q --durations=10`.

**Exit criteria**: counts match, spot-checks correct, tests green.

## Phase 5 — RollbackReady

**Goal**: ensure we can undo if something goes wrong in production.

- Verify the reverse migration works:
  ```bash
  python manage.py migrate <app> <previous_migration>
  python manage.py migrate <app>
  ```
- Document the rollback procedure:
  1. `python manage.py migrate <app> <previous_migration>`
  2. Verify data is restored
  3. Redeploy previous code version
- If the data migration is not reversible (destructive transform), document:
  - What data would be lost
  - Whether a backup was taken
  - The manual recovery steps

**Exit criteria**: rollback tested (or documented as non-reversible with backup).

## On any phase failure

Stop. Report which phase failed and what the current state is. Do NOT auto-rollback. Provide:
- The exact migration file and line that failed
- How many rows were processed before failure
- Whether the database is in a consistent state
- The recommended recovery action

## Hard rules

- Never run data migrations on production without a backup.
- Never process all rows in a single transaction (use batches).
- Never skip the validation phase.
- Never make data migrations that are not idempotent.
- Never combine schema changes and data changes in the same migration file.
