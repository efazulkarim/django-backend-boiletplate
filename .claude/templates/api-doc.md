# API doc template

## `<METHOD> <path>`

### Summary

<one-line summary of what the endpoint does>

### Auth

`<none>` / `<user>` (i.e. `permission_classes = [IsAuthenticated]`) / `<admin>` / `<service>` (API key, etc.)

### Headers

| Header | Required | Notes |
|---|---|---|
| `Authorization` | yes (mutating routes) | `Token <key>` |
| `Idempotency-Key` | yes (non-idempotent POST) | UUID v4 recommended |
| `Content-Type` | yes (with body) | `application/json` |

### Path / query params

| Name | Type | Required | Notes |
|---|---|---|---|
| `<id>` | int | yes | path |

### Request body

```json
{
  "field": "value"
}
```

Serializer: `<Resource>CreateSerializer` in `apps/<app>/serializers.py`.

### Response — `<status>`

```json
{
  "id": 1,
  "field": "value",
  "created_at": "2026-06-10T12:00:00Z",
  "updated_at": "2026-06-10T12:00:00Z"
}
```

Serializer: `<Resource>Serializer` in `apps/<app>/serializers.py`.

### Error responses

| Status | When | Body shape |
|---|---|---|
| 401 | missing/invalid token | `{ "detail": "Invalid token." }` |
| 403 | wrong owner / tier | `{ "detail": "You do not have permission." }` |
| 404 | resource not found | `{ "detail": "Not found." }` |
| 400 | invalid body | `{ "field": ["This field is required."] }` |
| 429 | rate limited | `{ "detail": "Request was throttled." }` |
| 500 | unexpected | `{ "detail": "Internal server error." }` |

### Example

```bash
curl -X POST http://localhost:8000/<path> \
  -H "Authorization: Token $TOKEN" \
  -H "Content-Type: application/json" \
  -H "Idempotency-Key: $(uuidgen)" \
  -d '{"field": "value"}'
```
