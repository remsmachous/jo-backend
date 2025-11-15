"""
Fichier : test_verify_and_my_tickets.py (application 'orders')
Description : Contient les tests d'intégration pour les vues de vérification
              de ticket (verify_ticket) et de liste des tickets de l'utilisateur
              (my_tickets) de l'application 'orders'.
"""
import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.signing import dumps
from orders.models import Ticket

pytestmark = pytest.mark.django_db
User = get_user_model()

def u(name): return reverse(f"orders:{name}")

# Fonction utilitaire pour créer une réservation et la finalise (checkout),
# ce qui génère un Ticket.
def create_paid_ticket(api_client):
    user = User.objects.create_user(username="frank", email="f@e.com", password="x")
    api_client.force_authenticate(user=user)
    payload = {
        "client": {"nom": "Doe", "prenom": "John", "email": "john@example.com"},
        "panier": [{"id": "offer_1", "titre": "Solo", "prix": "10.00", "qty": 1}],
        "total": "10.00",
        "places": 1,
    }
    r1 = api_client.post(u("reservation_create"), payload, format="json")
    rid = r1.json()["reservation_id"]
    r2 = api_client.post(u("checkout"), {"reservation_id": rid}, format="json")
    tid = r2.json()["ticket"]["id"]
    ticket = Ticket.objects.get(id=tid)
    return user, ticket

# Teste la vérification réussie d'un ticket valide.
def test_verify_ticket_ok(api_client):
    user, ticket = create_paid_ticket(api_client) 
    signed = dumps({"tid": ticket.id, "rid": ticket.reservation_id, "uid": ticket.user_id}, salt="ticket")
    r = api_client.post(u("verify_ticket"), {"qr": f"jo://ticket/{signed}"}, format="json")
    assert r.status_code == 200
    body = r.json()
    assert body["valid"] is True
    assert body["meta"]["ticket_id"] == ticket.id
    assert body["meta"]["reservation_id"] == ticket.reservation_id
    assert body["meta"]["user_id"] == ticket.user_id

# Teste le rejet d'un ticket avec une mauvaise signature.
def test_verify_ticket_bad_signature(api_client):
    r = api_client.post(u("verify_ticket"), {"token": "not-a-real-token"}, format="json")
    assert r.status_code == 200
    assert r.json()["valid"] is False

# Teste la vue listant tous les tickets de l'utilisateur.
def test_my_tickets_lists_results_with_qr_url(api_client):
    user, ticket = create_paid_ticket(api_client)
    api_client.force_authenticate(user=user)
    r = api_client.get(u("my_tickets"))
    assert r.status_code == 200
    data = r.json()
    assert data["count"] >= 1 
    assert any(it.get("qr_url") for it in data["results"])
