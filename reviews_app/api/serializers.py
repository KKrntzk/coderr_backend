from rest_framework import serializers
from reviews_app.models import Review


class ReviewSerializer(serializers.ModelSerializer):
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
    class Meta:
        model = Review
        fields = ["id", "business_user", "rating", "description"]

    def validate_business_user(self, value):
        if value.type != "business":
            raise serializers.ValidationError("This user is not a business user.")
        return value

    def validate(self, data):
        request = self.context["request"]
        if Review.objects.filter(
            business_user=data["business_user"], reviewer=request.user
        ).exists():
            raise serializers.ValidationError(
                "You have already reviewed this business user."
            )
        return data

    def create(self, validated_data):
        request = self.context["request"]
        return Review.objects.create(reviewer=request.user, **validated_data)

    def to_representation(self, instance):
        return ReviewSerializer(instance).data


class ReviewUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ["rating", "description"]

    def to_representation(self, instance):
        return ReviewSerializer(instance).data
