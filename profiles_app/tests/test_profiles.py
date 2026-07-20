from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

User = get_user_model()


class ProfileDetailViewTest(APITestCase):
    """Tests for GET /api/profile/{pk}/."""

    def setUp(self):
        """Create a user and authenticate as them."""
        self.user = User.objects.create_user(
            username="testuser",
            email="test@mail.de",
            password="testpassword123",
            type="customer",
        )
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token.key)
        self.url = reverse("profile-detail", kwargs={"pk": self.user.pk})

    def test_get_profile_success(self):
        """An existing profile is retrieved with its core fields."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["username"], "testuser")
        self.assertEqual(response.data["email"], "test@mail.de")
        self.assertEqual(response.data["user"], self.user.id)

    def test_get_profile_not_found(self):
        """A non-existent profile id returns a 404."""
        url = reverse("profile-detail", kwargs={"pk": 9999})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_profile_unauthenticated(self):
        """An unauthenticated request is rejected with a 401."""
        self.client.credentials()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_profile_fields_not_null(self):
        """Empty profile fields are returned as empty strings, not null."""
        response = self.client.get(self.url)
        self.assertEqual(response.data["first_name"], "")
        self.assertEqual(response.data["last_name"], "")
        self.assertEqual(response.data["location"], "")
        self.assertEqual(response.data["tel"], "")
        self.assertEqual(response.data["description"], "")
        self.assertEqual(response.data["working_hours"], "")


class ProfilePatchViewTest(APITestCase):
    """Tests for PATCH /api/profile/{pk}/."""

    def setUp(self):
        """Create the profile's owner and a second, unrelated user."""
        self.user = User.objects.create_user(
            username="testuser",
            email="test@mail.de",
            password="testpassword123",
            type="customer",
        )
        self.other_user = User.objects.create_user(
            username="otheruser",
            email="other@mail.de",
            password="testpassword123",
            type="customer",
        )
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token.key)
        self.url = reverse("profile-detail", kwargs={"pk": self.user.pk})

    def test_patch_profile_success(self):
        """The owner can update their own profile fields."""
        response = self.client.patch(
            self.url,
            {
                "first_name": "Max",
                "location": "Berlin",
            },
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["first_name"], "Max")
        self.assertEqual(response.data["location"], "Berlin")

    def test_patch_profile_not_owner(self):
        """A different user is rejected with a 403."""
        other_token = Token.objects.create(user=self.other_user)
        self.client.credentials(HTTP_AUTHORIZATION="Token " + other_token.key)
        response = self.client.patch(
            self.url,
            {
                "first_name": "Hacker",
            },
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_patch_profile_unauthenticated(self):
        """An unauthenticated request is rejected with a 401."""
        self.client.credentials()
        response = self.client.patch(
            self.url,
            {
                "first_name": "Max",
            },
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_patch_profile_not_found(self):
        """A non-existent profile id returns a 404."""
        url = reverse("profile-detail", kwargs={"pk": 9999})
        response = self.client.patch(
            url,
            {
                "first_name": "Max",
            },
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_patch_profile_fields_not_null(self):
        """An empty PATCH still returns empty strings, not null, for text fields."""
        response = self.client.patch(self.url, {})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["first_name"], "")
        self.assertEqual(response.data["location"], "")
        self.assertEqual(response.data["description"], "")

    def test_patch_profile_email_updates(self):
        """The email field can be updated via PATCH."""
        response = self.client.patch(self.url, {"email": "neue_email@mail.de"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], "neue_email@mail.de")


class BusinessProfileListViewTest(APITestCase):
    """Tests for GET /api/profiles/business/."""

    def setUp(self):
        """Create one customer and two business users."""
        self.url = reverse("business-profile-list")
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

    def test_get_business_profiles_success(self):
        """Only the two business profiles are returned."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_get_business_profiles_only_business(self):
        """Every profile in the list has type business."""
        response = self.client.get(self.url)
        for profile in response.data:
            self.assertEqual(profile["type"], "business")

    def test_get_business_profiles_unauthenticated(self):
        """An unauthenticated request is rejected with a 401."""
        self.client.credentials()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_business_profiles_fields_not_null(self):
        """Empty profile fields are returned as empty strings, not null."""
        response = self.client.get(self.url)
        for profile in response.data:
            self.assertEqual(profile["first_name"], "")
            self.assertEqual(profile["last_name"], "")
            self.assertEqual(profile["location"], "")
            self.assertEqual(profile["tel"], "")
            self.assertEqual(profile["description"], "")
            self.assertEqual(profile["working_hours"], "")


class CustomerProfileListViewTest(APITestCase):
    """Tests for GET /api/profiles/customer/."""

    def setUp(self):
        """Create one business and two customer users."""
        self.url = reverse("customer-profile-list")
        self.business = User.objects.create_user(
            username="testbusiness",
            email="business@mail.de",
            password="testpassword123",
            type="business",
        )
        self.customer1 = User.objects.create_user(
            username="testcustomer1",
            email="customer1@mail.de",
            password="testpassword123",
            type="customer",
        )
        self.customer2 = User.objects.create_user(
            username="testcustomer2",
            email="customer2@mail.de",
            password="testpassword123",
            type="customer",
        )
        self.token = Token.objects.create(user=self.business)
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token.key)

    def test_get_customer_profiles_success(self):
        """Only the two customer profiles are returned."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_get_customer_profiles_only_customer(self):
        """Every profile in the list has type customer."""
        response = self.client.get(self.url)
        for profile in response.data:
            self.assertEqual(profile["type"], "customer")

    def test_get_customer_profiles_unauthenticated(self):
        """An unauthenticated request is rejected with a 401."""
        self.client.credentials()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_customer_profiles_fields_present(self):
        """Each profile contains all fields required by the specification."""
        response = self.client.get(self.url)
        for profile in response.data:
            self.assertIn("user", profile)
            self.assertIn("username", profile)
            self.assertIn("first_name", profile)
            self.assertIn("last_name", profile)
            self.assertIn("file", profile)
            self.assertIn("uploaded_at", profile)
            self.assertIn("type", profile)
