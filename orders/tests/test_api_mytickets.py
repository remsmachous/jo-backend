# orders/tests/test_api_mytickets.py
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status

User = get_user_model()

class MyTicketsApiTests(APITestCase):
    def setUp(self):
        # Crée un utilisateur "normal" pour les tests
        username_field = getattr(User, "USERNAME_FIELD", "username")
        common = {
            "password": "Aa1234567890!test",
            "first_name": "U",
            "last_name": "Test",
            "email": "u1@example.com",
        }
        if username_field == "email":
            self.user = User.objects.create_user(email=common["email"], password=common["password"])
            self.login_username = common["email"]
        else:
            self.user = User.objects.create_user(username="user1", email=common["email"], password=common["password"])
            self.login_username = "user1"
        self.password = common["password"]

        # Endpoints (selon ton routeur existant)
        self.url_login = "/api/accounts/login"  # ⚠️ sans slash final, d’après tes URLs
        self.url_my_tickets = "/api/my-tickets/"

    def _get_access_token(self):
        """Helper pour récupérer un jeton d'accès via /login (supporte plusieurs noms de champs)."""
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
        self.fail("Le JSON de /login ne contient pas de jeton (access/access_token/token).")

    def test_mytickets_requires_auth(self):
        """Sans Bearer token → 401 Unauthorized."""
        r = self.client.get(self.url_my_tickets)
        self.assertEqual(r.status_code, status.HTTP_401_UNAUTHORIZED, r.content)

    def test_mytickets_ok_when_authenticated_and_empty(self):
        """
        Avec Bearer token valide → 200 et structure attendue.
        Liste vide si aucun ticket n'existe pour l'utilisateur.
        """
        token = self._get_access_token()
        r = self.client.get(self.url_my_tickets, HTTP_AUTHORIZATION=f"Bearer {token}")
        self.assertEqual(r.status_code, status.HTTP_200_OK, r.content)
        data = r.json()
        # structure minimale
        self.assertIn("count", data)
        self.assertIn("results", data)
        self.assertIsInstance(data["results"], list)
        # pas d'échec si 0 billet
        self.assertGreaterEqual(data["count"], 0)
        self.assertEqual(len(data["results"]), data["count"])
