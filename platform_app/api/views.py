from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.contrib.auth import get_user_model
from django.db.models import Avg

from reviews_app.models import Review
from offers_app.models import Offer

User = get_user_model()


class BaseInfoView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
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
