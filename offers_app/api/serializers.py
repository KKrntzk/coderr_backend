from rest_framework import serializers
from offers_app.models import Offer, OfferDetail, Feature
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


class FeatureSerializer(serializers.ListSerializer):
    child = serializers.CharField()


class OfferDetailCreateSerializer(serializers.ModelSerializer):
    features = serializers.SerializerMethodField()

    class Meta:
        model = OfferDetail
        fields = [
            "id",
            "title",
            "revisions",
            "delivery_time_in_days",
            "price",
            "features",
            "offer_type",
        ]

    def get_features(self, obj):
        if isinstance(obj, OfferDetail):
            return list(obj.features.values_list("name", flat=True))
        return obj.get("features", [])

    def to_internal_value(self, data):
        features = data.get("features", [])
        ret = super().to_internal_value(data)
        ret["features"] = features
        return ret


class OfferCreateSerializer(serializers.ModelSerializer):
    details = OfferDetailCreateSerializer(many=True)

    class Meta:
        model = Offer
        fields = [
            "id",
            "title",
            "image",
            "description",
            "details",
        ]

    def validate_details(self, value):
        if len(value) != 3:
            raise serializers.ValidationError(
                "An offer must contain exactly 3 details."
            )
        offer_types = [d["offer_type"] for d in value]
        if sorted(offer_types) != ["basic", "premium", "standard"]:
            raise serializers.ValidationError(
                "Details must contain basic, standard and premium."
            )
        return value

    def create(self, validated_data):
        details_data = validated_data.pop("details")
        offer = Offer.objects.create(**validated_data)
        for detail_data in details_data:
            features_data = detail_data.pop("features")
            offer_detail = OfferDetail.objects.create(offer=offer, **detail_data)
            for feature_name in features_data:
                Feature.objects.create(offer_detail=offer_detail, name=feature_name)
        return offer


class OfferRetrieveSerializer(serializers.ModelSerializer):
    details = OfferDetailMinimalSerializer(many=True, read_only=True)
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
        ]

    def get_min_price(self, obj):
        prices = obj.details.values_list("price", flat=True)
        return min(prices) if prices else None

    def get_min_delivery_time(self, obj):
        times = obj.details.values_list("delivery_time_in_days", flat=True)
        return min(times) if times else None
