"""
Fichier : views.py (application 'orders')
Description : Définit les vues de l'API pour l'ensemble du processus de commande,
              de la création de la réservation au paiement, à la vérification
              et à la consultation des billets.
"""

from rest_framework import permissions, generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import ReservationCreateSerializer, ReservationDetailSerializer, TicketDetailSerializer
import hashlib
import secrets
from django.shortcuts import get_object_or_404
from .models import Reservation, Ticket
from .utils import generate_ticket_qr_image
from django.conf import settings
from django.core.signing import loads, dumps, BadSignature
from rest_framework import permissions, status

# --- Vues du processus de commande ---

class ReservationCreateAPIView(APIView):
    """Crée une nouvelle réservation à partir d'un panier validé."""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        """Gère la requête POST pour créer une réservation."""
        serializer = ReservationCreateSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        reservation = serializer.save()
        return Response({"reservation_id": reservation.id}, status=status.HTTP_201_CREATED)


class ReservationDetailAPIView(generics.RetrieveAPIView):
    """Affiche les détails d'une réservation spécifique pour l'utilisateur connecté."""
    serializer_class = ReservationDetailSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """S'assure qu'un utilisateur ne peut voir que ses propres réservations."""
        return Reservation.objects.filter(user=self.request.user)


class CheckoutAPIView(APIView):
    """Gère le "paiement" d'une réservation et génère le billet correspondant."""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        """Simule un paiement et crée un ticket si la réservation est valide."""
        rid = request.data.get("reservation_id")
        if not rid:
            return Response({"detail": "reservation_id manquant"}, status=status.HTTP_400_BAD_REQUEST)

        reservation = get_object_or_404(Reservation, id=rid, user=request.user)

        # Vérifie si un ticket n'a pas déjà été généré pour éviter les doublons.
        if hasattr(reservation, "ticket"):
            ticket = reservation.ticket
            qr_url = request.build_absolute_uri(ticket.qr_image.url) if ticket.qr_image else None
            return Response(
                {
                    "status": "already_paid",
                    "ticket": {
                        "id": ticket.id,
                        "reservation_id": reservation.id,
                        "qr_url": qr_url,
                        "summary": {
                            "client": f"{reservation.client_prenom} {reservation.client_nom}",
                            "email": reservation.client_email,
                            "total": str(reservation.total),
                            "places": reservation.places,
                        },
                    },
                },
                status=status.HTTP_409_CONFLICT,
            )

        # Génère la clé sécurisée du ticket en combinant la clé du compte et une clé d'achat.
        account_key = getattr(request.user, "account_key", None)
        if not account_key:
            return Response({"detail": "account_key manquante pour cet utilisateur."}, status=status.HTTP_400_BAD_REQUEST)

        purchase_key = secrets.token_hex(32)
        final_key = hashlib.sha256((account_key + purchase_key).encode("utf-8")).hexdigest()

        # Génère la clé sécurisée du ticket en combinant la clé du compte et une clé d'achat.
        ticket = Ticket.objects.create(
            user=request.user,
            reservation=reservation,
            ticket_key=final_key,
        )

        # Génère l'image du QR code et la lie au ticket.
        relative_path = generate_ticket_qr_image(ticket)
        ticket.qr_image.name = relative_path
        ticket.save(update_fields=["qr_image"])

        qr_url = request.build_absolute_uri(ticket.qr_image.url)

        return Response(
            {
                "status": "paid",
                "ticket": {
                    "id": ticket.id,
                    "reservation_id": reservation.id,
                    "qr_url": qr_url,
                    "summary": {
                        "client": f"{reservation.client_prenom} {reservation.client_nom}",
                        "email": reservation.client_email,
                        "total": str(reservation.total),
                        "places": reservation.places,
                    },
                },
            },
            status=status.HTTP_201_CREATED,
        )

# --- Vues pour la gestion des billets ---

class TicketDetailAPIView(generics.RetrieveAPIView):
    """Affiche les détails d'un billet spécifique pour l'utilisateur connecté."""
    serializer_class = TicketDetailSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """S'assure qu'un utilisateur ne peut voir que ses propres billets."""
        return Ticket.objects.filter(user=self.request.user)
    

