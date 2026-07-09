from rest_framework import serializers
from offers_app.models import Offer, OfferDetail
from django.contrib.auth import get_user_model

User = get_user_model()


class OfferDetailMinimalSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()

    class Meta:
        model = OfferDetail
        fields = ["id", "url"]

    def get_url(self, obj):
        return f"/api/offerdetails/{obj.id}/"


class UserDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "username"]


class OfferListSerializer(serializers.ModelSerializer):
    details = OfferDetailMinimalSerializer(many=True, read_only=True)
    user_details = UserDetailsSerializer(source="user", read_only=True)
    min_price = serializers.SerializerMethodField()
    min_delivery_time = serializers.SerializerMethodField()

    class Meta:
        model = Offer
        fields = [
            "id",
            "user",
            "title",
            "image",
            "description",
            "created_at",
            "updated_at",
            "details",
            "min_price",
            "min_delivery_time",
            "user_details",
        ]

    def get_min_price(self, obj):
        prices = obj.details.values_list("price", flat=True)
        return min(prices) if prices else None

    def get_min_delivery_time(self, obj):
        times = obj.details.values_list("delivery_time_in_days", flat=True)
        return min(times) if times else None
