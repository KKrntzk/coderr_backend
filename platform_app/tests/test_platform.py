from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from offers_app.models import Offer
from reviews_app.models import Review

User = get_user_model()


class BaseInfoViewTest(APITestCase):
    """Tests for GET /api/base-info/."""

    def setUp(self):
        """Create two reviews, two business users, and one offer."""
        self.url = reverse("base-info")
        self.customer = User.objects.create_user(
            username="testcustomer",
            email="customer@mail.de",
            password="testpassword123",
            type="customer",
        )
        self.business1 = User.objects.create_user(
            username="testbusiness1",
            email="business1@mail.de",
            password="testpassword123",
            type="business",
        )
        self.business2 = User.objects.create_user(
            username="testbusiness2",
            email="business2@mail.de",
            password="testpassword123",
            type="business",
        )
        Review.objects.create(
            business_user=self.business1,
            reviewer=self.customer,
            rating=4,
            description="Gut.",
        )
        Review.objects.create(
            business_user=self.business2,
            reviewer=self.customer,
            rating=5,
            description="Sehr gut.",
        )
        self.offer = Offer.objects.create(
            user=self.business1,
            title="Logo Design",
            description="Logo Design Paket",
        )

    def test_base_info_success(self):
        """The endpoint returns 200."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_base_info_review_count(self):
        """review_count reflects the total number of reviews."""
        response = self.client.get(self.url)
        self.assertEqual(response.data["review_count"], 2)

    def test_base_info_average_rating(self):
        """average_rating is the mean of all review ratings, rounded to one decimal."""
        response = self.client.get(self.url)
        self.assertEqual(response.data["average_rating"], 4.5)

    def test_base_info_business_profile_count(self):
        """business_profile_count reflects the number of business users."""
        response = self.client.get(self.url)
        self.assertEqual(response.data["business_profile_count"], 2)

    def test_base_info_offer_count(self):
        """offer_count reflects the total number of offers."""
        response = self.client.get(self.url)
        self.assertEqual(response.data["offer_count"], 1)

    def test_base_info_no_auth_required(self):
        """The endpoint is accessible without authentication."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_base_info_empty_platform(self):
        """average_rating falls back to 0 when there are no reviews."""
        Review.objects.all().delete()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["average_rating"], 0)
