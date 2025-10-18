"""
Fichier : conftest.py
Description : Fichier de configuration et de définition des fixtures
              globales pour pytest. Les fixtures définies ici sont
              automatiquement découvertes par pytest.
"""

import pytest
from django.conf import settings
from rest_framework.test import APIClient

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture(autouse=True)
def _tmp_media(tmp_path, monkeypatch):
    # Crée un sous-répertoire 'media' dans le répertoire temporaire.
    tmp_media = tmp_path / "media"
    tmp_media.mkdir(parents=True, exist_ok=True)
    # Modifie temporairement la variable `MEDIA_ROOT` des paramètres Django
    monkeypatch.setattr(settings, "MEDIA_ROOT", str(tmp_media))
    return tmp_media
