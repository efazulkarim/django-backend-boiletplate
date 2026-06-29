"""Reusable filter utilities and base filter backends."""
from django.db.models import Q
from rest_framework.filters import BaseFilterBackend


class OwnerFilterBackend(BaseFilterBackend):
    """Filter queryset to only include objects owned by the current user.

    Expects the model to have a `user` or `author` FK field.
    Only applies to non-staff users.
    """

    def filter_queryset(self, request, queryset, view):
        if request.user.is_staff:
            return queryset

        if hasattr(queryset.model, 'user'):
            return queryset.filter(user=request.user)
        if hasattr(queryset.model, 'author'):
            return queryset.filter(author=request.user)

        return queryset


def build_search_filter(search_fields: list[str], query: str) -> Q:
    """Build a Q object for searching across multiple fields.

    Args:
        search_fields: List of field lookups (e.g. ['title', 'description', 'author__email'])
        query: The search query string

    Returns:
        Q object combining all field lookups with OR
    """
    q = Q()
    if not query:
        return q

    for field in search_fields:
        q |= Q(**{f'{field}__icontains': query})

    return q
