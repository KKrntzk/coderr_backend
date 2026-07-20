from django.contrib import admin

from orders_app.models import Order


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """Admin configuration for Order."""

    list_display = [
        "title",
        "customer_user",
        "business_user",
        "status",
        "price",
        "created_at",
    ]
