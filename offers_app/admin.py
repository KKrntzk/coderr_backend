from django.contrib import admin

from offers_app.models import Feature, Offer, OfferDetail


@admin.register(Offer)
class OfferAdmin(admin.ModelAdmin):
    """Admin configuration for Offer."""

    list_display = ["title", "user", "created_at", "updated_at"]


@admin.register(OfferDetail)
class OfferDetailAdmin(admin.ModelAdmin):
    """Admin configuration for OfferDetail."""

    list_display = ["title", "offer", "offer_type", "price", "delivery_time_in_days"]


@admin.register(Feature)
class FeatureAdmin(admin.ModelAdmin):
    """Admin configuration for Feature."""

    list_display = ["name", "offer_detail"]
