from django.urls import path

from orders_app.api.views import (
    CompletedOrderCountView,
    OrderCountView,
    OrderListCreateView,
    OrderUpdateDestroyView,
)

urlpatterns = [
    path("orders/", OrderListCreateView.as_view(), name="order-list-create"),
    path("orders/<int:pk>/", OrderUpdateDestroyView.as_view(), name="order-update"),
    path(
        "order-count/<int:business_user_id>/",
        OrderCountView.as_view(),
        name="order-count",
    ),
    path(
        "completed-order-count/<int:business_user_id>/",
        CompletedOrderCountView.as_view(),
        name="completed-order-count",
    ),
]
