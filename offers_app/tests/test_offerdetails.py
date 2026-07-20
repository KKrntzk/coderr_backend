from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from offers_app.models import Feature, Offer, OfferDetail

User = get_user_model()


class OfferDetailRetrieveViewTest(APITestCase):
    """Tests for GET /api/offerdetails/{id}/."""

    def setUp(self):
        """Create an offer detail with two features."""
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
        self.offer_detail = OfferDetail.objects.create(
            offer=self.offer,
            title="Basic Design",
            revisions=2,
            delivery_time_in_days=5,
            price=100,
            offer_type="basic",
        )
        Feature.objects.create(offer_detail=self.offer_detail, name="Logo Design")
        Feature.objects.create(offer_detail=self.offer_detail, name="Visitenkarte")
        self.url = reverse("offerdetail-retrieve", kwargs={"pk": self.offer_detail.pk})

    def test_get_offerdetail_success(self):
        """An existing offer detail is retrieved with its core fields."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.offer_detail.id)
        self.assertEqual(response.data["title"], "Basic Design")
        self.assertEqual(response.data["offer_type"], "basic")

    def test_get_offerdetail_features(self):
        """The response includes all feature names as a flat list."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("Logo Design", response.data["features"])
        self.assertIn("Visitenkarte", response.data["features"])

    def test_get_offerdetail_contains_required_fields(self):
        """The response contains all fields required by the specification."""
        response = self.client.get(self.url)
        self.assertIn("id", response.data)
        self.assertIn("title", response.data)
        self.assertIn("revisions", response.data)
        self.assertIn("delivery_time_in_days", response.data)
        self.assertIn("price", response.data)
        self.assertIn("features", response.data)
        self.assertIn("offer_type", response.data)

    def test_get_offerdetail_not_found(self):
        """A non-existent offer detail id returns a 404."""
        url = reverse("offerdetail-retrieve", kwargs={"pk": 9999})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_offerdetail_unauthenticated(self):
        """An unauthenticated request is rejected with a 401."""
        self.client.credentials()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
