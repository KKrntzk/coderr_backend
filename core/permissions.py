from rest_framework.permissions import BasePermission


class IsCustomerUser(BasePermission):
    """Allow access only to authenticated users with type 'customer'."""

    def has_permission(self, request, view):
        """Check that the requesting user is authenticated and a customer."""
        return request.user.is_authenticated and request.user.type == "customer"
