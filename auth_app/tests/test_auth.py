from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model

User = get_user_model()


class RegistrationViewTest(APITestCase):

    def setUp(self):
        self.url = reverse("registration")
        self.valid_data = {
            "username": "testuser",
            "email": "test@mail.de",
            "password": "testpassword123",
            "repeated_password": "testpassword123",
            "type": "customer",
        }

    def test_registration_success(self):
        response = self.client.post(self.url, self.valid_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("token", response.data)
        self.assertIn("user_id", response.data)
        self.assertEqual(response.data["username"], "testuser")
        self.assertEqual(response.data["email"], "test@mail.de")

    def test_registration_password_mismatch(self):
        data = self.valid_data.copy()
        data["repeated_password"] = "wrongpassword"
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("repeated_password", response.data)

    def test_registration_missing_email(self):
        data = self.valid_data.copy()
        data.pop("email")
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)

    def test_registration_duplicate_username(self):
        self.client.post(self.url, self.valid_data)
        response = self.client.post(self.url, self.valid_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("username", response.data)


class LoginViewTest(APITestCase):

    def setUp(self):
        self.url = reverse("login")
        self.user = User.objects.create_user(
            username="testuser",
            email="test@mail.de",
            password="testpassword123",
            type="customer",
        )

    def test_login_success(self):
        response = self.client.post(
            self.url,
            {
                "username": "testuser",
                "password": "testpassword123",
            },
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("token", response.data)
        self.assertIn("user_id", response.data)
        self.assertEqual(response.data["username"], "testuser")
        self.assertEqual(response.data["email"], "test@mail.de")

    def test_login_wrong_password(self):
        response = self.client.post(
            self.url,
            {
                "username": "testuser",
                "password": "wrongpassword",
            },
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("detail", response.data)

    def test_login_wrong_username(self):
        response = self.client.post(
            self.url,
            {
                "username": "wronguser",
                "password": "testpassword123",
            },
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("detail", response.data)

    def test_login_missing_fields(self):
        response = self.client.post(self.url, {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
