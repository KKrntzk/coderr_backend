from django.urls import path
from orders_app.api.views import (
    OrderListCreateView,
    OrderUpdateDestroyView,
    OrderCountView,
)

urlpatterns = [
    path("orders/", OrderListCreateView.as_view(), name="order-list-create"),
    path("orders/<int:pk>/", OrderUpdateDestroyView.as_view(), name="order-update"),
    path(
        "order-count/<int:business_user_id>/",
        OrderCountView.as_view(),
        name="order-count",
    ),
]
