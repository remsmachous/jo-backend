"""
Fichier : serializers.py (application 'orders')
Description : Gère la validation et la transformation des données pour les
              réservations et les billets. Sépare la logique de création (entrante)
              de la logique d'affichage (sortante).
"""

from decimal import Decimal
from rest_framework import serializers
from .models import Reservation, ReservationItem, Ticket 


class ClientSerializer(serializers.Serializer):
    """Définit la structure et la validation pour les données du client."""
    nom = serializers.CharField(max_length=150)
    prenom = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    telephone = serializers.CharField(max_length=30, allow_blank=True, required=False)


class CartItemSerializer(serializers.Serializer):
    """Définit la structure et la validation pour un article du panier."""
    id = serializers.CharField(max_length=64)         
    titre = serializers.CharField(max_length=255)
    prix = serializers.DecimalField(max_digits=10, decimal_places=2)
    qty = serializers.IntegerField(min_value=1)


class ReservationCreateSerializer(serializers.Serializer):
    """Définit la structure et la validation pour un article du panier."""
    client = ClientSerializer()
    panier = CartItemSerializer(many=True)
    total = serializers.DecimalField(max_digits=10, decimal_places=2)
    places = serializers.IntegerField(min_value=1)

    def validate(self, attrs):
        """
        Validation croisée pour s'assurer de la cohérence des données.
        Vérifie que le total et le nombre de places correspondent au contenu du panier.
        """
        expected = sum(Decimal(str(it["prix"])) * it["qty"] for it in attrs["panier"])
        if abs(expected - attrs["total"]) > Decimal("0.01"):
            raise serializers.ValidationError("Total incohérent avec le panier.")
        expected_places = sum(it["qty"] for it in attrs["panier"])
        if expected_places != attrs["places"]:
            raise serializers.ValidationError("Le nombre de places ne correspond pas au panier.")
        return attrs

    def create(self, validated_data):
        """
        Crée les objets Reservation et ReservationItem en base de données.
        """
        request = self.context.get("request")
        user = getattr(request, "user", None)
        if user is None or not user.is_authenticated:
            raise serializers.ValidationError("Authentification requise.")

        client = validated_data["client"]
        panier = validated_data["panier"]

        reservation = Reservation.objects.create(
            user=user,
            client_nom=client["nom"],
            client_prenom=client["prenom"],
            client_email=client["email"],
            client_telephone=client.get("telephone", ""),
            total=validated_data["total"],
            places=validated_data["places"],
        )

        items = []
        for it in panier:
            items.append(ReservationItem(
                reservation=reservation,
                offre_id=it["id"],
                titre=it["titre"],
                prix=it["prix"],
                qty=it["qty"],
            ))
        ReservationItem.objects.bulk_create(items)
        return reservation

# --- Serializers "Sortants" (utilisés pour l'affichage) ---

class ReservationItemOutSerializer(serializers.ModelSerializer):
    """Serializer simple pour afficher les détails d'un article de réservation."""
    class Meta:
        model = ReservationItem
        fields = ("offre_id", "titre", "prix", "qty")


class ReservationDetailSerializer(serializers.ModelSerializer):
    """Serializer complet pour afficher les détails d'une réservation et de ses articles."""
    items = ReservationItemOutSerializer(many=True, read_only=True)

    class Meta:
        model = Reservation
        fields = (
            "id", "user", "client_nom", "client_prenom", "client_email", "client_telephone",
            "total", "places", "created_at", "items"
        )
        read_only_fields = fields

class TicketDetailSerializer(serializers.ModelSerializer):
    """Serializer pour afficher les détails d'un ticket, y compris l'URL absolue du QR code."""
    qr_url = serializers.SerializerMethodField()
    reservation_id = serializers.IntegerField(source="reservation.id", read_only=True)

    class Meta:
        model = Ticket
        fields = ("id", "reservation_id", "qr_url", "created_at")

    def get_qr_url(self, obj):
        """Génère une URL absolue pour l'image du QR code."""
        request = self.context.get("request")
        if not obj.qr_image:
            return None
        return request.build_absolute_uri(obj.qr_image.url) if request else obj.qr_image.url
