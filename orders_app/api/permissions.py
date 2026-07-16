from rest_framework.permissions import BasePermission


class IsOrderBusinessOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.business_user == request.user