def _extract_signed_token(raw: str) -> str:
    if not isinstance(raw, str):
        return ""
    prefix = "jo://ticket/"
    return raw[len(prefix):] if raw.startswith(prefix) else raw


class VerifyTicketAPIView(APIView):
    """Endpoint public pour l'application de scan afin de vérifier un billet."""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        """Valide un token de billet en vérifiant sa signature et sa cohérence en base."""
        token = request.data.get("token") or request.data.get("qr")
        token = _extract_signed_token(token or "")
        if not token:
            return Response({"valid": False, "reason": "missing_token"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            data = loads(token, salt="ticket")  # {'tid': ..., 'rid': ..., 'uid': ...}
        except BadSignature:
            return Response({"valid": False, "reason": "bad_signature"}, status=status.HTTP_200_OK)

        tid = data.get("tid")
        rid = data.get("rid")
        uid = data.get("uid")
        if not all([tid, rid, uid]):
            return Response({"valid": False, "reason": "malformed_payload"}, status=status.HTTP_200_OK)

        from .models import Ticket  
        try:
            ticket = Ticket.objects.select_related("reservation", "user").get(id=tid)
        except Ticket.DoesNotExist:
            return Response({"valid": False, "reason": "ticket_not_found"}, status=status.HTTP_200_OK)

        if ticket.user_id != uid or ticket.reservation_id != rid:
            return Response({"valid": False, "reason": "mismatch"}, status=status.HTTP_200_OK)

        res = ticket.reservation
        return Response(
            {
                "valid": True,
                "meta": {
                    "ticket_id": ticket.id,
                    "reservation_id": ticket.reservation_id,
                    "user_id": ticket.user_id,
                    "client": f"{res.client_prenom} {res.client_nom}",
                    "email": res.client_email,
                    "places": res.places,
                    "total": str(res.total),
                    "created_at": ticket.created_at,
                },
            },
            status=status.HTTP_200_OK,
        )


class TicketOpaqueDebugAPIView(APIView):
    """Endpoint de débogage (disponible uniquement en mode DEBUG) pour générer un token signé."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk: int):
        """Retourne le token signé pour un billet donné."""
        if not settings.DEBUG:
            return Response(status=status.HTTP_404_NOT_FOUND)

        from .models import Ticket
        try:
            ticket = Ticket.objects.select_related("reservation").get(id=pk, user=request.user)
        except Ticket.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        payload = {"tid": ticket.id, "rid": ticket.reservation_id, "uid": ticket.user_id}
        signed = dumps(payload, salt="ticket")
        return Response({"token": signed})


class MyTicketsView(APIView):
    """Liste tous les billets de l'utilisateur actuellement authentifié."""
    permission_classes = [permissions.IsAuthenticated]

    def _build_absolute(self, request, url_or_path: str | None) -> str | None:
        if not url_or_path:
            return None
        if isinstance(url_or_path, str) and (url_or_path.startswith("http://") or url_or_path.startswith("https://")):
            return url_or_path
        return request.build_absolute_uri(url_or_path)

    def _extract_qr_url(self, request, ticket) -> str | None:
        val = getattr(ticket, "qr_url", None)
        if val:
            return self._build_absolute(request, val if isinstance(val, str) else str(val))

        for fname in ("qr_image", "qr_png", "qrcode", "qr"):
            f = getattr(ticket, fname, None)
            if f:
                url = None
                try:
                    url = f.url  
                except Exception:
                    try:
                        url = str(f)
                    except Exception:
                        url = None
                if url:
                    if isinstance(url, str) and url.startswith("/"):
                        return self._build_absolute(request, url)
                    media_url = getattr(settings, "MEDIA_URL", "") or ""
                    return self._build_absolute(request, media_url.rstrip("/") + "/" + str(url).lstrip("/"))
        return None

    def get(self, request):
        """Retourne une liste simplifiée des billets de l'utilisateur."""
        qs = Ticket.objects.filter(user=request.user).order_by("-id")
        results = []
        for t in qs:
            results.append({
                "id": t.pk,
                "qr_url": self._extract_qr_url(request, t),
                "created": getattr(t, "created_at", None) or getattr(t, "created", None),
            })
        return Response({"count": len(results), "results": results})