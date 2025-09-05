"""
Fichier : apps.py (application 'offers')
Description : Fichier de configuration pour l'application Django 'offers'.
"""
from django.apps import AppConfig


class OffersConfig(AppConfig):
    """
    Configuration de l'application 'offers'.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'offers'

    def ready(self):
        """
        Méthode appelée par Django lorsque cette application est chargée et prête.
        """
        from . import signals  