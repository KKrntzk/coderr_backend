from django.contrib.auth import get_user_model
from django.db.models import Avg
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from offers_app.models import Offer
from reviews_app.models import Review

User = get_user_model()


class BaseInfoView(APIView):
    """Return aggregated, platform-wide statistics.

    Combines data from the reviews, profiles, and offers domains, so it
    lives in its own app rather than in any single domain app.
    """

    permission_classes = [AllowAny]

    def get(self, request):
        """Compute and return review, rating, business profile, and offer counts."""
        review_count = Review.objects.count()
        average_rating = Review.objects.aggregate(avg=Avg("rating"))["avg"] or 0
        business_profile_count = User.objects.filter(type="business").count()
        offer_count = Offer.objects.count()

        return Response(
            {
                "review_count": review_count,
                "average_rating": round(average_rating, 1),
                "business_profile_count": business_profile_count,
                "offer_count": offer_count,
            }
        )
