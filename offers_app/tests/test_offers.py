from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from offers_app.models import Offer, OfferDetail

User = get_user_model()


class OfferListViewTest(APITestCase):
    """Tests for GET /api/offers/."""

    def setUp(self):
        """Create two offers from two different business users."""
        self.url = reverse("offer-list-create")
        self.business_user = User.objects.create_user(
            username="testbusiness",
            email="business@mail.de",
            password="testpassword123",
            type="business",
        )
        self.other_business = User.objects.create_user(
            username="otherbusiness",
            email="other@mail.de",
            password="testpassword123",
            type="business",
        )
        self.offer1 = Offer.objects.create(
            user=self.business_user,
            title="Website Design",
            description="Professionelles Website-Design",
        )
        self.detail1 = OfferDetail.objects.create(
            offer=self.offer1,
            title="Basic",
            revisions=2,
            delivery_time_in_days=7,
            price=100,
            offer_type="basic",
        )
        self.offer2 = Offer.objects.create(
            user=self.other_business,
            title="Logo Design",
            description="Professionelles Logo-Design",
        )
        self.detail2 = OfferDetail.objects.create(
            offer=self.offer2,
            title="Basic",
            revisions=1,
            delivery_time_in_days=3,
            price=50,
            offer_type="basic",
        )

    def test_get_offer_list_success(self):
        """All offers are returned in a paginated list."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 2)

    def test_get_offer_list_paginated(self):
        """The response follows the standard pagination format."""
        response = self.client.get(self.url)
        self.assertIn("count", response.data)
        self.assertIn("next", response.data)
        self.assertIn("previous", response.data)
        self.assertIn("results", response.data)

    def test_get_offer_list_no_auth_required(self):
        """The endpoint is accessible without authentication."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_filter_by_creator_id(self):
        """Filtering by creator_id returns only that user's offers."""
        response = self.client.get(self.url, {"creator_id": self.business_user.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["user"], self.business_user.id)

    def test_filter_by_min_price(self):
        """Filtering by min_price excludes offers below the threshold."""
        response = self.client.get(self.url, {"min_price": 75})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["min_price"], 100)

    def test_filter_by_max_delivery_time(self):
        """Filtering by max_delivery_time excludes slower offers."""
        response = self.client.get(self.url, {"max_delivery_time": 5})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["min_delivery_time"], 3)

    def test_search_by_title(self):
        """Searching matches offers by title."""
        response = self.client.get(self.url, {"search": "Website"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["title"], "Website Design")

    def test_ordering_by_min_price(self):
        """Ordering by min_price returns offers in ascending price order."""
        response = self.client.get(self.url, {"ordering": "min_price"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        prices = [r["min_price"] for r in response.data["results"]]
        self.assertEqual(prices, sorted(prices))

    def test_offer_contains_required_fields(self):
        """Each offer in the list contains all fields required by the specification."""
        response = self.client.get(self.url)
        result = response.data["results"][0]
        self.assertIn("id", result)
        self.assertIn("user", result)
        self.assertIn("title", result)
        self.assertIn("description", result)
        self.assertIn("details", result)
        self.assertIn("min_price", result)
        self.assertIn("min_delivery_time", result)
        self.assertIn("user_details", result)


class OfferCreateViewTest(APITestCase):
    """Tests for POST /api/offers/."""

    def setUp(self):
        """Create a business and a customer user, plus a valid offer payload."""
        self.url = reverse("offer-list-create")
        self.business_user = User.objects.create_user(
            username="testbusiness",
            email="business@mail.de",
            password="testpassword123",
            type="business",
        )
        self.customer_user = User.objects.create_user(
            username="testcustomer",
            email="customer@mail.de",
            password="testpassword123",
            type="customer",
        )
        self.business_token = Token.objects.create(user=self.business_user)
        self.customer_token = Token.objects.create(user=self.customer_user)
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.business_token.key)
        self.valid_data = {
            "title": "Grafikdesign-Paket",
            "description": "Ein umfassendes Grafikdesign-Paket.",
            "details": [
                {
                    "title": "Basic Design",
                    "revisions": 2,
                    "delivery_time_in_days": 5,
                    "price": 100,
                    "features": ["Logo Design", "Visitenkarte"],
                    "offer_type": "basic",
                },
                {
                    "title": "Standard Design",
                    "revisions": 5,
                    "delivery_time_in_days": 7,
                    "price": 200,
                    "features": ["Logo Design", "Visitenkarte", "Briefpapier"],
                    "offer_type": "standard",
                },
                {
                    "title": "Premium Design",
                    "revisions": 10,
                    "delivery_time_in_days": 10,
                    "price": 500,
                    "features": ["Logo Design", "Visitenkarte", "Briefpapier", "Flyer"],
                    "offer_type": "premium",
                },
            ],
        }

    def test_create_offer_success(self):
        """A valid payload creates an offer with all three details."""
        response = self.client.post(self.url, self.valid_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["title"], "Grafikdesign-Paket")
        self.assertEqual(len(response.data["details"]), 3)

    def test_create_offer_features_saved(self):
        """Features provided for a detail are saved and returned."""
        response = self.client.post(self.url, self.valid_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        basic_detail = next(
            d for d in response.data["details"] if d["offer_type"] == "basic"
        )
        self.assertIn("Logo Design", basic_detail["features"])
        self.assertIn("Visitenkarte", basic_detail["features"])

    def test_create_offer_missing_details(self):
        """Fewer than 3 details are rejected with a 400."""
        data = self.valid_data.copy()
        data["details"] = data["details"][:2]
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_offer_wrong_offer_types(self):
        """Details missing one of basic/standard/premium are rejected with a 400."""
        data = self.valid_data.copy()
        data["details"][0]["offer_type"] = "basic"
        data["details"][1]["offer_type"] = "basic"
        data["details"][2]["offer_type"] = "basic"
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_offer_customer_forbidden(self):
        """A customer user is rejected with a 403."""
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.customer_token.key)
        response = self.client.post(self.url, self.valid_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_offer_unauthenticated(self):
        """An unauthenticated request is rejected with a 401."""
        self.client.credentials()
        response = self.client.post(self.url, self.valid_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_offer_user_set_automatically(self):
        """The offer's owner is set to the requesting user, not a client-supplied value."""
        response = self.client.post(self.url, self.valid_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        offer = Offer.objects.get(id=response.data["id"])
        self.assertEqual(offer.user, self.business_user)
