---
description: Run the security-review skill chain: scan → verify → report. Audit auth, secrets, CORS, rate limits, webhooks.
argument-hint: [optional path or glob]
---

You are invoking the **security-review** workflow. The workflow file is `.claude/workflows/security-review.md` — read it first, then execute its phases in order.

Argument: optional path/glob. If absent, audit the full repo.

Execution:

1. **Scan** — invoke the `security-auditor` subagent on the target. It produces a severity-tagged findings list.
2. **Verify** — cross-check findings against OWASP API Top 10 (2023). Drop false positives. Merge duplicates.
3. **Report** — output a single severity-grouped list. Include:
   - Total findings by severity.
   - Each finding: `file:line` + one-line problem + one-line fix.
   - For BLOCKER/MAJOR, the exact remediation (one snippet, ≤20 lines).
4. **Apply** — ask "Apply the BLOCKER + MAJOR fixes? (y/n)". On `y`, apply and re-run the scan.

Project rules enforced (from `.claude/rules/auth-security.md` and `security-and-hardening` skill):

- Webhook handlers always verify signature (Polar `webhook-signature`, Stripe `stripe-signature`).
- `SECRET_KEY` and provider keys come from env, never hardcoded.
- `os.environ` only in `config/settings/`, never in app code.
- CORS `allowed_origins` is an explicit list, not `*` in any non-dev env.
- `SecurityMiddleware` is first in `MIDDLEWARE`.
- DRF throttling is configured for auth endpoints.
- `AUTH_USER_MODEL` is set to a custom user model.

Do not run exploit code. This is static review.
