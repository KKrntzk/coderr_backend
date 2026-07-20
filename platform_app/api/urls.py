from django.urls import path

from platform_app.api.views import BaseInfoView

urlpatterns = [
    path("base-info/", BaseInfoView.as_view(), name="base-info"),
]
