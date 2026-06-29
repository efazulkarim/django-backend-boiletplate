# Pagination Rules

## When to paginate

Every list endpoint MUST paginate. Never return an unbounded queryset to the client.

## Default pagination settings

```python
# config/settings/base.py
REST_FRAMEWORK = {
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 20,
    "MAX_PAGE_SIZE": 100,
}
```

## Response shape (page-number style)

```json
{
  "count": 142,
  "next": "http://localhost:8000/ideas/?page=3",
  "previous": "http://localhost:8000/ideas/?page=1",
  "results": [
    { "id": 1, "title": "..." },
    { "id": 2, "title": "..." }
  ]
}
```

## Custom pagination class

```python
# apps/<app>/pagination.py
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class StandardPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100

    def get_paginated_response(self, data):
        return Response({
            "count": self.page.paginator.count,
            "next": self.get_next_link(),
            "previous": self.get_previous_link(),
            "page_size": self.get_page_size(self.request),
            "results": data,
        })
```

## Using in views

```python
class IdeaViewSet(ModelViewSet):
    pagination_class = StandardPagination
    # ... or override per-action ...
```

## Cursor-based pagination (for real-time feeds)

Use cursor pagination when:
- Data changes frequently (new items added often)
- Users scroll infinitely (no "page 5" concept)
- Consistency matters more than random access

```python
from rest_framework.pagination import CursorPagination


class IdeaFeedPagination(CursorPagination):
    page_size = 20
    ordering = "-created_at"
    cursor_query_param = "cursor"
```

Response shape:
```json
{
  "next": "http://localhost:8000/ideas/?cursor=cD0yMDI2LTA2LTI5",
  "previous": null,
  "results": [...]
}
```

## Filtering + pagination

Always combine with `django-filter`:

```python
from django_filters.rest_framework import DjangoFilterBackend


class IdeaViewSet(ModelViewSet):
    pagination_class = StandardPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["status", "author"]
    search_fields = ["title", "description"]
    ordering_fields = ["created_at", "updated_at"]
    ordering = "-created_at"
```

## Caching paginated results

```python
from django.core.cache import cache


def get_ideas_page(page: int, page_size: int, filters: dict) -> dict:
    cache_key = f"api:ideas:list:p{page}:s{page_size}:{hash(frozenset(filters.items()))}:v1"
    result = cache.get(cache_key)
    if result is None:
        # ... query and paginate ...
        cache.set(cache_key, result, timeout=300)
    return result
```

## Testing pagination

```python
@pytest.mark.django_db
def test_ideas_list_paginated(auth_client, idea_factory):
    """List endpoint should return paginated results."""
    idea_factory.create_batch(25)

    response = auth_client.get("/ideas/")
    assert response.status_code == 200
    assert "count" in response.data
    assert "results" in response.data
    assert response.data["count"] == 25
    assert len(response.data["results"]) == 20  # default page_size


@pytest.mark.django_db
def test_ideas_list_custom_page_size(auth_client, idea_factory):
    """Should respect page_size query param."""
    idea_factory.create_batch(50)

    response = auth_client.get("/ideas/?page_size=10")
    assert response.status_code == 200
    assert len(response.data["results"]) == 10


@pytest.mark.django_db
def test_ideas_list_max_page_size(auth_client, idea_factory):
    """Should cap page_size at max_page_size."""
    idea_factory.create_batch(200)

    response = auth_client.get("/ideas/?page_size=500")
    assert response.status_code == 200
    assert len(response.data["results"]) <= 100
```
