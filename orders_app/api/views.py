from django.contrib.auth import get_user_model
from django.db.models import Q
from rest_framework import status
from rest_framework.exceptions import NotFound
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from core.permissions import IsCustomerUser
from offers_app.models import OfferDetail
from orders_app.api.permissions import IsOrderBusinessOwner
from orders_app.api.serializers import (
    OrderCreateSerializer,
    OrderSerializer,
    OrderStatusUpdateSerializer,
)
from orders_app.models import Order

User = get_user_model()


def _get_business_user_or_404(business_user_id):
    """Raise a 404 unless the given id belongs to a business user."""
    if not User.objects.filter(id=business_user_id, type="business").exists():
        raise NotFound("Business user not found.")


class OrderListCreateView(ListCreateAPIView):
    """List the requesting user's orders, or create a new order (customers only)."""

    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        """Restrict order creation to customers."""
        if self.request.method == "POST":
            return [IsAuthenticated(), IsCustomerUser()]
        return [IsAuthenticated()]

    def get_serializer_class(self):
        """Use the create serializer for POST, the read serializer otherwise."""
        if self.request.method == "POST":
            return OrderCreateSerializer
        return OrderSerializer

    def get_queryset(self):
        """Return orders where the user is either the customer or the business."""
        user = self.request.user
        return Order.objects.filter(Q(customer_user=user) | Q(business_user=user))

    def _validate_offer_detail_id(self, request):
        """Return a 400 response if offer_detail_id is missing or not an integer."""
        offer_detail_id = request.data.get("offer_detail_id")
        if not offer_detail_id:
            return Response(
                {"detail": "offer_detail_id is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            int(offer_detail_id)
        except (ValueError, TypeError):
            return Response(
                {"offer_detail_id": "Must be a valid integer."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return None

    def create(self, request, *args, **kwargs):
        """Validate offer_detail_id, then delegate to the default create flow."""
        error_response = self._validate_offer_detail_id(request)
        if error_response:
            return error_response
        offer_detail_id = int(request.data.get("offer_detail_id"))
        if not OfferDetail.objects.filter(id=offer_detail_id).exists():
            raise NotFound("OfferDetail not found.")
        return super().create(request, *args, **kwargs)


class OrderUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    """Update an order's status (business owner only) or delete it (admin only)."""

    http_method_names = ["patch", "delete", "head", "options"]
    queryset = Order.objects.all()

    def get_permissions(self):
        """Restrict deletion to admins; status updates to the order's business owner."""
        if self.request.method == "DELETE":
            return [IsAuthenticated(), IsAdminUser()]
        return [IsAuthenticated(), IsOrderBusinessOwner()]

    def get_serializer_class(self):
        """Only the status field is editable via this endpoint."""
        return OrderStatusUpdateSerializer

    def get_object(self):
        """Fetch the order and enforce object-level permissions."""
        obj = super().get_object()
        self.check_object_permissions(self.request, obj)
        return obj


class OrderCountView(APIView):
    """Return the number of in-progress orders for a business user."""

    permission_classes = [IsAuthenticated]

    def get(self, request, business_user_id):
        """Count in-progress orders for the given business user."""
        _get_business_user_or_404(business_user_id)
        count = Order.objects.filter(
            business_user_id=business_user_id,
            status="in_progress",
        ).count()
        return Response({"order_count": count})


class CompletedOrderCountView(APIView):
    """Return the number of completed orders for a business user."""

    permission_classes = [IsAuthenticated]

    def get(self, request, business_user_id):
        """Count completed orders for the given business user."""
        _get_business_user_or_404(business_user_id)
        count = Order.objects.filter(
            business_user_id=business_user_id,
            status="completed",
        ).count()
        return Response({"completed_order_count": count})
