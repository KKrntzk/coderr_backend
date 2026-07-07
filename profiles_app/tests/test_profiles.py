from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model

User = get_user_model()


class ProfileDetailViewTest(APITestCase):

    def setUp(self):
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
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["username"], "testuser")
        self.assertEqual(response.data["email"], "test@mail.de")
        self.assertEqual(response.data["user"], self.user.id)

    def test_get_profile_not_found(self):
        url = reverse("profile-detail", kwargs={"pk": 9999})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_profile_unauthenticated(self):
        self.client.credentials()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_profile_fields_not_null(self):
        response = self.client.get(self.url)
        self.assertEqual(response.data["first_name"], "")
        self.assertEqual(response.data["last_name"], "")
        self.assertEqual(response.data["location"], "")
        self.assertEqual(response.data["tel"], "")
        self.assertEqual(response.data["description"], "")
        self.assertEqual(response.data["working_hours"], "")


class ProfilePatchViewTest(APITestCase):

    def setUp(self):
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
        self.client.credentials()
        response = self.client.patch(
            self.url,
            {
                "first_name": "Max",
            },
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_patch_profile_not_found(self):
        url = reverse("profile-detail", kwargs={"pk": 9999})
        response = self.client.patch(
            url,
            {
                "first_name": "Max",
            },
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_patch_profile_fields_not_null(self):
        response = self.client.patch(self.url, {})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["first_name"], "")
        self.assertEqual(response.data["location"], "")
        self.assertEqual(response.data["description"], "")


class BusinessProfileListViewTest(APITestCase):

    def setUp(self):
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
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_get_business_profiles_only_business(self):
        response = self.client.get(self.url)
        for profile in response.data:
            self.assertEqual(profile["type"], "business")

    def test_get_business_profiles_unauthenticated(self):
        self.client.credentials()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_business_profiles_fields_not_null(self):
        response = self.client.get(self.url)
        for profile in response.data:
            self.assertEqual(profile["first_name"], "")
            self.assertEqual(profile["last_name"], "")
            self.assertEqual(profile["location"], "")
            self.assertEqual(profile["tel"], "")
            self.assertEqual(profile["description"], "")
            self.assertEqual(profile["working_hours"], "")


class CustomerProfileListViewTest(APITestCase):

    def setUp(self):
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
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_get_customer_profiles_only_customer(self):
        response = self.client.get(self.url)
        for profile in response.data:
            self.assertEqual(profile["type"], "customer")

    def test_get_customer_profiles_unauthenticated(self):
        self.client.credentials()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_customer_profiles_fields_present(self):
        response = self.client.get(self.url)
        for profile in response.data:
            self.assertIn("user", profile)
            self.assertIn("username", profile)
            self.assertIn("first_name", profile)
            self.assertIn("last_name", profile)
            self.assertIn("file", profile)
            self.assertIn("uploaded_at", profile)
            self.assertIn("type", profile)
