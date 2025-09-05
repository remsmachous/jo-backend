"""
Fichier : admin.py (application 'orders')
Description : Personnalise l'affichage et la gestion des modèles de commande
            
"""

from django.contrib import admin
from .models import Reservation, ReservationItem, Ticket


class ReservationItemInline(admin.TabularInline):
    """
    Permet d'afficher et de modifier les articles d'une réservation (ReservationItem)
    directement depuis la page d'édition de la réservation principale.
    """
    model = ReservationItem
    extra = 0


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    """
    Configuration de l'interface d'administration pour le modèle Reservation.
    """
    list_display = ("id", "user", "client_nom", "client_prenom", "client_email", "total", "places", "created_at")
    list_filter = ("created_at",)
    search_fields = ("client_nom", "client_prenom", "client_email", "user__username")
    inlines = [ReservationItemInline]


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    """
    Configuration de l'interface d'administration pour le modèle Ticket.
    """ 
    list_display = ("id", "reservation", "user", "ticket_key", "created_at")
    search_fields = ("ticket_key", "user__username", "reservation__id")
