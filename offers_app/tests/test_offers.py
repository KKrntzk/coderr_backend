from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model
from offers_app.models import Offer, OfferDetail, Feature

User = get_user_model()


class OfferListViewTest(APITestCase):

    def setUp(self):
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
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 2)

    def test_get_offer_list_paginated(self):
        response = self.client.get(self.url)
        self.assertIn("count", response.data)
        self.assertIn("next", response.data)
        self.assertIn("previous", response.data)
        self.assertIn("results", response.data)

    def test_get_offer_list_no_auth_required(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_filter_by_creator_id(self):
        response = self.client.get(self.url, {"creator_id": self.business_user.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["user"], self.business_user.id)

    def test_filter_by_min_price(self):
        response = self.client.get(self.url, {"min_price": 75})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["min_price"], 100)

    def test_filter_by_max_delivery_time(self):
        response = self.client.get(self.url, {"max_delivery_time": 5})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["min_delivery_time"], 3)

    def test_search_by_title(self):
        response = self.client.get(self.url, {"search": "Website"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["title"], "Website Design")

    def test_ordering_by_min_price(self):
        response = self.client.get(self.url, {"ordering": "min_price"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        prices = [r["min_price"] for r in response.data["results"]]
        self.assertEqual(prices, sorted(prices))

    def test_offer_contains_required_fields(self):
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

    def setUp(self):
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
        response = self.client.post(self.url, self.valid_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["title"], "Grafikdesign-Paket")
        self.assertEqual(len(response.data["details"]), 3)

    def test_create_offer_features_saved(self):
        response = self.client.post(self.url, self.valid_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        basic_detail = next(
            d for d in response.data["details"] if d["offer_type"] == "basic"
        )
        self.assertIn("Logo Design", basic_detail["features"])
        self.assertIn("Visitenkarte", basic_detail["features"])

    def test_create_offer_missing_details(self):
        data = self.valid_data.copy()
        data["details"] = data["details"][:2]
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_offer_wrong_offer_types(self):
        data = self.valid_data.copy()
        data["details"][0]["offer_type"] = "basic"
        data["details"][1]["offer_type"] = "basic"
        data["details"][2]["offer_type"] = "basic"
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_offer_customer_forbidden(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.customer_token.key)
        response = self.client.post(self.url, self.valid_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_offer_unauthenticated(self):
        self.client.credentials()
        response = self.client.post(self.url, self.valid_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_offer_user_set_automatically(self):
        response = self.client.post(self.url, self.valid_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        offer = Offer.objects.get(id=response.data["id"])
        self.assertEqual(offer.user, self.business_user)


class OfferRetrieveViewTest(APITestCase):

    def setUp(self):
        self.business_user = User.objects.create_user(
            username="testbusiness",
            email="business@mail.de",
            password="testpassword123",
            type="business",
        )
        self.token = Token.objects.create(user=self.business_user)
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token.key)
        self.offer = Offer.objects.create(
            user=self.business_user,
            title="Website Design",
            description="Professionelles Website-Design",
        )
        self.detail = OfferDetail.objects.create(
            offer=self.offer,
            title="Basic",
            revisions=2,
            delivery_time_in_days=7,
            price=100,
            offer_type="basic",
        )
        self.url = reverse("offer-retrieve", kwargs={"pk": self.offer.pk})

    def test_get_offer_success(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.offer.id)
        self.assertEqual(response.data["title"], "Website Design")
        self.assertEqual(response.data["user"], self.business_user.id)

    def test_get_offer_contains_required_fields(self):
        response = self.client.get(self.url)
        self.assertIn("id", response.data)
        self.assertIn("user", response.data)
        self.assertIn("title", response.data)
        self.assertIn("description", response.data)
        self.assertIn("details", response.data)
        self.assertIn("min_price", response.data)
        self.assertIn("min_delivery_time", response.data)
        self.assertNotIn("user_details", response.data)

    def test_get_offer_details_contain_url(self):
        response = self.client.get(self.url)
        self.assertEqual(len(response.data["details"]), 1)
        self.assertIn("id", response.data["details"][0])
        self.assertIn("url", response.data["details"][0])

    def test_get_offer_not_found(self):
        url = reverse("offer-retrieve", kwargs={"pk": 9999})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_offer_unauthenticated(self):
        self.client.credentials()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_offer_min_price(self):
        response = self.client.get(self.url)
        self.assertEqual(response.data["min_price"], 100)

    def test_get_offer_min_delivery_time(self):
        response = self.client.get(self.url)
        self.assertEqual(response.data["min_delivery_time"], 7)
