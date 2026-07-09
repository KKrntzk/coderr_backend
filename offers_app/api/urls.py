from django.urls import path
from offers_app.api.views import (
    OfferListCreateView,
    OfferRetrieveUpdateDestroyView,
    OfferDetailRetrieveView,
)

urlpatterns = [
    path("offers/", OfferListCreateView.as_view(), name="offer-list-create"),
    path(
        "offers/<int:pk>/",
        OfferRetrieveUpdateDestroyView.as_view(),
        name="offer-retrieve-update",
    ),
    path(
        "offerdetails/<int:pk>/",
        OfferDetailRetrieveView.as_view(),
        name="offerdetail-retrieve",
    ),
]
