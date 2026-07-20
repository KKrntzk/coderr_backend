from rest_framework.permissions import BasePermission


class IsOwnProfile(BasePermission):
    """Allow access only to the profile's own user."""

    def has_object_permission(self, request, view, obj):
        """Check that the requested profile belongs to the requesting user."""
        return obj == request.user
