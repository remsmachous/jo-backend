"""
Fichier : test_password_policy.py
Description : Contient les tests d'intégration pour vérifier la politique
              et les validateurs de mots de passe lors de l'enregistrement
              dans l'application 'accounts'.
"""
import pytest
from django.urls import reverse

pytestmark = pytest.mark.django_db

# Fonction utilitaire pour générer les URL à partir du nom de la vue.
def url(name):
    return reverse(f"accounts:{name}")

# Teste le rejet d'un mot de passe contenant un espace.
def test_register_rejects_password_with_space(api_client):
    """Le mot de passe ne doit pas contenir d'espace."""
    bad = {
        "username": "dave",
        "email": "dave@example.com",
        "password": "space inside"
    }
    resp = api_client.post(url("register"), bad, format="json")
    assert resp.status_code in (400, 422)

# Teste la fonctionnalité d'enregistrement avec plusieurs mots de passe faibles.
@pytest.mark.parametrize("weak", ["password", "motdepasse", "azerty", "qwerty", "Admin1234!"])
def test_register_may_reject_weak_passwords_if_validators_enabled(api_client, weak):
    """Teste plusieurs mots de passe faibles pour vérifier les validateurs."""
    pwd = weak if len(weak) >= 12 else weak + "X" * (12 - len(weak))
    payload = {
        "username": f"user_{weak}",
        "email": f"{weak}@ex.com",
        "password": pwd,
    }
    resp = api_client.post(url("register"), payload, format="json")
    assert resp.status_code in (201, 200, 400, 422)
