"""
Fichier : signals.py (application 'accounts')
"""

import secrets
from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User

@receiver(post_save, sender=User)
def generate_account_key_on_create(sender, instance: User, created: bool, **kwargs):
    """
    Génère une `account_key` sécurisée pour un utilisateur
    uniquement lors de sa création.
    """
    if not created:
        return

    # Si déjà présent, on ne touche pas.
    if instance.account_key:
        return

    # Génère une clé secrète sécurisée
    instance.account_key = secrets.token_hex(32)

    # Sauvegarde dans une transaction pour éviter les partiels
    def _save():
        instance.save(update_fields=["account_key"])

    # Si on est déjà dans une transaction, sauvegarde direct, sinon ouvre-en une
    if transaction.get_connection().in_atomic_block:
        _save()
    else:
        with transaction.atomic():
            _save()
