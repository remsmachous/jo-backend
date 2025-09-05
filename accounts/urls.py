"""
Fichier : urls.py
Description : Définit les routes de l'API pour l'authentification
              et la gestion des utilisateurs.
"""

from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import RegisterView, MeView

urlpatterns = [
     # Endpoint pour l'inscription d'un nouvel utilisateur.
    path("register", RegisterView.as_view(), name="register"),
     # Endpoint pour la connexion
    path("login", TokenObtainPairView.as_view(), name="login"),
    # Endpoint pour rafraîchir un token d'accès expiré en utilisant
    # un token de rafraîchissement valide.    
    path("token/refresh", TokenRefreshView.as_view(), name="token_refresh"),
    # Endpoint protégé pour récupérer les informations de l'utilisateur
    # actuellement authentifié    
    path("me", MeView.as_view(), name="me"),
]
