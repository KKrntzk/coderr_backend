from rest_framework.generics import ListAPIView, CreateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Min
from rest_framework.generics import ListCreateAPIView, RetrieveAPIView


from offers_app.models import Offer
from offers_app.api.serializers import (
    OfferListSerializer,
    OfferCreateSerializer,
    OfferRetrieveSerializer,
)
from offers_app.api.permissions import IsBusinessUser


class OfferPagination(PageNumberPagination):
    page_size = 6
    page_size_query_param = "page_size"


class OfferListCreateView(ListCreateAPIView):
    pagination_class = OfferPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ["title", "description"]
    ordering_fields = ["updated_at", "min_price"]
    ordering = ["-updated_at"]

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsBusinessUser()]
        return [AllowAny()]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return OfferCreateSerializer
        return OfferListSerializer

    def get_queryset(self):
        queryset = Offer.objects.annotate(
            min_price=Min("details__price"),
            min_delivery_time=Min("details__delivery_time_in_days"),
        )

        creator_id = self.request.query_params.get("creator_id")
        if creator_id:
            try:
                creator_id = int(creator_id)
            except ValueError:
                from rest_framework.exceptions import ValidationError

                raise ValidationError({"creator_id": "Must be a valid integer."})
            queryset = queryset.filter(user__id=creator_id)

        min_price = self.request.query_params.get("min_price")
        if min_price:
            try:
                min_price = float(min_price)
            except ValueError:
                from rest_framework.exceptions import ValidationError

                raise ValidationError({"min_price": "Must be a valid number."})
            queryset = queryset.filter(min_price__gte=min_price)

        max_delivery_time = self.request.query_params.get("max_delivery_time")
        if max_delivery_time:
            try:
                max_delivery_time = int(max_delivery_time)
            except ValueError:
                from rest_framework.exceptions import ValidationError

                raise ValidationError({"max_delivery_time": "Must be a valid integer."})
            queryset = queryset.filter(min_delivery_time__lte=max_delivery_time)

        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class OfferRetrieveView(RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = OfferRetrieveSerializer

    def get_queryset(self):
        return Offer.objects.annotate(
            min_price=Min("details__price"),
            min_delivery_time=Min("details__delivery_time_in_days"),
        )
