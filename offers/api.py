"""
Fichier : api.py (application 'offers')
Description : Définit le ViewSet pour l'API des offres (Offer).
"""
from rest_framework import serializers, viewsets, permissions, filters
from django.db.models import QuerySet
from .models import Offer

class OfferSerializer(serializers.ModelSerializer):
    """
    Serializer pour le modèle Offer.
    Convertit les instances du modèle Offer en JSON et vice-versa,
    et valide les données entrantes.
    """
    image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Offer
        fields = [
            "id",
            "name",
            "slug",
            "description",
            "price",
            "persons",
            "is_active",
            "sort_order",
            "created_at",
            "updated_at",
            "category", 
            "titre", 
            "btnLabel", 
            "alt",
            "image_url",  
        ]
        # Spécifie les champs qui ne peuvent pas être modifiés via l'API.
        read_only_fields = ["id", "created_at", "updated_at"]

    def get_image_url(self, obj):
        request = self.context.get("request")
        url = getattr(getattr(obj, "image", None), "url", None)
        if not url:
            url = getattr(obj, "image_url", None)
        if not url:
            return None
        if request and not str(url).startswith("http"):
            return request.build_absolute_uri(url)
        return url

class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Permission personnalisée : autorise l'accès en lecture à tout le monde,
    mais restreint l'écriture (POST, PUT, DELETE) aux administrateurs.
    """
    def has_permission(self, request, view):
        # Les méthodes "sûres" (GET, HEAD, OPTIONS) sont toujours autorisées.
        if request.method in permissions.SAFE_METHODS:
            return True
        # Pour les autres méthodes (écriture), l'utilisateur doit être
        # authentifié.
        user = request.user
        return bool(
            user
            and user.is_authenticated
            and (getattr(user, "is_staff", False) or getattr(user, "is_admin", False))
        )

class OfferViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour gérer les opérations CRUD (Create, Retrieve, Update, Delete)
    sur le modèle Offer.
    """
    serializer_class = OfferSerializer
    permission_classes = [IsAdminOrReadOnly]
    queryset = Offer.objects.all().order_by("sort_order", "name")

    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "slug", "description"]
    ordering_fields = ["sort_order", "name", "price", "persons", "updated_at", "created_at"]
    ordering = ["sort_order", "name"]

    def get_queryset(self) -> QuerySet:
        """
        Surcharge la méthode pour retourner le queryset.
        Permet de filtrer les offres retournées en fonction du statut de l'utilisateur.
        """
        qs = super().get_queryset()
        user = getattr(self, "request", None).user if hasattr(self, "request") else None
        if not (user and user.is_authenticated and (getattr(user, "is_staff", False) or getattr(user, "is_admin", False))):
            qs = qs.filter(is_active=True)
        return qs
    
    def get_serializer(self, *args, **kwargs):
        kwargs.setdefault("context", {}).setdefault("request", self.request)
        return super().get_serializer(*args, **kwargs)