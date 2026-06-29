---
name: drf-views
description: Django REST Framework view patterns for my-api-project. Use when adding a new API endpoint, creating a new ViewSet, or wiring a new resource into urls.py. Covers ViewSets, serializers, routers, and DRF conventions.
---

# DRF view patterns — `my-api-project`

## Files in scope

- `apps/<app>/views.py` — the views
- `apps/<app>/serializers.py` — request/response serializers
- `apps/<app>/urls.py` — URL routing
- `apps/<app>/services.py` — business logic (when the app grows)
- `config/urls.py` — root URL wiring

## Template ViewSet

```python
# apps/<app>/views.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import <Resource>
from .serializers import <Resource>Serializer, <Resource>CreateSerializer


class <Resource>ViewSet(viewsets.ModelViewSet):
    queryset = <Resource>.objects.filter(is_deleted=False)
    serializer_class = <Resource>Serializer
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == "create":
            return <Resource>CreateSerializer
        return <Resource>Serializer

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def perform_destroy(self, instance):
        """Soft delete instead of hard delete."""
        instance.is_deleted = True
        instance.save(update_fields=["is_deleted", "updated_at"])
```

## Template function-based view

```python
# apps/<app>/views.py
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def resource_list(request):
    resources = <Resource>.objects.filter(is_deleted=False)
    serializer = <Resource>Serializer(resources, many=True)
    return Response(serializer.data)
```

## URL registration

```python
# apps/<app>/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r"<resources>", views.<Resource>ViewSet, basename="<resource>")

urlpatterns = [
    path("", include(router.urls)),
]
```

```python
# config/urls.py — add to urlpatterns
path("api/", include("apps.<app>.urls")),
```

## Serializers

```python
# apps/<app>/serializers.py
from rest_framework import serializers
from .models import <Resource>


class <Resource>Serializer(serializers.ModelSerializer):
    class Meta:
        model = <Resource>
        fields = ["id", "name", "description", "created_at", "updated_at", "is_deleted"]
        read_only_fields = ["id", "created_at", "updated_at", "is_deleted"]


class <Resource>CreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = <Resource>
        fields = ["name", "description"]

    def validate_name(self, value):
        if len(value) > 200:
            raise serializers.ValidationError("Name must be 200 characters or fewer.")
        return value
```

## Service layer (for complex business logic)

```python
# apps/<app>/services.py
from .models import <Resource>


class <Resource>Service:
    @staticmethod
    def list_for_user(user, *, skip=0, limit=20):
        return (
            <Resource>.objects
            .filter(created_by=user, is_deleted=False)
            .order_by("-created_at")[skip:skip + limit]
        )

    @staticmethod
    def soft_delete(resource_id):
        resource = <Resource>.objects.get(id=resource_id)
        resource.is_deleted = True
        resource.save(update_fields=["is_deleted", "updated_at"])
```

## Conventions

- Plural noun paths, no verbs, no trailing slash mismatch.
- `serializer_class` on every ViewSet. Override `get_serializer_class()` for different actions.
- POST → 201, DELETE → 204 (override `perform_destroy` for soft delete).
- Auth via `permission_classes = [IsAuthenticated]`. Don't read user from body.
- Use `request.user` — DRF populates it from the token/session.
- Errors: raise `serializers.ValidationError` or return `Response({"error": "..."}, status=400)`.
- Never return `200` with an error body.

## Don't do

- Don't put complex business logic in views — use `services.py`.
- Don't call `serializer.save()` without handling `created_by` in `perform_create`.
- Don't use `delete()` on the queryset — use soft delete via `is_deleted`.
- Don't import models from other apps directly — use the service layer or explicit imports with a reason.
