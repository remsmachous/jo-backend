"""
Fichier : test_utils_qr.py (application 'orders')
Description : Contient les tests unitaires pour les fonctions utilitaires,
              notamment la génération d'images de code QR pour les tickets.
"""
import os
import pytest
from django.contrib.auth import get_user_model
from orders.models import Reservation, Ticket
from orders.utils import generate_ticket_qr_image

pytestmark = pytest.mark.django_db
User = get_user_model()

# Teste la fonction de génération du QRCode du ticket.
def test_generate_ticket_qr_image_creates_png(settings, tmp_path):
    user = User.objects.create_user(username="gina", password="x")
    res = Reservation.objects.create(user=user, client_nom="N", client_prenom="P",
                                     client_email="e@e.com", total="10.00", places=1)
    t = Ticket.objects.create(user=user, reservation=res, ticket_key="k"*64, qr_image="")
    rel = generate_ticket_qr_image(t)
    full_path = tmp_path / "media" / rel 
    assert rel.startswith("tickets/") and rel.endswith(".png")
