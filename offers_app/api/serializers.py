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


class OfferDetailUpdateSerializer(serializers.ModelSerializer):
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
        features = data.get("features", None)
        ret = super().to_internal_value(data)
        if features is not None:
            ret["features"] = features
        return ret


class OfferUpdateSerializer(serializers.ModelSerializer):
    details = OfferDetailUpdateSerializer(many=True, required=False)

    class Meta:
        model = Offer
        fields = [
            "id",
            "title",
            "image",
            "description",
            "details",
        ]

    def _update_offer_fields(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

    def _update_features(self, offer_detail, features_data):
        if features_data is not None:
            offer_detail.features.all().delete()
            for feature_name in features_data:
                Feature.objects.create(offer_detail=offer_detail, name=feature_name)

    def _update_offer_detail(self, instance, detail_data):
        offer_type = detail_data.get("offer_type")
        features_data = detail_data.pop("features", None)
        offer_detail = instance.details.filter(offer_type=offer_type).first()
        if offer_detail:
            for attr, value in detail_data.items():
                setattr(offer_detail, attr, value)
            offer_detail.save()
            self._update_features(offer_detail, features_data)

    def update(self, instance, validated_data):
        details_data = validated_data.pop("details", None)
        self._update_offer_fields(instance, validated_data)
        if details_data:
            for detail_data in details_data:
                self._update_offer_detail(instance, detail_data)
        return instance

    def to_representation(self, instance):
        return {
            "id": instance.id,
            "title": instance.title,
            "image": instance.image.url if instance.image else None,
            "description": instance.description,
            "details": OfferDetailUpdateSerializer(
                instance.details.all(), many=True
            ).data,
        }
