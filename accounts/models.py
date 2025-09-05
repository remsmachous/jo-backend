"""
Fichier : models.py (application 'accounts')
Description : Définit les modèles de base de données personnalisés pour
              cette application.
"""

from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    # Ajout d'un champ 'account_key' pour stocker une clé serveur.
    account_key = models.CharField(
        max_length=64,
        unique=True,
        null=True,        
        blank=True,
        editable=False,
        help_text="Clé serveur secrète générée automatiquement."
    )
