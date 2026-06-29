---
description: Create a safe, reversible Django migration. Accepts a short slug describing the change.
argument-hint: "<short slug, e.g. 'add_idea_priority'>"
---

You are the migration assistant for this Django project. Follow this flow:

1. Parse the slug from the argument. Refuse to proceed if it's empty or contains spaces.
2. Read `.claude/skills/django-migrations/SKILL.md` (or recall its rules).
3. Run `python manage.py makemigrations --dry-run` to preview what Django would generate.
4. Run `python manage.py makemigrations <app_label> -m "<slug>"`. **Do not** trust auto-generated output blindly — read the generated file.
5. Edit the migration file so that:
   - `dependencies` are correct.
   - New NOT NULL columns have a `default` or a two-step approach (add nullable → backfill → add NOT NULL).
   - New FKs come with an `index_together` or `AddIndex` in the same migration.
   - Data migrations use `RunPython` with `apps.get_model()` (never import models directly).
6. Run `python manage.py migrate`. If it fails, fix the migration, not the DB.
7. Run `python manage.py migrate <app_label> <previous_migration>` to reverse, then `python manage.py migrate` again. Both must succeed.
8. Update the matching model in the app's `models.py` to keep `makemigrations` consistent next time.
9. Add a `@pytest.mark.django_db` test in `tests/` that exercises the new column.
10. Report: migration file name, slug, what changed, up/down/up verified.

Hard rules:

- Never edit an applied migration; write a new one.
- Never drop a column on a populated table without a deprecation window.
- Never use `RunSQL` without `state_operations`.
- Use `apps.get_model()` inside `RunPython`, never import models directly.
