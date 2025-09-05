"""
Fichier : models.py (application 'orders')
Description : Définit les modèles pour le processus de commande,
              incluant les réservations, les articles de réservation
              et les billets finaux.
"""

from django.conf import settings
from django.db import models


class Reservation(models.Model):
    """
    Représente une réservation effectuée par un client avant le paiement.
    Contient les informations du client et un résumé de la commande.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="reservations",
    )
    client_nom = models.CharField(max_length=150)
    client_prenom = models.CharField(max_length=150)
    client_email = models.EmailField()
    client_telephone = models.CharField(max_length=30, blank=True, default="")

    total = models.DecimalField(max_digits=10, decimal_places=2)
    places = models.PositiveIntegerField()

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "created_at"]),
        ]

    def __str__(self) -> str:
        """Représentation textuelle de l'objet, utile dans l'admin."""
        return f"Reservation #{self.id} par {self.client_prenom} {self.client_nom} (user={self.user_id})"


class ReservationItem(models.Model):
    """
    Représente un article unique dans une réservation.
    Conserve un "snapshot" des informations de l'offre au moment de l'achat.
    """
    reservation = models.ForeignKey(
        Reservation,
        on_delete=models.CASCADE,
        related_name="items",
    )
    offre_id = models.CharField(max_length=64)
    titre = models.CharField(max_length=255)
    prix = models.DecimalField(max_digits=10, decimal_places=2)
    qty = models.PositiveIntegerField()

    class Meta:
        indexes = [
            models.Index(fields=["reservation"]),
            models.Index(fields=["offre_id"]),
        ]

    def __str__(self) -> str:
        return f"Item(offre_id={self.offre_id}, qty={self.qty}, res={self.reservation_id})"


class Ticket(models.Model):
    """
    Représente un billet électronique final, généré après un paiement réussi.
    Chaque réservation ne peut avoir qu'un seul ticket.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="tickets",
    )
    # La relation OneToOne garantit qu'une réservation ne peut générer qu'un seul ticket.
    reservation = models.OneToOneField(
        Reservation,
        on_delete=models.CASCADE,
        related_name="ticket",
    )
    ticket_key = models.CharField(max_length=64, unique=True)
    qr_image = models.ImageField(upload_to="tickets/")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "created_at"]),
            models.Index(fields=["ticket_key"]),
        ]

    def __str__(self) -> str:
        return f"Ticket #{self.id} for res={self.reservation_id}"
