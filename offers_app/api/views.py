from django.db.models import Min
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.exceptions import ValidationError
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.generics import (
    ListCreateAPIView,
    RetrieveAPIView,
    RetrieveUpdateDestroyAPIView,
)
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAuthenticated

from offers_app.api.permissions import IsBusinessUser, IsOfferOwner
from offers_app.api.serializers import (
    OfferCreateSerializer,
    OfferDetailCreateSerializer,
    OfferListSerializer,
    OfferRetrieveSerializer,
    OfferUpdateSerializer,
)
from offers_app.models import Offer, OfferDetail


class OfferPagination(PageNumberPagination):
    """Paginate offer lists with a fixed page size of 6."""

    page_size = 6
    page_size_query_param = "page_size"


class OfferListCreateView(ListCreateAPIView):
    """List all offers (public) or create a new offer (business users only)."""

    pagination_class = OfferPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ["title", "description"]
    ordering_fields = ["updated_at", "min_price"]
    ordering = ["-updated_at"]

    def get_permissions(self):
        """Restrict offer creation to business users; listing is public."""
        if self.request.method == "POST":
            return [IsBusinessUser()]
        return [AllowAny()]

    def get_serializer_class(self):
        """Use the create serializer for POST, the list serializer otherwise."""
        if self.request.method == "POST":
            return OfferCreateSerializer
        return OfferListSerializer

    def _filter_by_creator_id(self, queryset):
        """Filter offers by the creator's user id, if provided."""
        creator_id = self.request.query_params.get("creator_id")
        if not creator_id:
            return queryset
        try:
            return queryset.filter(user__id=int(creator_id))
        except ValueError:
            raise ValidationError({"creator_id": "Must be a valid integer."})

    def _filter_by_min_price(self, queryset):
        """Filter offers with a minimum price at or above the given value."""
        min_price = self.request.query_params.get("min_price")
        if not min_price:
            return queryset
        try:
            return queryset.filter(min_price__gte=float(min_price))
        except ValueError:
            raise ValidationError({"min_price": "Must be a valid number."})

    def _filter_by_max_delivery_time(self, queryset):
        """Filter offers with a minimum delivery time at or below the given value."""
        max_delivery_time = self.request.query_params.get("max_delivery_time")
        if not max_delivery_time:
            return queryset
        try:
            return queryset.filter(min_delivery_time__lte=int(max_delivery_time))
        except ValueError:
            raise ValidationError({"max_delivery_time": "Must be a valid integer."})

    def get_queryset(self):
        """Annotate offers with min price/delivery time and apply filters."""
        queryset = Offer.objects.annotate(
            min_price=Min("details__price"),
            min_delivery_time=Min("details__delivery_time_in_days"),
        )
        queryset = self._filter_by_creator_id(queryset)
        queryset = self._filter_by_min_price(queryset)
        queryset = self._filter_by_max_delivery_time(queryset)
        return queryset

    def perform_create(self, serializer):
        """Assign the requesting user as the owner of the new offer."""
        serializer.save(user=self.request.user)


class OfferRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    """Retrieve an offer, or update/delete it (owner only)."""

    http_method_names = ["get", "patch", "delete", "head", "options"]

    def get_permissions(self):
        """Restrict update and delete to the offer's owner."""
        if self.request.method in ["PATCH", "DELETE"]:
            return [IsAuthenticated(), IsOfferOwner()]
        return [IsAuthenticated()]

    def get_serializer_class(self):
        """Use the update serializer for PATCH, the retrieve serializer otherwise."""
        if self.request.method == "PATCH":
            return OfferUpdateSerializer
        return OfferRetrieveSerializer

    def get_queryset(self):
        """Annotate offers with their minimum price and delivery time."""
        return Offer.objects.annotate(
            min_price=Min("details__price"),
            min_delivery_time=Min("details__delivery_time_in_days"),
        )

    def get_object(self):
        """Fetch the offer and enforce object-level permissions."""
        obj = super().get_object()
        self.check_object_permissions(self.request, obj)
        return obj


class OfferDetailRetrieveView(RetrieveAPIView):
    """Retrieve a single offer detail by id."""

    permission_classes = [IsAuthenticated]
    serializer_class = OfferDetailCreateSerializer
    queryset = OfferDetail.objects.all()
