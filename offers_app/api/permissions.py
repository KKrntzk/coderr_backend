from rest_framework.permissions import BasePermission


class IsBusinessUser(BasePermission):
    """Allow access only to authenticated users with type 'business'."""

    def has_permission(self, request, view):
        """Check that the requesting user is authenticated and a business user."""
        return request.user.is_authenticated and request.user.type == "business"


class IsOfferOwner(BasePermission):
    """Allow access only to the user who created the offer."""

    def has_object_permission(self, request, view, obj):
        """Check that the requesting user is the owner of the offer."""
        return obj.user == request.user
