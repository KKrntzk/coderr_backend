from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from reviews_app.models import Review

User = get_user_model()


class ReviewListViewTest(APITestCase):
    """Tests for GET /api/reviews/."""

    def setUp(self):
        """Create a customer with reviews for two different business users."""
        self.url = reverse("review-list-create")
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
        """All reviews are returned."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_get_reviews_filter_by_business_user_id(self):
        """Filtering by business_user_id returns only that user's reviews."""
        response = self.client.get(self.url, {"business_user_id": self.business1.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["business_user"], self.business1.id)

    def test_get_reviews_filter_by_reviewer_id(self):
        """Filtering by reviewer_id returns only that user's reviews."""
        response = self.client.get(self.url, {"reviewer_id": self.customer.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_get_reviews_ordering_by_rating(self):
        """Ordering by rating returns reviews in ascending rating order."""
        response = self.client.get(self.url, {"ordering": "rating"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ratings = [r["rating"] for r in response.data]
        self.assertEqual(ratings, sorted(ratings))

    def test_get_reviews_unauthenticated(self):
        """An unauthenticated request is rejected with a 401."""
        self.client.credentials()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_reviews_contains_required_fields(self):
        """Each review contains all fields required by the specification."""
        response = self.client.get(self.url)
        result = response.data[0]
        self.assertIn("id", result)
        self.assertIn("business_user", result)
        self.assertIn("reviewer", result)
        self.assertIn("rating", result)
        self.assertIn("description", result)


class ReviewCreateViewTest(APITestCase):
    """Tests for POST /api/reviews/."""

    def setUp(self):
        """Create a customer, a business user, and a second unrelated customer."""
        self.url = reverse("review-list-create")
        self.customer = User.objects.create_user(
            username="testcustomer",
            email="customer@mail.de",
            password="testpassword123",
            type="customer",
        )
        self.business = User.objects.create_user(
            username="testbusiness",
            email="business@mail.de",
            password="testpassword123",
            type="business",
        )
        self.other_customer = User.objects.create_user(
            username="othercustomer",
            email="othercustomer@mail.de",
            password="testpassword123",
            type="customer",
        )
        self.customer_token = Token.objects.create(user=self.customer)
        self.business_token = Token.objects.create(user=self.business)
        self.other_customer_token = Token.objects.create(user=self.other_customer)
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.customer_token.key)
        self.valid_data = {
            "business_user": self.business.id,
            "rating": 4,
            "description": "Alles war toll!",
        }

    def test_create_review_success(self):
        """A valid payload creates a review with the reviewer set automatically."""
        response = self.client.post(self.url, self.valid_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["business_user"], self.business.id)
        self.assertEqual(response.data["reviewer"], self.customer.id)
        self.assertEqual(response.data["rating"], 4)

    def test_create_review_duplicate(self):
        """A second review for the same business user by the same reviewer is rejected."""
        self.client.post(self.url, self.valid_data)
        response = self.client.post(self.url, self.valid_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_review_target_not_business(self):
        """Reviewing a non-business user is rejected with a 400."""
        data = self.valid_data.copy()
        data["business_user"] = self.other_customer.id
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_review_business_forbidden(self):
        """A business user is rejected with a 403."""
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.business_token.key)
        response = self.client.post(self.url, self.valid_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_review_unauthenticated(self):
        """An unauthenticated request is rejected with a 401."""
        self.client.credentials()
        response = self.client.post(self.url, self.valid_data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_review_different_customers_allowed(self):
        """Different customers can each review the same business user once."""
        response1 = self.client.post(self.url, self.valid_data)
        self.assertEqual(response1.status_code, status.HTTP_201_CREATED)

        self.client.credentials(
            HTTP_AUTHORIZATION="Token " + self.other_customer_token.key
        )
        response2 = self.client.post(self.url, self.valid_data)
        self.assertEqual(response2.status_code, status.HTTP_201_CREATED)


class ReviewUpdateDestroyViewTest(APITestCase):
    """Tests for PATCH and DELETE /api/reviews/{id}/."""

    def setUp(self):
        """Create a review and a second, unrelated customer."""
        self.customer = User.objects.create_user(
            username="testcustomer",
            email="customer@mail.de",
            password="testpassword123",
            type="customer",
        )
        self.other_customer = User.objects.create_user(
            username="othercustomer",
            email="othercustomer@mail.de",
            password="testpassword123",
            type="customer",
        )
        self.business = User.objects.create_user(
            username="testbusiness",
            email="business@mail.de",
            password="testpassword123",
            type="business",
        )
        self.customer_token = Token.objects.create(user=self.customer)
        self.other_customer_token = Token.objects.create(user=self.other_customer)
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.customer_token.key)

        self.review = Review.objects.create(
            business_user=self.business,
            reviewer=self.customer,
            rating=4,
            description="Sehr professionell.",
        )
        self.url = reverse("review-update-destroy", kwargs={"pk": self.review.pk})

    def test_patch_review_success(self):
        """The author can update rating and description."""
        response = self.client.patch(
            self.url, {"rating": 5, "description": "Noch besser!"}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["rating"], 5)
        self.assertEqual(response.data["description"], "Noch besser!")

    def test_patch_review_business_user_unchanged(self):
        """The reviewed business user cannot be changed via PATCH."""
        response = self.client.patch(self.url, {"rating": 5})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["business_user"], self.business.id)

    def test_patch_review_not_owner(self):
        """A different customer is rejected with a 403."""
        self.client.credentials(
            HTTP_AUTHORIZATION="Token " + self.other_customer_token.key
        )
        response = self.client.patch(self.url, {"rating": 1})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_patch_review_unauthenticated(self):
        """An unauthenticated request is rejected with a 401."""
        self.client.credentials()
        response = self.client.patch(self.url, {"rating": 1})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_patch_review_not_found(self):
        """A non-existent review id returns a 404."""
        url = reverse("review-update-destroy", kwargs={"pk": 9999})
        response = self.client.patch(url, {"rating": 1})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_review_success(self):
        """The author can delete their review, which is then removed from the DB."""
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Review.objects.filter(pk=self.review.pk).exists())

    def test_delete_review_not_owner(self):
        """A non-author is rejected with a 403 and the review remains."""
        self.client.credentials(
            HTTP_AUTHORIZATION="Token " + self.other_customer_token.key
        )
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Review.objects.filter(pk=self.review.pk).exists())

    def test_delete_review_unauthenticated(self):
        """An unauthenticated request is rejected with a 401."""
        self.client.credentials()
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_review_not_found(self):
        """A non-existent review id returns a 404."""
        url = reverse("review-update-destroy", kwargs={"pk": 9999})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
