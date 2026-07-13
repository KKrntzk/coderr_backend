from rest_framework.generics import ListAPIView, CreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import NotFound
from django.db.models import Q

from orders_app.models import Order
from orders_app.api.serializers import OrderSerializer, OrderCreateSerializer
from orders_app.api.permissions import IsCustomerUser
from offers_app.models import OfferDetail


class OrderListView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = OrderSerializer

    def get_queryset(self):
        user = self.request.user
        return Order.objects.filter(Q(customer_user=user) | Q(business_user=user))


class OrderCreateView(CreateAPIView):
    permission_classes = [IsAuthenticated, IsCustomerUser]
    serializer_class = OrderCreateSerializer

    def create(self, request, *args, **kwargs):
        offer_detail_id = request.data.get("offer_detail_id")
        if not offer_detail_id:
            return Response(
                {"detail": "offer_detail_id is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if not OfferDetail.objects.filter(id=offer_detail_id).exists():
            raise NotFound("OfferDetail not found.")
        return super().create(request, *args, **kwargs)
