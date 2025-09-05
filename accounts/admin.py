"""
Fichier : admin.py (application 'accounts')
Description : Personnalise l'affichage des modèles de cette application
             dans l'interface d'administration de Django.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

@admin.register(User)

class CustomUserAdmin(UserAdmin):
    """
        Personnalise l'affichage du modèle User personnalisé dans l'admin.
        Ajoute simplement l'affichage de notre champ personnalisé `account_key`.
    """
    readonly_fields = getattr(UserAdmin, "readonly_fields", tuple()) + ("account_key",)
    fieldsets = UserAdmin.fieldsets + (
        ("Clés serveur", {"fields": ("account_key",)}),
    )