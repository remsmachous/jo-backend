"""
Fichier : serializers.py
Description : Contient les serializers pour gérer la conversion des données
              entre les modèles Django et le format JSON pour l'API.
              Gère également la validation des données d'inscription.
"""

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
    """
    Serializer pour l'inscription d'un nouvel utilisateur.
    Valide les données, crée l'utilisateur, et retourne les données de
    l'utilisateur avec les tokens JWT (access et refresh).
    """
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ("id", "username", "email", "password")

    def validate_password(self, value):
        """
        Valide la force du mot de passe en utilisant les validateurs de Django
        et ajoute une règle personnalisée pour interdire les espaces.
        """
        validate_password(value)
        if " " in value:
            raise serializers.ValidationError("Le mot de passe ne doit pas contenir d'espaces.")
        return value

    def create(self, validated_data):
        """
        Crée une nouvelle instance de User en s'assurant que le mot de passe
        est correctement hashé.
        """
        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data.get("email", ""),
            password=validated_data["password"],
        )
        return user

    def to_representation(self, instance):
        """
        Modifie la représentation finale de l'objet après la création.
        Ajoute les tokens JWT à la réponse JSON.
        """
        data = super().to_representation(instance)
        refresh = RefreshToken.for_user(instance)
        data["tokens"] = {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }
        return data


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer simple pour afficher les informations publiques d'un utilisateur.
    Utilisé pour ne pas exposer d'informations sensibles comme le mot de passe.
    """
    class Meta:
        model = User
        fields = ("id", "username", "email")
