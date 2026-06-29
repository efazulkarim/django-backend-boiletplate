# Commit message template

Conventional Commits. One logical change per commit.

## Subject

```
<type>(<scope>): <imperative summary, lowercase, no period, ≤72 chars>
```

`<type>` ∈ `feat`, `fix`, `chore`, `refactor`, `docs`, `test`, `perf`, `build`, `ci`.
`<scope>` ∈ `auth`, `view`, `serializer`, `model`, `service`, `llm`, `db`, `migration`, `settings`, `middleware`, `tests`, `docs`, `deps`, `ci`, or empty.

## Body (optional, wrap at 72)

Explain the *why*, not the *what*. Reference an issue id if there is one.

```
Previously, the LLM service lost token usage on transport errors
because the helper returned early. Move token_usage into the
fallback dict so we always have a number to bill against.

Refs: #123
```

## Trailer (mandatory)

```
Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>
```

## Examples

```
feat(llm): add Vultr as last-resort fallback
fix(auth): rotate refresh token jti on use
chore(deps): bump djangorestframework to 3.15.0
refactor(view): extract idempotency-key handling into mixin
test(service): cover idea soft-delete cascade
docs(readme): document the LLM provider priority chain
```
