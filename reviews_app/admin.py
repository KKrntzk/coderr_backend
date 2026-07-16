from django.contrib import admin
from reviews_app.models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ["business_user", "reviewer", "rating", "created_at"]
