from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()


class ProfileSerializer(serializers.ModelSerializer):
    """Serializer for retrieving and updating a single user's profile."""

    user = serializers.IntegerField(source="id", read_only=True)
    created_at = serializers.DateTimeField(source="date_joined", read_only=True)

    class Meta:
        model = User
        fields = [
            "user",
            "username",
            "first_name",
            "last_name",
            "file",
            "location",
            "tel",
            "description",
            "working_hours",
            "type",
            "email",
            "created_at",
        ]
        extra_kwargs = {
            "username": {"read_only": True},
            "type": {"read_only": True},
        }


class ProfileListSerializer(serializers.ModelSerializer):
    """Serializer for listing business profiles."""

    user = serializers.IntegerField(source="id", read_only=True)

    class Meta:
        model = User
        fields = [
            "user",
            "username",
            "first_name",
            "last_name",
            "file",
            "location",
            "tel",
            "description",
            "working_hours",
            "type",
        ]


class CustomerProfileListSerializer(serializers.ModelSerializer):
    """Serializer for listing customer profiles."""

    user = serializers.IntegerField(source="id", read_only=True)

    class Meta:
        model = User
        fields = [
            "user",
            "username",
            "first_name",
            "last_name",
            "file",
            "uploaded_at",
            "type",
        ]
