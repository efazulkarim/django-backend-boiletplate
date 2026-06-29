---
name: performance-audit
description: Performance analysis pipeline — scan → measure → fix → verify. Finds N+1 queries, missing indexes, slow endpoints, and memory issues.
phases: [Scan, Measure, Fix, Verify]
---

# performance-audit pipeline

Invoke via `/performance-audit` or directly. Identifies and fixes performance bottlenecks.

## Phase 1 — Scan (subagent: `query-optimizer`)

**Goal**: identify all performance issues without measuring yet.

**Static analysis (no DB needed):**

1. **N+1 query detection:**
   - Search for `.all()` or `.filter()` in serializer `to_representation` methods
   - Search for attribute access on related objects in templates/serializers without `select_related` or `prefetch_related`
   - Search for loops that execute queries:
     ```python
     # BAD — N+1
     for idea in Idea.objects.all():
         print(idea.author.name)  # hits DB each time

     # GOOD — 2 queries
     for idea in Idea.objects.select_related("author").all():
         print(idea.author.name)
     ```

2. **Missing index detection:**
   - Search for `filter()`, `exclude()`, `order_by()` on fields without indexes
   - Check `Meta.indexes` in all models
   - Check for FK fields without `db_index=True`

3. **Serializer inefficiency:**
   - Search for `SerializerMethodField` that executes queries
   - Search for nested serializers without `select_related` in the view

4. **View-level issues:**
   - Search for `.count()` followed by `.all()` (two queries, should be one)
   - Search for `list()` on querysets that could be paginated
   - Search for unbounded querysets (no `[:N]` or pagination)

**Output**: list of issues with file:line, severity (HIGH/MEDIUM/LOW), and fix suggestion.

**Exit criteria**: all static issues identified.

## Phase 2 — Measure

**Goal**: quantify the actual impact of identified issues.

**For each HIGH/MEDIUM issue:**

1. **Count queries:**
   ```python
   from django.test.utils import override_settings
   from django.db import connection

   with override_settings(DEBUG=True):
       # ... execute the endpoint ...
       print(f"Queries: {len(connection.queries)}")
       for q in connection.queries:
           print(f"  {q['time']}s — {q['sql'][:100]}")
   ```

2. **EXPLAIN ANALYZE on slow queries:**
   ```sql
   EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT)
   SELECT * FROM api_idea WHERE status = 'published' ORDER BY created_at DESC;
   ```

3. **Benchmark endpoints:**
   ```bash
   # Using wrk or ab
   wrk -t4 -c100 -d10s http://localhost:8000/ideas/
   ```

4. **Memory profiling (if needed):**
   ```python
   import tracemalloc
   tracemalloc.start()
   # ... code ...
   current, peak = tracemalloc.get_traced_memory()
   print(f"Current: {current / 1024 / 1024:.1f}MB, Peak: {peak / 1024 / 1024:.1f}MB")
   ```

**Output**: measurements per issue — query count, query time, endpoint latency.

**Exit criteria**: every HIGH issue has a measurement.

## Phase 3 — Fix (subagent: `query-optimizer`)

**Goal**: apply fixes for all HIGH and MEDIUM issues.

**Fix patterns:**

1. **N+1 → select_related/prefetch_related:**
   ```python
   # Before
   queryset = Idea.objects.all()
   # After
   queryset = Idea.objects.select_related("author").prefetch_related("tags")
   ```

2. **Missing index:**
   ```python
   class Meta:
       indexes = [
           models.Index(fields=["status", "-created_at"]),
       ]
   ```

3. **Serializer query → annotated queryset:**
   ```python
   # Before: SerializerMethodField hits DB
   # After: annotate in the view
   queryset = Idea.objects.annotate(
       author_name=F("author__name"),
       tag_count=Count("tags"),
   )
   ```

4. **Unbounded queryset → pagination:**
   ```python
   # Before
   return Idea.objects.all()
   # After
   return Idea.objects.all()[:100]
   ```

5. **Count + list → single query:**
   ```python
   # Before
   count = queryset.count()
   items = list(queryset)
   # After
   items = list(queryset)
   count = len(items)  # or use pagination's count
   ```

For each fix:
- Apply the change
- Run `ruff check` — clean
- Run `pytest -q <related_tests>` — must pass
- Re-measure query count and latency

**Exit criteria**: all HIGH issues fixed, MEDIUM issues fixed or documented.

## Phase 4 — Verify (subagent: `query-optimizer`)

**Goal**: confirm improvements and catch regressions.

- Re-run the measurements from Phase 2.
- Compare before/after:
  ```
  Endpoint: GET /ideas/
  Before: 47 queries, 230ms avg
  After:  3 queries, 18ms avg
  Improvement: 93% fewer queries, 92% faster
  ```
- Run full test suite: `pytest -q --durations=10`.
- Run `mypy .` — types must still be clean.
- Document any issues that were NOT fixed (with justification).

**Exit criteria**: improvements measured and documented, tests green.

## On any phase failure

Stop. Report what failed and the current measurement state. If a fix causes a test to fail, revert the fix and report — don't modify tests to pass performance changes.

## What this workflow does NOT do

- Does not change business logic (only query patterns and indexes)
- Does not add caching (that's a separate concern, see `redis-caching` skill)
- Does not change API response shapes
- Does not add new dependencies
- Does not refactor code structure (that's `/refactor`)
