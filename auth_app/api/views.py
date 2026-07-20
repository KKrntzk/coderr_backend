from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from auth_app.api.serializers import LoginSerializer, RegistrationSerializer


def _build_auth_response(user, status_code):
    """Build the token response payload shared by registration and login."""
    token, _ = Token.objects.get_or_create(user=user)
    return Response(
        {
            "token": token.key,
            "username": user.username,
            "email": user.email,
            "user_id": user.id,
        },
        status=status_code,
    )


class RegistrationView(APIView):
    """Create a new user account and return an authentication token."""

    permission_classes = [AllowAny]

    def post(self, request):
        """Validate registration data and create the user."""
        serializer = RegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return _build_auth_response(user, status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    """Authenticate a user and return an authentication token."""

    permission_classes = [AllowAny]

    def post(self, request):
        """Validate credentials and authenticate the user."""
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data["user"]
            return _build_auth_response(user, status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
