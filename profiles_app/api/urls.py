from django.urls import path
from profiles_app.api.views import ProfileDetailView, BusinessProfileListView

urlpatterns = [
    path("profile/<int:pk>/", ProfileDetailView.as_view(), name="profile-detail"),
    path(
        "profiles/business/",
        BusinessProfileListView.as_view(),
        name="business-profile-list",
    ),
]
