from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from rest_framework.generics import ListAPIView

from profiles_app.api.serializers import (
    ProfileSerializer,
    ProfileListSerializer,
    CustomerProfileListSerializer,
)
from profiles_app.api.permissions import IsOwnProfile

User = get_user_model()


class ProfileDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.request.method == "PATCH":
            return [IsAuthenticated(), IsOwnProfile()]
        return [IsAuthenticated()]

    def get_object(self, pk):
        try:
            return User.objects.get(pk=pk)
        except User.DoesNotExist:
            return None

    def get(self, request, pk):
        user = self.get_object(pk)
        if user is None:
            return Response(
                {"detail": "Profile not found."}, status=status.HTTP_404_NOT_FOUND
            )
        serializer = ProfileSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, pk):
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
    permission_classes = [IsAuthenticated]
    serializer_class = ProfileListSerializer

    def get_queryset(self):
        return User.objects.filter(type=User.BUSINESS)


class CustomerProfileListView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CustomerProfileListSerializer

    def get_queryset(self):
        return User.objects.filter(type=User.CUSTOMER)
