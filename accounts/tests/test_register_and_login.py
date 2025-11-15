"""
Fichier : test_register_and_login.py
Description : Contient les tests d'intégration pour les vues d'enregistrement
              et de connexion (login) de l'application 'accounts'.
"""
import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model

pytestmark = pytest.mark.django_db
User = get_user_model()

# Fonction utilitaire pour générer les URL à partir du nom de la vue.
def url(name: str) -> str:
    return reverse(f"accounts:{name}")

# Teste la fonctionnalité d'enregistrement d'un nouvel utilisateur.
def test_register_returns_tokens_and_creates_user(api_client):
    payload = {
        "username": "ada",
        "email": "ada@example.com",
        "password": "VeryStr0ng!Pass",
    }
    resp = api_client.post(url("register"), payload, format="json")
    assert resp.status_code in (200, 201)
    data = resp.json()
    assert "tokens" in data and "access" in data["tokens"] and "refresh" in data["tokens"]
    assert User.objects.filter(username="ada").exists()

# Teste la fonctionnalité de connexion d'un utilisateur existant.
def test_login_returns_jwt_tokens(api_client):
    User.objects.create_user(username="bob", email="bob@example.com", password="S3cure!Pass")
    resp = api_client.post(url("login"), {"username": "bob", "password": "S3cure!Pass"}, format="json")
    assert resp.status_code == 200
    data = resp.json()
    assert "access" in data and "refresh" in data

# Teste la vue 'me' (profil utilisateur actuel).
def test_me_requires_auth_then_returns_profile(api_client):
    r = api_client.get(url("me"))
    assert r.status_code in (401, 403)

    User.objects.create_user(username="carol", email="carol@example.com", password="S3cure!Pass")
    tokens = api_client.post(url("login"), {"username": "carol", "password": "S3cure!Pass"}, format="json").json()
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {tokens['access']}")
    me = api_client.get(url("me"))
    assert me.status_code == 200
    body = me.json()
    assert body["username"] == "carol"
    assert "is_staff" in body and "is_superuser" in body and "is_admin" in body
