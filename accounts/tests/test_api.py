# accounts/tests/test_api.py
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status

User = get_user_model()


def _register_payload(i: int):
    """
    Fabrique un payload valide pour /api/accounts/register
    en s'adaptant à USERNAME_FIELD (email ou username).
    """
    username_field = getattr(User, "USERNAME_FIELD", "username")
    base = {
        "password": "Aa1234567890!test",
        "first_name": f"U{i}",
        "last_name": "Test",
    }
    if username_field == "email":
        base["email"] = f"user{i}@example.com"
    else:
        base["username"] = f"user{i}"
        base["email"] = f"user{i}@example.com"  # si votre serializer l'accepte
    return base


class AccountsApiTests(APITestCase):
    def setUp(self):
        # Base URLS — on les écrit en dur car elles existent déjà dans ton router
        self.url_register = "/api/accounts/register"
        self.url_login = "/api/accounts/login"  # sans slash final (cf. ton routeur)
        self.url_me = "/api/accounts/me"

    def _extract_access_token(self, login_json):
        """
        Selon l'implémentation du login, le champ du token peut s'appeler:
        - access (SimpleJWT usage courant)
        - access_token
        - token
        On les essaie dans cet ordre.
        """
        for key in ("access", "access_token", "token"):
            token = login_json.get(key)
            if token:
                return token
        self.fail("Le JSON de /login ne contient pas de jeton (access/access_token/token manquant).")

    def test_register_login_me_happy_path(self):
        # 1) Register
        payload = _register_payload(1)
        r = self.client.post(self.url_register, data=payload, format="json")
        self.assertEqual(r.status_code, status.HTTP_201_CREATED, r.content)

        # 2) Login
        username_field = getattr(User, "USERNAME_FIELD", "username")
        login_body = {
            "username": payload["email" if username_field == "email" else "username"],
            "password": payload["password"],
        }
        r = self.client.post(self.url_login, data=login_body, format="json")
        self.assertEqual(r.status_code, status.HTTP_200_OK, r.content)
        token = self._extract_access_token(r.json())

        # 3) /me avec Bearer token
        r = self.client.get(self.url_me, HTTP_AUTHORIZATION=f"Bearer {token}")
        self.assertEqual(r.status_code, status.HTTP_200_OK, r.content)

        data = r.json()
        # On vérifie que l'identité correspond
        if username_field == "email":
            self.assertEqual(data.get("email"), payload["email"])
        else:
            # on accepte que /me renvoie username et/ou email selon ton serializer
            self.assertIn(data.get("username"), (payload["username"],))
            self.assertEqual(data.get("email"), payload["email"])
        # Les flags admin peuvent exister (pas obligatoires pour cet utilisateur)
        self.assertIn("is_staff", data)
        self.assertIn("is_superuser", data)
