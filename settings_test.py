"""
Fichier : settings_test.py
Description : Fichier de configuration spécifique aux tests
              pour l'environnement Django.
"""

from .jo_backend.settings import *  

# Configuration de la base de données pour les tests.
DATABASES["default"]["NAME"] = os.getenv("DB_NAME_TEST", "jo_db_test")


# Backend d'email pour les tests.
# Utilise 'locmem.EmailBackend' pour intercepter les emails en mémoire
# au lieu de les envoyer réellement.
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
