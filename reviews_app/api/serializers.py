from rest_framework import serializers

from reviews_app.models import Review


class ReviewSerializer(serializers.ModelSerializer):
    """Read-only serializer exposing all fields of a review."""

    class Meta:
        model = Review
        fields = [
            "id",
            "business_user",
            "reviewer",
            "rating",
            "description",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields


class ReviewCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating a review for a business user."""

    class Meta:
        model = Review
        fields = ["id", "business_user", "rating", "description"]

    def validate_business_user(self, value):
        """Ensure the review target is a business user."""
        if value.type != "business":
            raise serializers.ValidationError("This user is not a business user.")
        return value

    def validate(self, data):
        """Ensure the requesting user has not already reviewed this business user."""
        request = self.context["request"]
        if Review.objects.filter(
            business_user=data["business_user"], reviewer=request.user
        ).exists():
            raise serializers.ValidationError(
                "You have already reviewed this business user."
            )
        return data

    def create(self, validated_data):
        """Create the review with the requesting user as the reviewer."""
        request = self.context["request"]
        return Review.objects.create(reviewer=request.user, **validated_data)

    def to_representation(self, instance):
        """Return the full review representation after creation."""
        return ReviewSerializer(instance).data


class ReviewUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating only a review's rating and description."""

    class Meta:
        model = Review
        fields = ["rating", "description"]

    def to_representation(self, instance):
        """Return the full review representation after the update."""
        return ReviewSerializer(instance).data
