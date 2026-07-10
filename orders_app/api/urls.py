from django.urls import path
from orders_app.api.views import OrderListView

ulrpatters = [path("orders/", OrderListView.as_view(), name="order-list")]
