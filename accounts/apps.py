"""
Fichier : apps.py (application 'accounts')
Description : Fichier de configuration pour l'application Django 'accounts'.
Permet de définir les métadonnées de l'application et d'exécuter
du code au démarrage, comme l'enregistrement des signaux.
"""

from django.apps import AppConfig

class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'accounts'

    def ready(self):
        from . import signals  