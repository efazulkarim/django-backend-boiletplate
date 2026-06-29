---
name: polar-payments
description: Polar SDK patterns for my-api-project. Use when modifying payment views, subscription services, or webhook handling. Covers checkout creation, webhook signature verification, and sandbox vs live toggle.
---

# Polar payments — `my-api-project`

## Files in scope

- `apps/<app>/views.py` — checkout creation, customer portal, webhook
- `apps/<app>/services/subscription_service.py` — tier mapping, entitlement checks
- `apps/<app>/services/subscription_config.py` — product IDs, feature flags per tier
- `config/settings/base.py` — `POLAR_ACCESS_TOKEN`, `POLAR_WEBHOOK_SECRET`, `POLAR_SANDBOX`

## Env keys

```text
POLAR_ACCESS_TOKEN=                 # required
POLAR_WEBHOOK_SECRET=               # required
POLAR_SANDBOX=true|false
POLAR_SUCCESS_URL=...
POLAR_SOLOPRENEUR_PRODUCT_ID=...
POLAR_ENTREPRENEUR_PRODUCT_ID=...
```

## SDK use

```python
from polar_sdk import Polar
from django.conf import settings


def get_polar_client() -> Polar:
    return Polar(
        access_token=settings.POLAR_ACCESS_TOKEN,
        server=settings.POLAR_SANDBOX and "sandbox" or "production",
    )
```

## Checkout (DRF view)

```python
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_checkout(request):
    polar = get_polar_client()
    session = await polar.checkouts.create(
        request=CreateCheckoutRequest(
            product_id=request.data["product_id"],
            success_url=settings.POLAR_SUCCESS_URL.format(CHECKOUT_ID="{CHECKOUT_ID}"),
            customer_email=request.user.email,
            metadata={"user_id": str(request.user.pk)},
        )
    )
    return Response({"url": session.url, "id": session.id}, status=status.HTTP_201_CREATED)
```

## Webhook signature

```python
import hmac
import hashlib
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status


@api_view(["POST"])
@permission_classes([AllowAny])
def polar_webhook(request):
    body = request.body
    sig = request.headers.get("webhook-signature", "")
    expected = hmac.new(
        settings.POLAR_WEBHOOK_SECRET.encode(),
        body,
        hashlib.sha256,
    ).hexdigest()
    if not hmac.compare_digest(sig, expected):
        return Response({"error": "Bad signature"}, status=status.HTTP_401_UNAUTHORIZED)
    event = request.data
    # dispatch on event["type"]
    handle_polar_event(event)
    return Response({"ok": True})
```

## Sandbox vs live

- `POLAR_SANDBOX=true` → SDK points at `https://sandbox-api.polar.sh`, no real cards.
- `POLAR_SANDBOX=false` → production.
- Local dev: `POLAR_SANDBOX=true`. CI: same.
- Production env var is set at deploy time; never commit it.

## Tier mapping (in `subscription_config.py`)

```python
from django.conf import settings

TIER_PRODUCTS = {
    "free": None,
    "solopreneur": settings.POLAR_SOLOPRENEUR_PRODUCT_ID,
    "entrepreneur": settings.POLAR_ENTREPRENEUR_PRODUCT_ID,
}

TIER_LIMITS = {
    "free": {"ideas": 3, "personas_per_idea": 2, "llm_calls_per_month": 50},
    "solopreneur": {"ideas": 25, "personas_per_idea": 5, "llm_calls_per_month": 1000},
    "entrepreneur": {"ideas": -1, "personas_per_idea": 10, "llm_calls_per_month": -1},
}
```

## Hard rules

- Webhook handler always verifies signature. Always.
- `POLAR_ACCESS_TOKEN` and `POLAR_WEBHOOK_SECRET` come from env, never logged.
- Sandbox mode in any non-prod env.
- Webhook returns 200 quickly; do heavy work in a background task (Celery).
- Always use `user_id` from the authenticated request, not from the request body.

## Don't do

- Don't trust the `customer_email` in webhook payload alone; reconcile with the user from `metadata.user_id`.
- Don't downgrade a user on `subscription.cancelled` immediately — wait for `subscription.period.ended`.
- Don't use the legacy `STRIPE_*` paths for new features; they're frozen.
