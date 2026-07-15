from django.urls import path
from orders_app.api.views import OrderListCreateView, OrderUpdateView

urlpatterns = [
    path("orders/", OrderListCreateView.as_view(), name="order-list-create"),
    path("orders/<int:pk>/", OrderUpdateView.as_view(), name="order-update"),
]
