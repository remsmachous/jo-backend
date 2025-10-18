"""
Fichier : urls.py (application 'orders')
Description : Définit toutes les routes (endpoints) de l'API liées au processus
              de commande, de la création de la réservation au paiement et à la
              consultation des billets.
"""
app_name = "orders"
from django.urls import path
from .views import (
    ReservationCreateAPIView,
    ReservationDetailAPIView,
    CheckoutAPIView,
    TicketDetailAPIView,
    VerifyTicketAPIView,
    TicketOpaqueDebugAPIView,
    MyTicketsView, 
    TicketOpaqueDebugAPIView, 
)

# La liste de toutes les routes pour l'application 'orders'.
urlpatterns = [
    # --- Processus de commande ---
    path("reservations", ReservationCreateAPIView.as_view(), name="reservation_create"),
    path("reservations/<int:pk>", ReservationDetailAPIView.as_view(), name="reservation_detail"),
    path("checkout", CheckoutAPIView.as_view(), name="checkout"),

    # --- Gestion des Billets ---
    path("tickets/<int:pk>", TicketDetailAPIView.as_view(), name="ticket_detail"),
    path("verify", VerifyTicketAPIView.as_view(), name="verify_ticket"),
    path("tickets/<int:pk>/opaque", TicketOpaqueDebugAPIView.as_view(), name="ticket_opaque_debug"),
    path("my-tickets/", MyTicketsView.as_view(), name="my_tickets"),
]