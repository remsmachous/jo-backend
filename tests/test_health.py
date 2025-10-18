"""
Fichier : test_health.py
Description : Contient le test unitaire pour la vue de vérification
              de l'état de santé de l'API (/api/health).
"""
import pytest
from django.test import Client

@pytest.mark.django_db
def test_health_check_ok():
    """
    Teste que les endpoints de vérification de santé répondent avec succès (HTTP 200)
    et retournent le statut "ok".
    """
    c = Client()
    r1 = c.get("/api/health")
    r2 = c.get("/api/health/")
    assert r1.status_code == 200 and r2.status_code == 200
    assert r1.json().get("status") == "ok"
