from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from orders_app.models import Order

User = get_user_model()


class OrderCountViewTest(APITestCase):
    """Tests for GET /api/order-count/{business_user_id}/."""

    def setUp(self):
        """Create two in-progress and one completed order for a business user."""
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
        """The endpoint returns 200 with an order_count field."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["order_count"], 2)

    def test_order_count_only_in_progress(self):
        """Only in-progress orders are counted, not completed ones."""
        response = self.client.get(self.url)
        self.assertEqual(response.data["order_count"], 2)

    def test_order_count_business_user_not_found(self):
        """A non-existent business user id returns a 404."""
        url = reverse("order-count", kwargs={"business_user_id": 9999})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_order_count_user_is_customer_not_business(self):
        """An id belonging to a customer, not a business user, returns a 404."""
        url = reverse("order-count", kwargs={"business_user_id": self.customer.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_order_count_unauthenticated(self):
        """An unauthenticated request is rejected with a 401."""
        self.client.credentials()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class CompletedOrderCountViewTest(APITestCase):
    """Tests for GET /api/completed-order-count/{business_user_id}/."""

    def setUp(self):
        """Create two completed and one in-progress order for a business user."""
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
            status="completed",
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
            status="completed",
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
            status="in_progress",
        )
        self.url = reverse(
            "completed-order-count", kwargs={"business_user_id": self.business.id}
        )

    def test_completed_order_count_success(self):
        """The endpoint returns 200 with a completed_order_count field."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["completed_order_count"], 2)

    def test_completed_order_count_business_user_not_found(self):
        """A non-existent business user id returns a 404."""
        url = reverse("completed-order-count", kwargs={"business_user_id": 9999})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_completed_order_count_user_is_customer_not_business(self):
        """An id belonging to a customer, not a business user, returns a 404."""
        url = reverse(
            "completed-order-count", kwargs={"business_user_id": self.customer.id}
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_completed_order_count_unauthenticated(self):
        """An unauthenticated request is rejected with a 401."""
        self.client.credentials()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
