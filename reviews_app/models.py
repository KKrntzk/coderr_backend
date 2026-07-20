from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Review(models.Model):
    """A customer's review of a business user's services."""

    business_user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="received_reviews"
    )
    reviewer = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="written_reviews"
    )
    rating = models.IntegerField()
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["business_user", "reviewer"],
                name="unique_review_per_business_user",
            )
        ]

    def __str__(self):
        """Return a short summary of who reviewed whom with which rating."""
        return f"{self.reviewer} -> {self.business_user} ({self.rating})"
