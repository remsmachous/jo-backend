"""
Fichier : apps.py (application 'orders')
Description : Fichier de configuration pour l'application Django 'orders'.

"""

from django.apps import AppConfig


class OrdersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'orders'
