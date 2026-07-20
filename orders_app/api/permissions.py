from rest_framework.permissions import BasePermission


class IsOrderBusinessOwner(BasePermission):
    """Allow access only to the business user assigned to the order."""

    def has_object_permission(self, request, view, obj):
        """Check that the requesting user is the order's business user."""
        return obj.business_user == request.user
