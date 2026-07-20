from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from profiles_app.api.permissions import IsOwnProfile
from profiles_app.api.serializers import (
    CustomerProfileListSerializer,
    ProfileListSerializer,
    ProfileSerializer,
)

User = get_user_model()


class ProfileDetailView(APIView):
    """Retrieve any user's profile, or update the requesting user's own profile."""

    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        """Restrict updates to the profile's own user."""
        if self.request.method == "PATCH":
            return [IsAuthenticated(), IsOwnProfile()]
        return [IsAuthenticated()]

    def get_object(self, pk):
        """Return the user with the given pk, or None if not found."""
        try:
            return User.objects.get(pk=pk)
        except User.DoesNotExist:
            return None

    def get(self, request, pk):
        """Return the profile data for the given user id."""
        user = self.get_object(pk)
        if user is None:
            return Response(
                {"detail": "Profile not found."}, status=status.HTTP_404_NOT_FOUND
            )
        serializer = ProfileSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, pk):
        """Partially update the profile, enforcing object-level permissions."""
        user = self.get_object(pk)
        if user is None:
            return Response(
                {"detail": "Profile not found."}, status=status.HTTP_404_NOT_FOUND
            )
        self.check_object_permissions(request, user)
        serializer = ProfileSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BusinessProfileListView(ListAPIView):
    """List all business user profiles."""

    permission_classes = [IsAuthenticated]
    serializer_class = ProfileListSerializer

    def get_queryset(self):
        """Return only users of type business."""
        return User.objects.filter(type=User.BUSINESS)


class CustomerProfileListView(ListAPIView):
    """List all customer user profiles."""

    permission_classes = [IsAuthenticated]
    serializer_class = CustomerProfileListSerializer

    def get_queryset(self):
        """Return only users of type customer."""
        return User.objects.filter(type=User.CUSTOMER)
