from django.contrib import admin
from offers_app.models import Offer, OfferDetail, Feature


@admin.register(Offer)
class OfferAdmin(admin.ModelAdmin):
    list_display = ["title", "user", "created_at", "updated_at"]


@admin.register(OfferDetail)
class OfferDetailAdmin(admin.ModelAdmin):
    list_display = ["title", "offer", "offer_type", "price", "delivery_time_in_days"]


@admin.register(Feature)
class FeatureAdmin(admin.ModelAdmin):
    list_display = ["name", "offer_detail"]
