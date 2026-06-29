# Redis Caching Skill

## When to cache

Cache when:
- Data is read-heavy, write-light (user profiles, config, lookups)
- Expensive queries that don't change per-request (aggregations, reports)
- Computed values that are stable for a window (TTL-based)

Do NOT cache when:
- Data changes on every request (real-time counters)
- Personalized data that can't be keyed by user (use user-scoped keys)
- The cache lookup cost exceeds the computation cost

## Django cache configuration

```python
# config/settings/base.py
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": os.environ.get("REDIS_URL", "redis://localhost:6379/0"),
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "SERIALIZER": "django_redis.serializers.json.JSONSerializer",
            "CONNECTION_POOL_KWARGS": {"max_connections": 50},
        },
        "KEY_PREFIX": "myapi",
        "TIMEOUT": 300,  # 5 minutes default
    },
    "sessions": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": os.environ.get("REDIS_SESSION_URL", "redis://localhost:6379/1"),
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        },
        "KEY_PREFIX": "session",
    },
}
```

## Cache key naming convention

```
<app>:<resource>:<id_or_filter>:<version>
```

Examples:
- `users:profile:42:v1`
- `api:ideas:list:page1:published:true:v1`
- `core:config:site_settings:v1`

## Low-level cache API

```python
from django.core.cache import cache


def get_user_profile(user_id: int) -> dict:
    cache_key = f"users:profile:{user_id}:v1"
    data = cache.get(cache_key)

    if data is None:
        User = apps.get_model("users", "User")
        user = User.objects.get(id=user_id)
        data = {"id": user.id, "email": user.email, "name": user.name}
        cache.set(cache_key, data, timeout=600)  # 10 minutes

    return data


def invalidate_user_profile(user_id: int) -> None:
    cache_key = f"users:profile:{user_id}:v1"
    cache.delete(cache_key)
```

## Cache-aside pattern in services

```python
# apps/<app>/services.py
from django.core.cache import cache
from django.apps import apps as django_apps


class IdeaService:
    CACHE_KEY_PREFIX = "api:ideas"
    CACHE_TTL = 300  # 5 minutes

    @classmethod
    def get_published_ideas(cls, page: int = 1, page_size: int = 20) -> dict:
        cache_key = f"{cls.CACHE_KEY_PREFIX}:list:page{page}:size{page_size}:v1"
        result = cache.get(cache_key)

        if result is None:
            Idea = django_apps.get_model("api", "Idea")
            queryset = Idea.objects.filter(
                is_deleted=False,
                status="published",
            ).select_related("author").order_by("-created_at")

            # ... pagination logic ...
            result = {  # type: ignore[assignment]
                "items": list(queryset.values("id", "title", "created_at")),
                "page": page,
                "page_size": page_size,
            }
            cache.set(cache_key, result, timeout=cls.CACHE_TTL)

        return result  # type: ignore[return-value]

    @classmethod
    def invalidate_idea_list(cls) -> None:
        """Invalidate all list caches for ideas."""
        # Pattern-based invalidation requires django-redis
        cache.delete_pattern(f"{cls.CACHE_KEY_PREFIX}:list:*:v1")

    @classmethod
    def invalidate_idea(cls, idea_id: int) -> None:
        cache.delete(f"{cls.CACHE_KEY_PREFIX}:detail:{idea_id}:v1")
        cls.invalidate_idea_list()
```

## Caching Django views

```python
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework.viewsets import ReadOnlyModelViewSet


class IdeaViewSet(ReadOnlyModelViewSet):
    @method_decorator(cache_page(60 * 5))  # 5 minutes
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @method_decorator(cache_page(60 * 10))  # 10 minutes
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
```

## Per-user caching

```python
from django.views.decorators.vary import vary_on_cookie, vary_on_headers


@method_decorator(vary_on_headers("Authorization"))
@method_decorator(cache_page(60 * 2))  # 2 minutes per user
def my_view(request):
    ...
```

## Testing cached code

```python
import pytest
from django.core.cache import cache


@pytest.mark.django_db
def test_get_user_profile_caches_result(user):
    """First call should hit DB, second should hit cache."""
    from apps.users.services import get_user_profile

    # Clear cache
    cache.clear()

    # First call — DB hit
    result1 = get_user_profile(user.id)

    # Mutate DB directly (bypass service)
    user.email = "changed@example.com"
    user.save(update_fields=["email"])

    # Second call — should return cached value
    result2 = get_user_profile(user.id)
    assert result2["email"] != "changed@example.com"

    # Invalidate and re-fetch
    from apps.users.services import invalidate_user_profile
    invalidate_user_profile(user.id)
    result3 = get_user_profile(user.id)
    assert result3["email"] == "changed@example.com"


@pytest.mark.django_db
def test_cache_invalidation_on_update(user):
    """Updating a user should invalidate its cache."""
    from apps.users.services import get_user_profile, invalidate_user_profile

    get_user_profile(user.id)
    invalidate_user_profile(user.id)

    assert cache.get(f"users:profile:{user.id}:v1") is None
```

## Cache warming

```python
# apps/core/management/commands/warm_cache.py
from django.core.management.base import BaseCommand
from django.apps import apps as django_apps


class Command(BaseCommand):
    help = "Warm frequently-accessed caches"

    def handle(self, *args, **options):
        from django.core.cache import cache

        # Warm site config
        SiteConfig = django_apps.get_model("core", "SiteConfig")
        config = SiteConfig.objects.first()
        if config:
            cache.set("core:config:site_settings:v1", config.to_dict(), timeout=3600)

        self.stdout.write(self.style.SUCCESS("Cache warmed"))
```

## Cache monitoring

```python
# In Django shell or management command
from django.core.cache import cache

# Get cache stats (requires django-redis)
cache_info = cache.client.get_client().info()
print(f"Keys: {cache_info['db0']['keys']}")
print(f"Memory: {cache_info['used_memory_human']}")
```

## Common pitfalls

1. **Cache stampede**: Use `cache.add()` for atomic set-if-not-exists
2. **Thundering herd**: Use a lock or `cache.get_or_set()` for expensive computations
3. **Stale data**: Always have an invalidation strategy before caching writes
4. **Cache size**: Monitor Redis memory; set `maxmemory-policy` to `allkeys-lru`
5. **Serialization**: Keep cached values JSON-serializable (no datetime objects)
