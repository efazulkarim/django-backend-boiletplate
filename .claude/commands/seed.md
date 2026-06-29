---
description: Generate or reset test/development data. Seeds the database with realistic fixtures.
argument-hint: "[optional: app_name or 'reset']"
---

You are the data seeding assistant for this Django project. Follow this flow:

1. Parse the argument:
   - Empty → seed all apps with default data.
   - `reset` → flush and re-seed everything.
   - `<app_name>` → seed only that app.

2. Check for existing management commands:
   - Look for `apps/<app>/management/commands/seed_*.py`.
   - If found, run them in dependency order.

3. If no seed command exists, create one:
   - Use `apps.get_model()` to avoid import-time model access.
   - Use `factory_boy` if available, otherwise raw `Model.objects.create()`.
   - Generate realistic data (not "test1", "test2" — use fake names, emails, etc.).
   - Respect FK dependencies (create parent objects first).
   - Use `--count` argument for configurable batch sizes.

4. Run the seed command(s):
   ```bash
   python manage.py seed_<app> --count=50
   ```

5. Report: what was seeded, how many objects per model, any FK relationships created.

## Seed command template

```python
# apps/<app>/management/commands/seed_<app>.py
from django.core.management.base import BaseCommand
from django.apps import apps as django_apps


class Command(BaseCommand):
    help = "Seed <app> with development data"

    def add_arguments(self, parser):
        parser.add_argument("--count", type=int, default=20, help="Number of objects to create")
        parser.add_argument("--clear", action="store_true", help="Clear existing data first")

    def handle(self, *args, **options):
        count = options["count"]

        if options["clear"]:
            Model = django_apps.get_model("<app>", "<Model>")
            Model.objects.all().delete()
            self.stdout.write(self.style.WARNING("Cleared existing data"))

        # Create in dependency order
        User = django_apps.get_model("users", "User")
        users = []
        for i in range(count):
            user, _ = User.objects.get_or_create(
                email=f"user{i}@example.com",
                defaults={"name": f"User {i}"},
            )
            users.append(user)

        Idea = django_apps.get_model("api", "Idea")
        for i in range(count * 3):
            Idea.objects.get_or_create(
                title=f"Idea {i}",
                defaults={
                    "description": f"Description for idea {i}",
                    "author": users[i % len(users)],
                    "status": "published",
                },
            )

        self.stdout.write(self.style.SUCCESS(f"Seeded {count} users, {count * 3} ideas"))
```

Hard rules:

- Never seed production databases (check `settings.DEBUG` or `ENVIRONMENT`).
- Use `get_or_create` to be idempotent — running seed twice shouldn't duplicate data.
- Create objects in FK dependency order.
- Use `bulk_create` for large batches (>1000 objects) for performance.
