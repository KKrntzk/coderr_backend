from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model
from offers_app.models import Offer, OfferDetail, Feature

User = get_user_model()


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
        self.url = reverse("offer-retrieve-update", kwargs={"pk": self.offer.pk})

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
        url = reverse("offer-retrieve-update", kwargs={"pk": 9999})
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


class OfferUpdateViewTest(APITestCase):

    def setUp(self):
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
        self.token = Token.objects.create(user=self.business_user)
        self.other_token = Token.objects.create(user=self.other_business)
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token.key)
        self.offer = Offer.objects.create(
            user=self.business_user,
            title="Website Design",
            description="Professionelles Website-Design",
        )
        self.basic_detail = OfferDetail.objects.create(
            offer=self.offer,
            title="Basic",
            revisions=2,
            delivery_time_in_days=7,
            price=100,
            offer_type="basic",
        )
        self.standard_detail = OfferDetail.objects.create(
            offer=self.offer,
            title="Standard",
            revisions=5,
            delivery_time_in_days=10,
            price=200,
            offer_type="standard",
        )
        self.premium_detail = OfferDetail.objects.create(
            offer=self.offer,
            title="Premium",
            revisions=10,
            delivery_time_in_days=14,
            price=500,
            offer_type="premium",
        )
        self.url = reverse("offer-retrieve-update", kwargs={"pk": self.offer.pk})

    def test_patch_offer_title_success(self):
        response = self.client.patch(
            self.url,
            {
                "title": "Updated Website Design",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "Updated Website Design")

    def test_patch_offer_detail_success(self):
        response = self.client.patch(
            self.url,
            {
                "details": [
                    {
                        "title": "Basic Updated",
                        "revisions": 3,
                        "delivery_time_in_days": 6,
                        "price": 120,
                        "features": ["Logo Design", "Flyer"],
                        "offer_type": "basic",
                    }
                ]
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        basic = next(d for d in response.data["details"] if d["offer_type"] == "basic")
        self.assertEqual(basic["title"], "Basic Updated")
        self.assertEqual(str(basic["price"]), "120.00")
        self.assertIn("Logo Design", basic["features"])

    def test_patch_offer_detail_id_unchanged(self):
        response = self.client.patch(
            self.url,
            {
                "details": [
                    {
                        "title": "Basic Updated",
                        "revisions": 3,
                        "delivery_time_in_days": 6,
                        "price": 120,
                        "features": [],
                        "offer_type": "basic",
                    }
                ]
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        basic = next(d for d in response.data["details"] if d["offer_type"] == "basic")
        self.assertEqual(basic["id"], self.basic_detail.id)

    def test_patch_offer_not_owner(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.other_token.key)
        response = self.client.patch(
            self.url,
            {
                "title": "Hacker",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_patch_offer_unauthenticated(self):
        self.client.credentials()
        response = self.client.patch(
            self.url,
            {
                "title": "Hacker",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_patch_offer_not_found(self):
        url = reverse("offer-retrieve-update", kwargs={"pk": 9999})
        response = self.client.patch(
            url,
            {
                "title": "Test",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_patch_offer_other_details_unchanged(self):
        response = self.client.patch(
            self.url,
            {
                "details": [
                    {
                        "title": "Basic Updated",
                        "revisions": 3,
                        "delivery_time_in_days": 6,
                        "price": 120,
                        "features": [],
                        "offer_type": "basic",
                    }
                ]
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        standard = next(
            d for d in response.data["details"] if d["offer_type"] == "standard"
        )
        self.assertEqual(standard["title"], "Standard")
        self.assertEqual(str(standard["price"]), "200.00")
