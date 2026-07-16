from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model
from reviews_app.models import Review

User = get_user_model()


class ReviewListViewTest(APITestCase):

    def setUp(self):
        self.url = reverse("review-list")
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
        self.token = Token.objects.create(user=self.customer)
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token.key)

        self.review1 = Review.objects.create(
            business_user=self.business1,
            reviewer=self.customer,
            rating=4,
            description="Sehr professionell.",
        )
        self.review2 = Review.objects.create(
            business_user=self.business2,
            reviewer=self.customer,
            rating=5,
            description="Top Qualität!",
        )

    def test_get_reviews_success(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_get_reviews_filter_by_business_user_id(self):
        response = self.client.get(self.url, {"business_user_id": self.business1.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["business_user"], self.business1.id)

    def test_get_reviews_filter_by_reviewer_id(self):
        response = self.client.get(self.url, {"reviewer_id": self.customer.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_get_reviews_ordering_by_rating(self):
        response = self.client.get(self.url, {"ordering": "rating"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ratings = [r["rating"] for r in response.data]
        self.assertEqual(ratings, sorted(ratings))

    def test_get_reviews_unauthenticated(self):
        self.client.credentials()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_reviews_contains_required_fields(self):
        response = self.client.get(self.url)
        result = response.data[0]
        self.assertIn("id", result)
        self.assertIn("business_user", result)
        self.assertIn("reviewer", result)
        self.assertIn("rating", result)
        self.assertIn("description", result)
