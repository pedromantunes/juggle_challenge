from __future__ import annotations

from rest_framework import permissions


class IsOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.user.auth_user == request.user or (request.user.is_staff)


class OwnerFilterMixin:
    def get_queryset(self):
        queryset = super().get_queryset()
        if not self.request.user.is_anonymous:
            return queryset.filter(user__auth_user=self.request.user)


class OwnerUserFilterMixin:
    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(auth_user=self.request.user)
