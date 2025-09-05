# orders/tests/test_api_checkout_verify.py
from django.contrib.auth import get_user_model
from django.core.signing import dumps  # ✅ on utilise le signer Django
from rest_framework.test import APITestCase
from rest_framework import status

from offers.models import Offer

User = get_user_model()


class CheckoutVerifyApiTests(APITestCase):
    def setUp(self):
        # Crée un utilisateur
        username_field = getattr(User, "USERNAME_FIELD", "username")
        if username_field == "email":
            self.user = User.objects.create_user(email="buyer@example.com", password="Aa1234567890!test")
            self.login_username = "buyer@example.com"
        else:
            self.user = User.objects.create_user(username="buyer", email="buyer@example.com", password="Aa1234567890!test")
            self.login_username = "buyer"
        self.password = "Aa1234567890!test"

        # Une offre pour composer le panier
        self.offer = Offer.objects.create(
            name="Solo",
            slug="solo",
            description="Billet solo",
            price="49.00",
            persons=1,
            is_active=True,
        )

        # Endpoints
        self.url_login = "/api/accounts/login"
        self.url_reservations = "/api/reservations"
        self.url_checkout = "/api/checkout"
        self.url_verify = "/api/verify"

    def _get_access_token(self):
        r = self.client.post(
            self.url_login,
            data={"username": self.login_username, "password": self.password},
            format="json",
        )
        self.assertEqual(r.status_code, status.HTTP_200_OK, r.content)
        data = r.json()
        for k in ("access", "access_token", "token"):
            if data.get(k):
                return data[k]
        self.fail("Login n’a pas renvoyé de jeton.")

    def test_checkout_then_verify_happy_path(self):
        token = self._get_access_token()
        auth = {"HTTP_AUTHORIZATION": f"Bearer {token}"}

        # 1) Création réservation (schéma FR)
        reservation_payload = {
            "client": {"prenom": "Alice", "nom": "Buyer", "email": "buyer@example.com"},
            "panier": [{"id": self.offer.id, "titre": self.offer.name, "prix": 49.00, "qty": 2}],
            "total": "98.00",
            "places": 2,
        }
        r = self.client.post(self.url_reservations, data=reservation_payload, format="json", **auth)
        self.assertEqual(r.status_code, status.HTTP_201_CREATED, r.content)
        reservation_id = r.json().get("reservation_id")
        self.assertIsNotNone(reservation_id)

        # 2) Checkout -> création ticket
        r = self.client.post(self.url_checkout, data={"reservation_id": reservation_id}, format="json", **auth)
        self.assertEqual(r.status_code, status.HTTP_201_CREATED, r.content)
        ticket_id = r.json()["ticket"]["id"]

        # 3) Générer le même token signé que la vue debug /opaque (dumps(..., salt="ticket"))
        payload = {"tid": ticket_id, "rid": reservation_id, "uid": self.user.id}
        signed_token = dumps(payload, salt="ticket")

        # 4) Vérifier via /verify
        r = self.client.post(self.url_verify, data={"token": signed_token}, format="json")
        self.assertEqual(r.status_code, status.HTTP_200_OK, r.content)
        body = r.json()
        self.assertTrue(body.get("valid") is True, f"Ticket devrait être valide, reçu: {body}")
        self.assertEqual(body["meta"]["ticket_id"], ticket_id)
        self.assertEqual(body["meta"]["reservation_id"], reservation_id)
        self.assertEqual(body["meta"]["user_id"], self.user.id)
