from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model
from orders_app.models import Order

User = get_user_model()


class OrderCountViewTest(APITestCase):

    def setUp(self):
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
        self.token = Token.objects.create(user=self.customer)
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token.key)

        Order.objects.create(
            customer_user=self.customer,
            business_user=self.business,
            title="Order 1",
            revisions=3,
            delivery_time_in_days=5,
            price=150,
            features=[],
            offer_type="basic",
            status="in_progress",
        )
        Order.objects.create(
            customer_user=self.customer,
            business_user=self.business,
            title="Order 2",
            revisions=3,
            delivery_time_in_days=5,
            price=150,
            features=[],
            offer_type="basic",
            status="in_progress",
        )
        Order.objects.create(
            customer_user=self.customer,
            business_user=self.business,
            title="Order 3",
            revisions=3,
            delivery_time_in_days=5,
            price=150,
            features=[],
            offer_type="basic",
            status="completed",
        )
        self.url = reverse("order-count", kwargs={"business_user_id": self.business.id})

    def test_order_count_success(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["order_count"], 2)

    def test_order_count_only_in_progress(self):
        response = self.client.get(self.url)
        self.assertEqual(response.data["order_count"], 2)

    def test_order_count_business_user_not_found(self):
        url = reverse("order-count", kwargs={"business_user_id": 9999})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_order_count_user_is_customer_not_business(self):
        url = reverse("order-count", kwargs={"business_user_id": self.customer.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_order_count_unauthenticated(self):
        self.client.credentials()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
