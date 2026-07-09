from django.urls import path
from offers_app.api.views import OfferListView

urlpatterns = [
    path("offers/", OfferListView.as_view(), name="offer-list"),
]
