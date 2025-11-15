"""
Fichier : test_offers_model.py (application 'offers')
Description : Contient les tests unitaires pour le modèle Offer,
              y compris la vérification des méthodes de sauvegarde
              automatique et la validation des champs (ex: dimensions d'image).
"""
import io
import pytest
from PIL import Image
from django.core.exceptions import ValidationError
from offers.models import Offer

pytestmark = pytest.mark.django_db

# Teste que les champs 'slug' et 'titre' sont automatiquement remplis lors de la sauvegarde.
def test_slug_and_titre_autofill_on_save():
    o = Offer(name="Famille Max", price=120, persons=4, is_active=True)
    o.save()
    assert o.slug == "famille-max"  
    assert o.titre == "Famille Max" 

# Fonction utilitaire pour créer un fichier image en mémoire.
def _make_image_file(size=(100, 100), fmt="PNG"):
    file = io.BytesIO()
    img = Image.new("RGB", size, (255, 255, 255))
    img.save(file, fmt)
    file.name = "test.png"
    file.seek(0)
    return file

# Teste la validation des dimensions d'image (rejet si les dimensions sont incorrectes).
def test_image_dimension_validation():
    bad_img = _make_image_file(size=(900, 900))
    o = Offer(name="Solo Img", price=10, persons=1, is_active=True)

    with pytest.raises(ValidationError):
        o.image.save("bad.png", bad_img)

# Teste que le modèle accepte les dimensions d'image correctes.
def test_image_accepts_exact_dimension():
    good_img = _make_image_file(size=(900, 1225))
    o = Offer(name="Solo Img OK", price=10, persons=1, is_active=True)
    o.image.save("ok.png", good_img)
    o.save()
