from django.urls import path
from offers_app.api.views import OfferListCreateView, OfferRetrieveView

urlpatterns = [
    path("offers/", OfferListCreateView.as_view(), name="offer-list-create"),
    path("offers/<int:pk>/", OfferRetrieveView.as_view(), name="offer-retrieve"),
]
