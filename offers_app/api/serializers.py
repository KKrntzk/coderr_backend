from django.contrib.auth import get_user_model
from rest_framework import serializers

from offers_app.models import Feature, Offer, OfferDetail

User = get_user_model()


class OfferDetailMinimalSerializer(serializers.ModelSerializer):
    """Minimal representation of an offer detail: id and its resource URL."""

    url = serializers.SerializerMethodField()

    class Meta:
        model = OfferDetail
        fields = ["id", "url"]

    def get_url(self, obj):
        """Build the absolute API path to this offer detail."""
        return f"/api/offerdetails/{obj.id}/"


class UserDetailsSerializer(serializers.ModelSerializer):
    """Minimal user representation embedded in offer responses."""

    class Meta:
        model = User
        fields = ["first_name", "last_name", "username"]


class OfferListSerializer(serializers.ModelSerializer):
    """Serializer for listing offers, including computed price/delivery info."""

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
        """Return the lowest price among this offer's details."""
        prices = obj.details.values_list("price", flat=True)
        return min(prices) if prices else None

    def get_min_delivery_time(self, obj):
        """Return the shortest delivery time among this offer's details."""
        times = obj.details.values_list("delivery_time_in_days", flat=True)
        return min(times) if times else None


class OfferDetailCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating an offer detail, including its features."""

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
        """Return feature names as a flat list, for both model instances and raw data."""
        if isinstance(obj, OfferDetail):
            return list(obj.features.values_list("name", flat=True))
        return obj.get("features", [])

    def to_internal_value(self, data):
        """Keep the raw features list so create() can build Feature objects from it."""
        features = data.get("features", [])
        ret = super().to_internal_value(data)
        ret["features"] = features
        return ret


class OfferCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating an offer together with its three details."""

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
        """Ensure exactly one basic, one standard and one premium detail is provided."""
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
        """Create the offer, its details, and their features."""
        details_data = validated_data.pop("details")
        offer = Offer.objects.create(**validated_data)
        for detail_data in details_data:
            features_data = detail_data.pop("features")
            offer_detail = OfferDetail.objects.create(offer=offer, **detail_data)
            for feature_name in features_data:
                Feature.objects.create(offer_detail=offer_detail, name=feature_name)
        return offer


class OfferRetrieveSerializer(serializers.ModelSerializer):
    """Serializer for retrieving a single offer's details."""

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
        """Return the lowest price among this offer's details."""
        prices = obj.details.values_list("price", flat=True)
        return min(prices) if prices else None

    def get_min_delivery_time(self, obj):
        """Return the shortest delivery time among this offer's details."""
        times = obj.details.values_list("delivery_time_in_days", flat=True)
        return min(times) if times else None


class OfferDetailUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating a single offer detail, including its features."""

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
        """Return feature names as a flat list, for both model instances and raw data."""
        if isinstance(obj, OfferDetail):
            return list(obj.features.values_list("name", flat=True))
        return obj.get("features", [])

    def to_internal_value(self, data):
        """Keep the raw features list only when explicitly provided (partial update)."""
        features = data.get("features", None)
        ret = super().to_internal_value(data)
        if features is not None:
            ret["features"] = features
        return ret


class OfferUpdateSerializer(serializers.ModelSerializer):
    """Serializer for partially updating an offer and/or its details."""

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
        """Apply top-level field changes to the offer instance."""
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

    def _update_features(self, offer_detail, features_data):
        """Replace an offer detail's features with the given list of names."""
        if features_data is not None:
            offer_detail.features.all().delete()
            for feature_name in features_data:
                Feature.objects.create(offer_detail=offer_detail, name=feature_name)

    def _update_offer_detail(self, instance, detail_data):
        """Update the offer detail matching the given offer_type, if it exists."""
        offer_type = detail_data.get("offer_type")
        features_data = detail_data.pop("features", None)
        offer_detail = instance.details.filter(offer_type=offer_type).first()
        if offer_detail:
            for attr, value in detail_data.items():
                setattr(offer_detail, attr, value)
            offer_detail.save()
            self._update_features(offer_detail, features_data)

    def update(self, instance, validated_data):
        """Update the offer and any provided details, matched by offer_type."""
        details_data = validated_data.pop("details", None)
        self._update_offer_fields(instance, validated_data)
        if details_data:
            for detail_data in details_data:
                self._update_offer_detail(instance, detail_data)
        return instance

    def to_representation(self, instance):
        """Return the full offer with its details after an update."""
        return {
            "id": instance.id,
            "title": instance.title,
            "image": instance.image.url if instance.image else None,
            "description": instance.description,
            "details": OfferDetailUpdateSerializer(
                instance.details.all(), many=True
            ).data,
        }

    def validate_details(self, value):
        """Ensure every detail includes an offer_type to identify it."""
        for detail in value:
            if not detail.get("offer_type"):
                raise serializers.ValidationError(
                    "Each detail must include an offer_type."
                )
        return value
