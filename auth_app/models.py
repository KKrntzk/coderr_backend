from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    CUSTOMER = "customer"
    BUSINESS = "business"

    TYPE_CHOICES = [
        (CUSTOMER, "Customer"),
        (BUSINESS, "Business"),
    ]

    type = models.CharField(
        max_length=20,
        choices=TYPE_CHOICES,
    )
