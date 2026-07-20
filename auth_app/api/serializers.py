from django.contrib.auth import authenticate, get_user_model
from rest_framework import serializers

User = get_user_model()


class RegistrationSerializer(serializers.ModelSerializer):
    """Serializer for creating a new user (customer or business)."""

    repeated_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["username", "email", "password", "repeated_password", "type"]
        extra_kwargs = {
            "password": {"write_only": True},
            "email": {"required": True},
        }

    def validate(self, data):
        """Ensure password and repeated_password match."""
        if data["password"] != data["repeated_password"]:
            raise serializers.ValidationError(
                {"repeated_password": "Passwords do not match."}
            )
        return data

    def create(self, validated_data):
        """Create a new user with a securely hashed password."""
        validated_data.pop("repeated_password")
        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            password=validated_data["password"],
            type=validated_data["type"],
        )
        return user


class LoginSerializer(serializers.Serializer):
    """Serializer for authenticating a user via username and password."""

    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        """Authenticate the user and attach the user instance to the data."""
        user = authenticate(
            username=data["username"],
            password=data["password"],
        )
        if user is None:
            raise serializers.ValidationError({"detail": "Invalid credentials."})
        data["user"] = user
        return data
