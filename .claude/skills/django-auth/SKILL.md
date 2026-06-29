---
name: django-auth
description: Authentication patterns for my-api-project — DRF Token auth, django-allauth, session auth, and permissions. Use when modifying auth views, adding login/logout, or wiring OAuth.
---

# Django auth — `my-api-project`

## Files in scope

- `apps/users/models.py` — custom User model (email-based, no username)
- `apps/users/admin.py` — custom UserAdmin
- `apps/api/views.py` — `user_profile` endpoint
- `config/settings/base.py` — `AUTH_USER_MODEL`, `AUTHENTICATION_BACKENDS`, `REST_FRAMEWORK` auth classes
- `config/urls.py` — allauth URL mounting

## Auth methods

### DRF Token auth

```python
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate


@api_view(["POST"])
@permission_classes([AllowAny])
def login(request):
    email = request.data.get("email")
    password = request.data.get("password")
    user = authenticate(request, email=email, password=password)
    if user is None:
        return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)
    token, _ = Token.objects.get_or_create(user=user)
    return Response({"token": token.key, "user_id": user.pk, "email": user.email})


@api_view(["POST"])
def logout(request):
    request.user.auth_token.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)
```

### Session auth (django-allauth)

Allauth handles registration, login, logout, password reset, email verification, and social auth.

```python
# config/urls.py
urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("allauth.urls")),  # login, signup, password reset
    path("api/", include("apps.api.urls")),
    path("health/", include("apps.core.urls")),
]
```

### Protected views

```python
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def user_profile(request):
    user = request.user
    return Response({
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "is_staff": user.is_staff,
    })
```

## Custom permissions

```python
# apps/core/permissions.py
from rest_framework.permissions import BasePermission


class IsOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.created_by == request.user
```

## User model

```python
# apps/users/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    username = None
    email = models.EmailField(unique=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta:
        db_table = "users"
```

`AUTH_USER_MODEL = "users.User"` must be set in `config/settings/base.py`.

## Hard rules

- Use `settings.AUTH_USER_MODEL` for FKs, never `auth.User` directly.
- `request.user` is populated by DRF's authentication classes — don't decode JWTs manually.
- `IsAuthenticated` on every mutating endpoint. Don't read user from body.
- Return 401 for missing/invalid auth, 403 for insufficient permissions.
- Never log passwords (plain or hashed).
- Token auth: `rest_framework.authtoken.models.Token` — one token per user.
- Soft-deleted users cannot authenticate: check `is_active` (Django's built-in flag).

## Don't do

- Don't store passwords in plaintext — Django hashes with PBKDF2 by default.
- Don't use `@csrf_exempt` on API views — DRF handles CSRF via `SessionAuthentication`.
- Don't bypass `permission_classes` to "make it work" — fix the permission.
- Don't return 403 when the user isn't authenticated — that's 401.
- Don't create custom JWT auth unless there's a specific requirement — use DRF Token or allauth.
