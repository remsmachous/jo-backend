"""
Fichier : wsgi.py
Description : Fichier de configuration WSGI pour le projet jo_backend.

"""

import os

from django.core.wsgi import get_wsgi_application

# Indique à Django où trouver le fichier de configuration principal du projet.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jo_backend.settings')

# Crée l'application WSGI que le serveur web pourra utiliser.
application = get_wsgi_application()
