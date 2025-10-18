"""
Fichier : test_checkout_and_ticket.py (application 'orders')
Description : Contient les tests d'intégration pour la vue de 'checkout' (paiement/validation
              de la réservation) qui crée un Ticket et un code QR associé.
              Ces tests vérifient la génération du ticket, l'idempotence et la robustesse
              face à un utilisateur sans clé de compte (account_key).
"""
import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from orders.models import Reservation, Ticket

pytestmark = pytest.mark.django_db
User = get_user_model()

def u(name): return reverse(f"orders:{name}")

# Fonction utilitaire pour créer une réservation valide nécessaire aux tests de checkout.
def make_reservation(api_client, user):
    api_client.force_authenticate(user=user)
    payload = {
        "client": {"nom": "Doe", "prenom": "Jane", "email": "jane@example.com"},
        "panier": [{"id": "offer_1", "titre": "Solo", "prix": "10.00", "qty": 1}],
        "total": "10.00",
        "places": 1,
    }
    r = api_client.post(u("reservation_create"), payload, format="json")
    assert r.status_code == 201
    return r.json()["reservation_id"]

# Teste que la finalisation de la commande (checkout) génère un Ticket et un code QR.
def test_checkout_generates_ticket_and_qr(api_client, tmp_path, monkeypatch):
    user = User.objects.create_user(username="carol", email="c@e.com", password="x")
    rid = make_reservation(api_client, user)

    assert getattr(User.objects.get(username="carol"), "account_key", None)

    r = api_client.post(u("checkout"), {"reservation_id": rid}, format="json")
    assert r.status_code == 201
    body = r.json()
    assert body["status"] == "paid"
    t = Ticket.objects.get(id=body["ticket"]["id"])
    assert body["ticket"]["qr_url"]
    assert t.qr_image and str(t.qr_image.name).endswith(".png")

# Teste que la finalisation de la commande est idempotente.
def test_checkout_is_idempotent(api_client):
    user = User.objects.create_user(username="dave", email="d@e.com", password="x")
    rid = make_reservation(api_client, user)
    first = api_client.post(u("checkout"), {"reservation_id": rid}, format="json")
    assert first.status_code == 201
    second = api_client.post(u("checkout"), {"reservation_id": rid}, format="json")
    assert second.status_code == 409
    assert second.json()["status"] == "already_paid"

def test_checkout_handles_missing_account_key_gracefully(api_client):
    user = User.objects.create_user(username="eve", email="e@e.com", password="x")
    user_obj = User.objects.get(username="eve")
    user_obj.account_key = None
    user_obj.save(update_fields=["account_key"])

    rid = make_reservation(api_client, user)
    r = api_client.post(u("checkout"), {"reservation_id": rid}, format="json")
    assert r.status_code == 201
    body = r.json()
    assert body.get("status") == "paid"
    assert body.get("ticket") and body["ticket"].get("id") and body["ticket"].get("qr_url")
    
