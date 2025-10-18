"""
Fichier : settings_test.py
Description : Fichier de configuration spécifique aux tests
              pour l'environnement Django.
"""

from .jo_backend.settings import *  

# Configuration de la base de données pour les tests.
# Utilise une base de données SQLite en mémoire pour des tests rapides et isolés.
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

# Backend d'email pour les tests.
# Utilise 'locmem.EmailBackend' pour intercepter les emails en mémoire
# au lieu de les envoyer réellement.
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
