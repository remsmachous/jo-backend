"""
Fichier : views.py 
Description : Définit les vues de l'API pour la gestion des utilisateurs.
              Utilise les vues génériques de DRF pour plus de concision.
"""
from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from .serializers import RegisterSerializer, UserSerializer

User = get_user_model()

class RegisterView(generics.CreateAPIView):
    """
    Vue pour l'inscription d'un nouvel utilisateur.
    """
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]


class MeView(APIView):
    """
    Vue pour récupérer les informations de l'utilisateur actuellement connecté.
    C'est un endpoint protégé, accessible uniquement avec un token d'authentification valide.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """
        Gère les requêtes GET pour retourner les données de l'utilisateur authentifié.
        """
        serializer = UserSerializer(request.user)
        data = dict(serializer.data)  

        u = request.user
        data.update({
            "is_staff": bool(getattr(u, "is_staff", False)),
            "is_superuser": bool(getattr(u, "is_superuser", False)),
            
            "is_admin": bool(getattr(u, "is_admin", False)),
        })

        return Response(data)
