---
name: stripe-payments
description: Stripe (legacy) patterns for my-api-project. Use when modifying Stripe payment views. Covers checkout, webhook signature, and idempotency keys. Note: Polar is the primary billing path; Stripe routes exist for back-compat.
---

# Stripe (legacy) — `my-api-project`

## Status

**Frozen.** New features go through Polar. Stripe routes stay for users who haven't migrated; bug fixes only.

## Files in scope

- `apps/<app>/views.py` — checkout, webhook
- `apps/<app>/services/subscription_service.py` — shared with Polar
- `config/settings/base.py` — `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET`, `STRIPE_PUBLISHABLE_KEY`

## Env keys

```text
STRIPE_SECRET_KEY=
STRIPE_WEBHOOK_SECRET=
STRIPE_PUBLISHABLE_KEY=
```

## Use

```python
import stripe
from django.conf import settings

stripe.api_key = settings.STRIPE_SECRET_KEY
```

## Checkout (DRF view)

```python
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_stripe_checkout(request):
    session = stripe.checkout.Session.create(
        mode="subscription",
        line_items=[{"price": request.data["price_id"], "quantity": 1}],
        success_url=request.data.get("success_url", "/"),
        cancel_url=request.data.get("cancel_url", "/"),
        customer_email=request.user.email,
        metadata={"user_id": str(request.user.pk)},
        idempotency_key=request.headers.get("Idempotency-Key"),
    )
    return Response({"url": session.url, "id": session.id}, status=status.HTTP_201_CREATED)
```

## Webhook

```python
@api_view(["POST"])
@permission_classes([AllowAny])
def stripe_webhook(request):
    body = request.body
    sig = request.headers.get("stripe-signature", "")
    try:
        event = stripe.Webhook.construct_event(body, sig, settings.STRIPE_WEBHOOK_SECRET)
    except (ValueError, stripe.error.SignatureVerificationError):
        return Response({"error": "Bad signature"}, status=status.HTTP_401_UNAUTHORIZED)
    # dispatch on event["type"]
    handle_stripe_event(event)
    return Response({"ok": True})
```

## Idempotency

Pass the `Idempotency-Key` header from the client straight to Stripe. Persist the key + session id so retries replay the same response.

## Hard rules

- Webhook always verifies signature. Always.
- `STRIPE_SECRET_KEY` and `STRIPE_WEBHOOK_SECRET` come from env, never logged.
- Use `user_id` from the authenticated request, not from the request body.
- Webhook returns 200 quickly; heavy work in background (Celery).

## Don't do

- Don't add new endpoints. If you need new billing behavior, route through Polar.
- Don't set `stripe.api_key` at module top level outside a function; keep it lazy.
- Don't mix Stripe and Polar entitlement logic; both feed the same `subscription_service` tier field.
