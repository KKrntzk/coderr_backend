from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from offers_app.models import Offer, OfferDetail

User = get_user_model()


class OfferRetrieveViewTest(APITestCase):
    """Tests for GET /api/offers/{id}/."""

    def setUp(self):
        """Create a business user with one offer and one detail."""
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
        """An existing offer is retrieved with its core fields."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.offer.id)
        self.assertEqual(response.data["title"], "Website Design")
        self.assertEqual(response.data["user"], self.business_user.id)

    def test_get_offer_contains_required_fields(self):
        """The response contains all expected fields but not user_details."""
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
        """Each nested detail exposes its id and resource url."""
        response = self.client.get(self.url)
        self.assertEqual(len(response.data["details"]), 1)
        self.assertIn("id", response.data["details"][0])
        self.assertIn("url", response.data["details"][0])

    def test_get_offer_not_found(self):
        """A non-existent offer id returns a 404."""
        url = reverse("offer-retrieve-update", kwargs={"pk": 9999})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_offer_unauthenticated(self):
        """An unauthenticated request is rejected with a 401."""
        self.client.credentials()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_offer_min_price(self):
        """The min_price field reflects the cheapest detail."""
        response = self.client.get(self.url)
        self.assertEqual(response.data["min_price"], 100)

    def test_get_offer_min_delivery_time(self):
        """The min_delivery_time field reflects the fastest detail."""
        response = self.client.get(self.url)
        self.assertEqual(response.data["min_delivery_time"], 7)


class OfferUpdateViewTest(APITestCase):
    """Tests for PATCH /api/offers/{id}/."""

    def setUp(self):
        """Create an offer with all three detail tiers, owned by a business user."""
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
        """Updating only the title leaves the response with the new value."""
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
        """Updating a detail by offer_type changes its fields and features."""
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
        """Updating a detail keeps its original id."""
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
        """A user who does not own the offer is rejected with a 403."""
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
        """An unauthenticated request is rejected with a 401."""
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
        """A non-existent offer id returns a 404."""
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
        """Updating one detail leaves the other tiers untouched."""
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

    def test_patch_offer_detail_without_offer_type(self):
        """A detail without an offer_type is rejected with a 400."""
        response = self.client.patch(
            self.url,
            {
                "details": [
                    {
                        "title": "Basic Updated",
                        "price": 120,
                    }
                ]
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class OfferDeleteViewTest(APITestCase):
    """Tests for DELETE /api/offers/{id}/."""

    def setUp(self):
        """Create an offer owned by a business user, plus a second business user."""
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
        self.url = reverse("offer-retrieve-update", kwargs={"pk": self.offer.pk})

    def test_delete_offer_success(self):
        """The owner can delete their offer, which is then removed from the DB."""
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Offer.objects.filter(pk=self.offer.pk).exists())

    def test_delete_offer_not_owner(self):
        """A non-owner is rejected with a 403 and the offer remains."""
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.other_token.key)
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Offer.objects.filter(pk=self.offer.pk).exists())

    def test_delete_offer_unauthenticated(self):
        """An unauthenticated request is rejected with a 401 and the offer remains."""
        self.client.credentials()
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertTrue(Offer.objects.filter(pk=self.offer.pk).exists())

    def test_delete_offer_not_found(self):
        """A non-existent offer id returns a 404."""
        url = reverse("offer-retrieve-update", kwargs={"pk": 9999})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
