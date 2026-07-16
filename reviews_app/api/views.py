from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.filters import OrderingFilter
from rest_framework.exceptions import ValidationError

from reviews_app.models import Review
from reviews_app.api.serializers import ReviewSerializer


class ReviewListView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ReviewSerializer
    filter_backends = [OrderingFilter]
    ordering_fields = ["updated_at", "rating"]
    ordering = ["-updated_at"]

    def _filter_by_business_user_id(self, queryset):
        business_user_id = self.request.query_params.get("business_user_id")
        if not business_user_id:
            return queryset
        try:
            return queryset.filter(business_user_id=int(business_user_id))
        except ValueError:
            raise ValidationError({"business_user_id": "Must be a valid integer."})

    def _filter_by_reviewer_id(self, queryset):
        reviewer_id = self.request.query_params.get("reviewer_id")
        if not reviewer_id:
            return queryset
        try:
            return queryset.filter(reviewer_id=int(reviewer_id))
        except ValueError:
            raise ValidationError({"reviewer_id": "Must be a valid integer."})

    def get_queryset(self):
        queryset = Review.objects.all()
        queryset = self._filter_by_business_user_id(queryset)
        queryset = self._filter_by_reviewer_id(queryset)
        return queryset
