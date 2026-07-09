from django.urls import path
from offers_app.api.views import (
    OfferListCreateView,
    OfferRetrieveUpdateView,
)

urlpatterns = [
    path("offers/", OfferListCreateView.as_view(), name="offer-list-create"),
    path(
        "offers/<int:pk>/",
        OfferRetrieveUpdateView.as_view(),
        name="offer-retrieve-update",
    ),
]
