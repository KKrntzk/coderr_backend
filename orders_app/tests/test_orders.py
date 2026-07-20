from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from offers_app.models import Feature, Offer, OfferDetail
from orders_app.models import Order

User = get_user_model()


class OrderListViewTest(APITestCase):
    """Tests for GET /api/orders/."""

    def setUp(self):
        """Create an order between a customer and a business user."""
        self.url = reverse("order-list-create")
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
        """The customer sees their own order."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_get_orders_as_business_user(self):
        """The business user sees the order they are assigned to."""
        business_token = Token.objects.create(user=self.business)
        self.client.credentials(HTTP_AUTHORIZATION="Token " + business_token.key)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_get_orders_not_involved(self):
        """A user with no relation to the order sees an empty list."""
        other_token = Token.objects.create(user=self.other_user)
        self.client.credentials(HTTP_AUTHORIZATION="Token " + other_token.key)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    def test_get_orders_unauthenticated(self):
        """An unauthenticated request is rejected with a 401."""
        self.client.credentials()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_orders_contains_required_fields(self):
        """Each order in the list contains all fields required by the specification."""
        response = self.client.get(self.url)
        result = response.data[0]
        self.assertIn("id", result)
        self.assertIn("customer_user", result)
        self.assertIn("business_user", result)
        self.assertIn("title", result)
        self.assertIn("features", result)
        self.assertIn("status", result)


class OrderCreateViewTest(APITestCase):
    """Tests for POST /api/orders/."""

    def setUp(self):
        """Create a business user with an offer detail, and a customer to order it."""
        self.url = reverse("order-list-create")
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
        self.customer_token = Token.objects.create(user=self.customer)
        self.business_token = Token.objects.create(user=self.business)
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.customer_token.key)

        self.offer = Offer.objects.create(
            user=self.business,
            title="Logo Design Paket",
            description="Ein Logo Design Paket",
        )
        self.offer_detail = OfferDetail.objects.create(
            offer=self.offer,
            title="Basic Logo",
            revisions=3,
            delivery_time_in_days=5,
            price=150,
            offer_type="basic",
        )
        Feature.objects.create(offer_detail=self.offer_detail, name="Logo Design")
        Feature.objects.create(offer_detail=self.offer_detail, name="Visitenkarten")

    def test_create_order_success(self):
        """A valid offer_detail_id creates an order with the copied core fields."""
        response = self.client.post(self.url, {"offer_detail_id": self.offer_detail.id})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["title"], "Basic Logo")
        self.assertEqual(response.data["customer_user"], self.customer.id)
        self.assertEqual(response.data["business_user"], self.business.id)

    def test_create_order_features_copied(self):
        """The offer detail's features are copied into the order as a snapshot."""
        response = self.client.post(self.url, {"offer_detail_id": self.offer_detail.id})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("Logo Design", response.data["features"])
        self.assertIn("Visitenkarten", response.data["features"])

    def test_create_order_status_default(self):
        """A new order defaults to status in_progress."""
        response = self.client.post(self.url, {"offer_detail_id": self.offer_detail.id})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["status"], "in_progress")

    def test_create_order_missing_offer_detail_id(self):
        """A missing offer_detail_id is rejected with a 400."""
        response = self.client.post(self.url, {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_order_offer_detail_not_found(self):
        """A non-existent offer_detail_id returns a 404."""
        response = self.client.post(self.url, {"offer_detail_id": 9999})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_order_business_forbidden(self):
        """A business user is rejected with a 403."""
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.business_token.key)
        response = self.client.post(self.url, {"offer_detail_id": self.offer_detail.id})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_order_unauthenticated(self):
        """An unauthenticated request is rejected with a 401."""
        self.client.credentials()
        response = self.client.post(self.url, {"offer_detail_id": self.offer_detail.id})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class OrderUpdateViewTest(APITestCase):
    """Tests for PATCH /api/orders/{id}/."""

    def setUp(self):
        """Create an order and a second, unrelated business user."""
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
        self.other_business = User.objects.create_user(
            username="otherbusiness",
            email="otherbusiness@mail.de",
            password="testpassword123",
            type="business",
        )
        self.customer_token = Token.objects.create(user=self.customer)
        self.business_token = Token.objects.create(user=self.business)
        self.other_business_token = Token.objects.create(user=self.other_business)
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.business_token.key)

        self.order = Order.objects.create(
            customer_user=self.customer,
            business_user=self.business,
            title="Logo Design",
            revisions=3,
            delivery_time_in_days=5,
            price=150,
            features=["Logo Design", "Visitenkarten"],
            offer_type="basic",
        )
        self.url = reverse("order-update", kwargs={"pk": self.order.pk})

    def test_patch_order_status_success(self):
        """The assigned business user can update the order's status."""
        response = self.client.patch(self.url, {"status": "completed"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "completed")

    def test_patch_order_other_fields_unchanged(self):
        """Fields other than status are ignored, even if submitted."""
        response = self.client.patch(
            self.url,
            {
                "status": "completed",
                "title": "Hacked Title",
                "price": 9999,
            },
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "Logo Design")
        self.assertEqual(str(response.data["price"]), "150.00")

    def test_patch_order_not_business_owner(self):
        """A different business user is rejected with a 403."""
        self.client.credentials(
            HTTP_AUTHORIZATION="Token " + self.other_business_token.key
        )
        response = self.client.patch(self.url, {"status": "completed"})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_patch_order_customer_forbidden(self):
        """The customer who placed the order cannot change its status."""
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.customer_token.key)
        response = self.client.patch(self.url, {"status": "completed"})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_patch_order_unauthenticated(self):
        """An unauthenticated request is rejected with a 401."""
        self.client.credentials()
        response = self.client.patch(self.url, {"status": "completed"})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_patch_order_not_found(self):
        """A non-existent order id returns a 404."""
        url = reverse("order-update", kwargs={"pk": 9999})
        response = self.client.patch(url, {"status": "completed"})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class OrderDeleteViewTest(APITestCase):
    """Tests for DELETE /api/orders/{id}/."""

    def setUp(self):
        """Create an order plus a staff (admin) user for deletion tests."""
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
        self.admin = User.objects.create_user(
            username="testadmin",
            email="admin@mail.de",
            password="testpassword123",
            type="business",
            is_staff=True,
        )
        self.business_token = Token.objects.create(user=self.business)
        self.admin_token = Token.objects.create(user=self.admin)
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.admin_token.key)

        self.order = Order.objects.create(
            customer_user=self.customer,
            business_user=self.business,
            title="Logo Design",
            revisions=3,
            delivery_time_in_days=5,
            price=150,
            features=["Logo Design", "Visitenkarten"],
            offer_type="basic",
        )
        self.url = reverse("order-update", kwargs={"pk": self.order.pk})

    def test_delete_order_success(self):
        """An admin can delete an order, which is then removed from the DB."""
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Order.objects.filter(pk=self.order.pk).exists())

    def test_delete_order_not_admin(self):
        """A non-admin business user is rejected with a 403 and the order remains."""
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.business_token.key)
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Order.objects.filter(pk=self.order.pk).exists())

    def test_delete_order_unauthenticated(self):
        """An unauthenticated request is rejected with a 401."""
        self.client.credentials()
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_order_not_found(self):
        """A non-existent order id returns a 404."""
        url = reverse("order-update", kwargs={"pk": 9999})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
