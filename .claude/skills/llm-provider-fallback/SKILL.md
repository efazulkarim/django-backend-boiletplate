---
name: llm-provider-fallback
description: Multi-provider LLM routing for my-api-project. Use when adding a new LLM provider, fixing provider-specific bugs, or adjusting the priority chain. Priority: OpenRouter > ApiFreeLLM > GLM > Vultr.
---

# LLM provider fallback — `my-api-project`

## Priority chain (immutable order)

```text
OpenRouter  >  ApiFreeLLM  >  GLM  >  Vultr
```

A new provider slots in at a specific position. The order is product, not technical: OpenRouter is the production default; ApiFreeLLM is the free-tier backup; GLM and Vultr are the last-resort fallbacks.

## How selection works

```python
# apps/<app>/services/llm_service.py — selection at module load
USE_OPENROUTER = bool(settings.OPENROUTER_API_KEY)
USE_APIFREELL = not USE_OPENROUTER and bool(settings.APIFREELL_API_KEY)
USE_GLM = not USE_OPENROUTER and not USE_APIFREELL and bool(settings.GLM_API_KEY)
USE_VULTR = not any([USE_OPENROUTER, USE_APIFREELL, USE_GLM])

if USE_OPENROUTER:
    ACTIVE_API_KEY = settings.OPENROUTER_API_KEY
    ACTIVE_API_BASE_URL = settings.OPENROUTER_API_BASE_URL
    ACTIVE_CHAT_MODEL = settings.OPENROUTER_CHAT_MODEL
    PROVIDER_NAME = "OpenRouter"
# ... etc
```

Selection is at module load. There is **no per-request fallback**: if the active provider fails, the request fails.

## Provider matrix

| Provider     | base URL                                | stream    | response_format json_object | max_tokens default |
|--------------|-----------------------------------------|-----------|-----------------------------|--------------------|
| OpenRouter   | `https://openrouter.ai/api/v1`          | optional  | supported                   | caller decides     |
| ApiFreeLLM   | `https://api.apifreellm.com/v1`         | optional  | unsupported                 | caller decides     |
| GLM          | `https://api.z.ai/api/coding/paas/v4`   | optional  | partial                     | 2048 injected      |
| Vultr        | `https://api.vultrinference.com/v1`     | optional  | unsupported                 | caller decides     |

## Request shape (unified)

```python
import httpx

request_payload = {
    "model": ACTIVE_CHAT_MODEL,
    "messages": [...],
    "temperature": 0.5,
    "stream": False,
}
if USE_GLM:
    request_payload["max_tokens"] = request_payload.get("max_tokens", 2048)

response = httpx.post(
    f"{ACTIVE_API_BASE_URL}/chat/completions",
    json=request_payload,
    headers={"Authorization": f"Bearer {ACTIVE_API_KEY}"},
    timeout=60,
)
```

## Response extraction (unified)

```python
content = response.json().get("choices", [{}])[0].get("message", {}).get("content", "")
# Robust JSON extraction: first '{' to last '}'
start = content.find("{")
end = content.rfind("}")
if start == -1 or end == -1 or end <= start:
    raise ValueError("No JSON object in response")
analysis = json.loads(content[start : end + 1])
```

## Error shape (contract)

Every error path returns the full key set:

```python
{
    "error": str,
    "insight": str,
    "recommendations": list[str],
    "score": int,
    "reasoning": str,
    "overview": str,
    "strategic_next_steps": list[str],
    "key_strengths": list[str],
    "key_challenges": list[str],
}
```

## Settings

```python
# config/settings/base.py
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")
OPENROUTER_CHAT_MODEL = os.environ.get("OPENROUTER_CHAT_MODEL", "deepseek/deepseek-r1-distill-llama-70b")
APIFREELL_API_KEY = os.environ.get("APIFREELL_API_KEY", "")
APIFREELL_CHAT_MODEL = os.environ.get("APIFREELL_CHAT_MODEL", "deepseek-r1-distill-llama-70b")
GLM_API_KEY = os.environ.get("GLM_API_KEY", "")
GLM_CHAT_MODEL = os.environ.get("GLM_CHAT_MODEL", "glm-4.5")
VULTR_API_KEY = os.environ.get("VULTR_API_KEY", "")
```

## Adding a new provider (checklist)

1. **Env keys** in `config/settings/base.py`: `<P>_API_KEY`, `<P>_CHAT_MODEL`.
2. **`.env.example`** with the new keys + a comment.
3. **Provider block** in the LLM service (URLs, defaults).
4. **Priority chain** — pick a position. Default: above Vultr (the last-resort).
5. **`USE_<P>` flag** and if/elif cascade. Order must match the priority chain.
6. **`PROVIDER_NAME`** and `ACTIVE_*` triple.
7. **Early-return** for missing key — name the right env key in the error.
8. **Mock fixture** in `tests/` using `unittest.mock.patch`.
9. **Run the full pytest suite** — must not regress existing providers.

## Don't do

- Don't change the priority order without a product call.
- Don't remove or rename keys in the error response.
- Don't switch to SSE / streaming on these endpoints.
- Don't log the API key (not even truncated).
- Don't add a third-party framework (LangChain, LlamaIndex). Use raw `httpx`.
- Don't add per-request fallback — module-load selection only.
- Don't change temperature defaults without measuring output quality.
