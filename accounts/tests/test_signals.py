"""
Fichier : test_signals.py
Description : Contient les tests unitaires pour les signaux Django,
              en particulier ceux qui sont déclenchés lors de la création
              d'un utilisateur dans l'application 'accounts'.
"""
import pytest
from django.contrib.auth import get_user_model

pytestmark = pytest.mark.django_db
User = get_user_model()

# Teste si une clé de compte est générée automatiquement lors de la création d'un utilisateur.
def test_account_key_generated_on_user_create():
    u = User.objects.create_user(username="zoe", email="zoe@example.com", password="S3cure!Pass")
    assert u.account_key and isinstance(u.account_key, str) and len(u.account_key) >= 64
