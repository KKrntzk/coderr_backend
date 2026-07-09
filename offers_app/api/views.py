from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny
from rest_framework.pagination import PageNumberPagination
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Min

from offers_app.models import Offer
from offers_app.api.serializers import OfferListSerializer


class OfferPagination(PageNumberPagination):
    page_size = 6
    page_size_query_param = "page_size"


class OfferListView(ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = OfferListSerializer
    pagination_class = OfferPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ["title", "description"]
    ordering_fields = ["updated_at", "min_price"]
    ordering = ["-updated_at"]

    def get_queryset(self):
        queryset = Offer.objects.annotate(
            min_price=Min("details__price"),
            min_delivery_time=Min("details__delivery_time_in_days"),
        )

        creator_id = self.request.query_params.get("creator_id")
        if creator_id:
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
