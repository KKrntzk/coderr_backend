from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Offer(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="offers")
    title = models.CharField(max_length=255)
    image = models.ImageField(upload_to="offer_images/", blank=True, null=True)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class OfferDetail(models.Model):
    BASIC = "basic"
    STANDARD = "standard"
    PREMIUM = "premium"

    OFFER_TYPE_CHOICES = [
        (BASIC, "Basic"),
        (STANDARD, "Standard"),
        (PREMIUM, "Premium"),
    ]

    offer = models.ForeignKey(Offer, on_delete=models.CASCADE, related_name="details")
    title = models.CharField(max_length=255)
    revisions = models.IntegerField()
    delivery_time_in_days = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    offer_type = models.CharField(max_length=20, choices=OFFER_TYPE_CHOICES)

    def __str__(self):
        return f"{self.offer.title} - {self.offer_type}"


class Feature(models.Model):
    offer_detail = models.ForeignKey(
        OfferDetail, on_delete=models.CASCADE, related_name="features"
    )
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name
