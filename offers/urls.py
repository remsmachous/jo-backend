"""
Fichier : urls.py (application 'offers')
Description : Définit les routes de l'API pour les offres.
              Utilise un routeur de DRF pour générer automatiquement
              toutes les URL nécessaires pour le ViewSet.
"""
app_name = "offers"
from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .api import OfferViewSet

# Crée une instance du routeur par défaut de DRF.
router = DefaultRouter()

# Enregistre le OfferViewSet avec le routeur.
router.register(r"offers", OfferViewSet, basename="offer")

urlpatterns = router.urls

