from rest_framework.permissions import BasePermission


class IsReviewer(BasePermission):
    """Allow access only to the user who wrote the review."""

    def has_object_permission(self, request, view, obj):
        """Check that the requesting user is the review's author."""
        return obj.reviewer == request.user
