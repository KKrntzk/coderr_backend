from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Order(models.Model):
    """An order placed by a customer for a specific offer detail.

    Order data is a frozen snapshot of the offer detail at the time of
    purchase, so later changes to the offer do not affect existing orders.
    """

    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

    STATUS_CHOICES = [
        (IN_PROGRESS, "In Progress"),
        (COMPLETED, "Completed"),
        (CANCELLED, "Cancelled"),
    ]

    customer_user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="customer_orders"
    )
    business_user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="business_orders"
    )
    title = models.CharField(max_length=255)
    revisions = models.IntegerField()
    delivery_time_in_days = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    features = models.JSONField(default=list)
    offer_type = models.CharField(max_length=20)
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default=IN_PROGRESS
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        """Return the order's title together with its current status."""
        return f"{self.title} ({self.status})"
