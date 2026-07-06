from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from auth_app.models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (("Additional Info", {"fields": ("type",)}),)
