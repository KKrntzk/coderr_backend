from rest_framework.exceptions import ValidationError
from rest_framework.filters import OrderingFilter
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated

from core.permissions import IsCustomerUser
from reviews_app.api.permissions import IsReviewer
from reviews_app.api.serializers import (
    ReviewCreateSerializer,
    ReviewSerializer,
    ReviewUpdateSerializer,
)
from reviews_app.models import Review


class ReviewListCreateView(ListCreateAPIView):
    """List all reviews, or create a new review (customers only)."""

    filter_backends = [OrderingFilter]
    ordering_fields = ["updated_at", "rating"]
    ordering = ["-updated_at"]

    def get_permissions(self):
        """Restrict review creation to customers."""
        if self.request.method == "POST":
            return [IsAuthenticated(), IsCustomerUser()]
        return [IsAuthenticated()]

    def get_serializer_class(self):
        """Use the create serializer for POST, the read serializer otherwise."""
        if self.request.method == "POST":
            return ReviewCreateSerializer
        return ReviewSerializer

    def _filter_by_business_user_id(self, queryset):
        """Filter reviews by the reviewed business user's id, if provided."""
        business_user_id = self.request.query_params.get("business_user_id")
        if not business_user_id:
            return queryset
        try:
            return queryset.filter(business_user_id=int(business_user_id))
        except ValueError:
            raise ValidationError({"business_user_id": "Must be a valid integer."})

    def _filter_by_reviewer_id(self, queryset):
        """Filter reviews by the reviewer's id, if provided."""
        reviewer_id = self.request.query_params.get("reviewer_id")
        if not reviewer_id:
            return queryset
        try:
            return queryset.filter(reviewer_id=int(reviewer_id))
        except ValueError:
            raise ValidationError({"reviewer_id": "Must be a valid integer."})

    def get_queryset(self):
        """Return all reviews, optionally filtered by business user or reviewer."""
        queryset = Review.objects.all()
        queryset = self._filter_by_business_user_id(queryset)
        queryset = self._filter_by_reviewer_id(queryset)
        return queryset


class ReviewUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    """Update or delete a review (author only)."""

    http_method_names = ["patch", "delete", "head", "options"]
    permission_classes = [IsAuthenticated, IsReviewer]
    serializer_class = ReviewUpdateSerializer
    queryset = Review.objects.all()

    def get_object(self):
        """Fetch the review and enforce object-level permissions."""
        obj = super().get_object()
        self.check_object_permissions(self.request, obj)
        return obj
