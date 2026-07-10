from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model
from orders_app.models import Order

User = get_user_model()


class OrderListViewTest(APITestCase):

    def setUp(self):
        self.url = reverse("order-list")
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
        self.other_user = User.objects.create_user(
            username="testbusinessother",
            email="business@mail.de",
            password="test12",
            type="customer",
        )
        self.token = Token.objects.create(user=self.customer)
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token.key)
        self.order = Order.objects.create(
            customer_user=self.customer,
            business_user=self.business,
            title="Logo Desgin",
            revisions=3,
            delivery_time_in_days=5,
            price=150,
            features=["logo design", "Visitenkarten"],
            offer_type="basic",
        )

    def test_get_orders_success(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_get_orders_as_business_user(self):
        business_token = Token.objects.create(user=self.business)
        self.client.credentials(HTTP_AUTHORIZATION="Token " + business_token.key)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_get_orders_not_involved(self):
        other_token = Token.objects.create(user=self.other_user)
        self.client.credentials(HTTP_AUTHORIZATION="Token " + other_token.key)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    def test_get_orders_unauthenticated(self):
        self.client.credentials()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_orders_contains_required_fields(self):
        response = self.client.get(self.url)
        result = response.data[0]
        self.assertIn("id", result)
        self.assertIn("customer_user", result)
        self.assertIn("business_user", result)
        self.assertIn("title", result)
        self.assertIn("features", result)
        self.assertIn("status", result)
