"""
Fichier : test_offers_api.py (application 'offers')
Description : Contient les tests d'intégration pour l'API des offres (CRUD,
              filtrage, vérification des champs, etc.).
"""
import io
from PIL import Image
import pytest
from django.urls import reverse
from offers.models import Offer

pytestmark = pytest.mark.django_db

def url_list():
    return reverse("offers:offer-list")

# Fonction utilitaire pour créer un fichier image en mémoire.
def _make_image_file(size=(900, 1225), fmt="PNG"):
    """Crée une image en mémoire avec les dimensions attendues par le modèle (900x1225)."""
    file = io.BytesIO()
    img = Image.new("RGB", size, (255, 255, 255))
    img.save(file, fmt)
    file.name = "test.png"
    file.seek(0)
    return file

# Teste que la liste publique des offres n'affiche que les offres actives.
def test_public_list_shows_only_active(api_client, monkeypatch, tmp_path):
    monkeypatch.setenv("FRONT_OFFRES_JS_PATH", str(tmp_path / "offres.js"))

    active = Offer.objects.create(name="Solo A", price=25, persons=1, is_active=True)
    active.image.save("ok.png", _make_image_file())  

    Offer.objects.create(name="Duo B", price=40, persons=2, is_active=False)

    resp = api_client.get(url_list())
    assert resp.status_code == 200
    data = resp.json()

    assert any(o["name"] == "Solo A" for o in data)
    assert all(o["is_active"] for o in data)

    solo = next(o for o in data if o["name"] == "Solo A")
    assert "image_url" in solo and solo["image_url"]
