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
    file = models.ImageField(
        upload_to="profile_pictures/",
        blank=True,
        null=True,
    )
    location = models.CharField(max_length=100, blank=True, default="")
    tel = models.CharField(max_length=20, blank=True, default="")
    description = models.TextField(blank=True, default="")
    working_hours = models.CharField(max_length=50, blank=True, default="")
    uploaded_at = models.DateTimeField(null=True, blank=True)
