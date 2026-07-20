from rest_framework import serializers

from offers_app.models import OfferDetail
from orders_app.models import Order


class OrderSerializer(serializers.ModelSerializer):
    """Read-only serializer exposing all fields of an order."""

    class Meta:
        model = Order
        fields = [
            "id",
            "customer_user",
            "business_user",
            "title",
            "revisions",
            "delivery_time_in_days",
            "price",
            "features",
            "offer_type",
            "status",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields


class OrderCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating an order from an offer detail's snapshot."""

    offer_detail_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Order
        fields = ["id", "offer_detail_id"]

    def create(self, validated_data):
        """Copy the offer detail's data into a new order for the requesting user."""
        offer_detail_id = validated_data.pop("offer_detail_id")
        offer_detail = OfferDetail.objects.get(id=offer_detail_id)
        request = self.context["request"]

        order = Order.objects.create(
            customer_user=request.user,
            business_user=offer_detail.offer.user,
            title=offer_detail.title,
            revisions=offer_detail.revisions,
            delivery_time_in_days=offer_detail.delivery_time_in_days,
            price=offer_detail.price,
            features=list(offer_detail.features.values_list("name", flat=True)),
            offer_type=offer_detail.offer_type,
        )
        return order

    def to_representation(self, instance):
        """Return the full order representation after creation."""
        return OrderSerializer(instance).data


class OrderStatusUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating only an order's status."""

    class Meta:
        model = Order
        fields = ["status"]

    def to_representation(self, instance):
        """Return the full order representation after the status update."""
        return OrderSerializer(instance).data
