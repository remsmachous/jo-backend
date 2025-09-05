"""
Fichier : urls.py (projet 'jo_backend')
Description : Fichier de configuration principal des URL pour l'ensemble du projet.
              Il agit comme un routeur qui délègue les requêtes API aux
              applications concernées (accounts, orders, offers).
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)
from django.http import JsonResponse
from django.conf import settings
from django.conf.urls.static import static
from django.urls import re_path
from django.views.static import serve


def health(_request):
    """
    Vue simple pour vérifier l'état de santé de l'API.
    Utile pour les services de monitoring.
    """
    return JsonResponse({"status": "ok", "service": "jo_backend", "version": "0.1.0"}, status=200)

# Liste des routes principales du projet.
urlpatterns = [
     # Route pour l'interface d'administration de Django.
    path("admin/", admin.site.urls),
    # Route pour le "health check" de l'API.
    path("api/health", health, name="health"),   
    path("api/health/", health, name="health_s"),
    # Délègue toutes les URL commençant par /api/accounts/
    # à l'application 'accounts'.
    path("api/accounts/", include("accounts.urls")),
    # Délègue les URL commençant par /api/ aux applications
    # 'orders' et 'offers'.
    path("api/", include("orders.urls")),
    path("api/", include("offers.urls")),
    re_path(r"^media/(?P<path>.*)$", serve, {"document_root": settings.MEDIA_ROOT}),

    # JWT (SimpleJWT)
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/token/verify/", TokenVerifyView.as_view(), name="token_verify"),
]

# Ajoute les routes pour servir les fichiers media (images uploadées)
# uniquement en mode DÉVELOPPEMENT.
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

