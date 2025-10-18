"""
Fichier : test_offers_permissions.py (application 'offers')
Description : Contient les tests d'intégration pour vérifier les permissions
              d'accès (notamment la création) aux vues de l'API des offres.
              Seuls les utilisateurs administrateurs (is_staff=True) devraient
              être autorisés à créer des offres.
"""
import io
from PIL import Image
import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse

pytestmark = pytest.mark.django_db
User = get_user_model()

def url_list():
    return reverse("offers:offer-list")

# Fonction utilitaire pour créer un fichier image en mémoire (utilisé pour simuler un upload).
def _make_image_file(size=(900, 1225), fmt="PNG"):
    f = io.BytesIO()
    Image.new("RGB", size, (255, 255, 255)).save(f, fmt)
    f.name = "test.png"
    f.seek(0)
    return f

# Teste qu'un utilisateur non authentifié ou non-administrateur ne peut pas créer d'offre.
def test_non_admin_cannot_create_offer(api_client):
    payload = {"name": "Duo", "price": 90, "persons": 2, "is_active": True}
    r = api_client.post(url_list(), payload, format="json")
    assert r.status_code in (401, 403)

# Teste qu'un utilisateur administrateur peut créer une offre.
def test_admin_can_create_offer(api_client, monkeypatch, tmp_path):
    monkeypatch.setenv("FRONT_OFFRES_JS_PATH", str(tmp_path / "offres.js"))

    from offers import api as offers_api
    def _safe_get_image_url(self, obj):
        img = getattr(obj, "image", None)
        if not img:
            return None
        try:
            url = img.url
        except Exception:
            return None
        request = self.context.get("request")
        return request.build_absolute_uri(url) if request else url
    monkeypatch.setattr(offers_api.OfferSerializer, "get_image_url", _safe_get_image_url, raising=False)

    admin = User.objects.create_user(username="admin", email="a@a.a", password="x", is_staff=True)
    api_client.force_authenticate(user=admin)

    payload = {"name": "Duo", "price": 90, "persons": 2, "is_active": True}
    r = api_client.post(url_list(), data=payload, format="json")
    assert r.status_code in (200, 201)
    data = r.json()
    assert data["name"] == "Duo"
    assert data["slug"] and data["titre"]
    assert "image_url" in data
