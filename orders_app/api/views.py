from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import NotFound
from django.db.models import Q
from django.contrib.auth import get_user_model
from rest_framework.views import APIView

from orders_app.models import Order
from orders_app.api.serializers import (
    OrderSerializer,
    OrderCreateSerializer,
    OrderStatusUpdateSerializer,
)
from orders_app.api.permissions import IsCustomerUser, IsOrderBusinessOwner
from offers_app.models import OfferDetail

User = get_user_model()


class OrderListCreateView(ListCreateAPIView):
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAuthenticated(), IsCustomerUser()]
        return [IsAuthenticated()]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return OrderCreateSerializer
        return OrderSerializer

    def get_queryset(self):
        user = self.request.user
        return Order.objects.filter(Q(customer_user=user) | Q(business_user=user))

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


class OrderUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    http_method_names = ["patch", "delete", "head", "options"]
    queryset = Order.objects.all()

    def get_permissions(self):
        if self.request.method == "DELETE":
            return [IsAuthenticated(), IsAdminUser()]
        return [IsAuthenticated(), IsOrderBusinessOwner()]

    def get_serializer_class(self):
        return OrderStatusUpdateSerializer

    def get_object(self):
        obj = super().get_object()
        self.check_object_permissions(self.request, obj)
        return obj


class OrderCountView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, business_user_id):
        if not User.objects.filter(id=business_user_id, type="business").exists():
            raise NotFound("Business user not found.")

        count = Order.objects.filter(
            business_user_id=business_user_id,
            status="in_progress",
        ).count()

        return Response({"order_count": count})
