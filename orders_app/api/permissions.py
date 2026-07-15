from rest_framework.permissions import BasePermission


class IsCustomerUser(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.type == "customer"


class IsOrderBusinessOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.business_user == request.user
