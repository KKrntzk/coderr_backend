from django.urls import path
from reviews_app.api.views import ReviewListCreateView

urlpatterns = [
    path("reviews/", ReviewListCreateView.as_view(), name="review-list-create"),
]
