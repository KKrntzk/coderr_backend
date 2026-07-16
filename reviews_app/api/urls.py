from django.urls import path
from reviews_app.api.views import ReviewListView

urlpatterns = [
    path("reviews/", ReviewListView.as_view(), name="review-list"),
]
