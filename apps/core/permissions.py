"""Reusable DRF permission classes."""
from rest_framework.permissions import BasePermission


class IsOwner(BasePermission):
    """Allow access only to the object's owner.

    Expects the view's object to have a `user` or `author` attribute
    that matches request.user.
    """

    def has_object_permission(self, request, view, obj):
        owner = getattr(obj, 'user', None) or getattr(obj, 'author', None)
        if owner is None:
            return False
        return owner == request.user


class IsAdmin(BasePermission):
    """Allow access only to admin/staff users."""

    def has_permission(self, request, view):
        return request.user and request.user.is_staff


class IsOwnerOrReadOnly(BasePermission):
    """Allow write access only to the owner; read access to all."""

    def has_object_permission(self, request, view, obj):
        if request.method in ('GET', 'HEAD', 'OPTIONS'):
            return True
        owner = getattr(obj, 'user', None) or getattr(obj, 'author', None)
        if owner is None:
            return False
        return owner == request.user
