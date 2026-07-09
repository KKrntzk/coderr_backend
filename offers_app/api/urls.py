from django.urls import path
from offers_app.api.views import OfferListCreateView

urlpatterns = [
    path("offers/", OfferListCreateView.as_view(), name="offer-list-create"),
]
