# /sync-skills

Syncs all skills declared in `skills.json` against the project `.claude/skills/` directory.

**Usage:** Type `/sync-skills` in Claude Code.

**What it does:**
1. Reads `skills.json` from the project root
2. For `source: "local"` skills: checks if they exist in `./.claude/skills/<name>/`
3. For `source: "global"` skills: checks if they exist in `~/.claude/skills/<name>/`
4. If a global skill is missing, runs the `fallback` command (usually `skillsmith install`)
5. Reports synced, missing, and fetched skills

**Example output:**
```
Synced skills (14/14):
  django-migrations (local) - present
  drf-views (local) - present
  django-auth (local) - present
  llm-provider-fallback (local) - present
  neon-postgres (local) - present
  polar-payments (local) - present
  django-settings (local) - present
  pytest-django (local) - present
  django-models (local) - present
  stripe-payments (local) - present
  caveman (local) - present
  security-and-hardening (global) - present
  test-driven-development (global) - present
  commit (global) - present

Missing: 0
```

**If skills are missing:**
- Run `skillsmith install <skill-name>` (for global skills)
- Or copy the skill folder from a template repo into `./.claude/skills/`
- Or run `skillsmith author init <skill-name>` to create a new one from scratch

**To add a new skill to this project:**
1. Add the entry to `skills.json`
2. If local: create `./.claude/skills/<name>/SKILL.md`
3. If global: run `skillsmith install <name>` or ensure it's in `~/.claude/skills/`
4. Run `/sync-skills` to verify
