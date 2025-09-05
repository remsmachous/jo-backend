
"""
Fichier : admin.py (application 'offers')
Description : Personnalise l'affichage et la gestion du modèle 'Offer'
              dans l'interface d'administration de Django.
"""
from django.contrib import admin
from django.utils.html import format_html
from .models import Offer


@admin.register(Offer)
class OfferAdmin(admin.ModelAdmin):
    """
    Configuration de l'interface d'administration pour le modèle Offer.
    """
    # --- Configuration de la vue LISTE ---
    list_display = (
        "image_thumb",
        "name",
        "category",
        "price",
        "persons",
        "is_active",
        "sort_order",
        "updated_at",
    )
    list_display_links = ("name",)
    list_editable = ("is_active", "sort_order")
    list_filter = ("category", "is_active")
    search_fields = ("name", "slug", "description", "titre", "alt")
    ordering = ("sort_order", "name")

    # --- Configuration du formulaire d'ÉDITION ---
    readonly_fields = ("image_preview", "created_at", "updated_at")
    fieldsets = (
        ("Informations principales", {
            "fields": (
                ("name", "slug"),
                ("category", "persons"),
                ("price", "is_active", "sort_order"),
                "description",
            )
        }),
        ("Affichage Front (offres.js)", {
            "fields": (
                ("titre", "btnLabel"),
            ),
            "description": (
                "Ces champs alimentent le fichier généré <code>src/data/offres.js</code> côté React."
            ),
        }),
        ("Image (900×1025)", {
            "fields": (
                "image",
                "alt",
                "image_preview",
            ),
            "description": (
                "Téléversez une image <strong>exactement 900×1025 px</strong>. "
                "L’aperçu est affiché ci-dessous après l’enregistrement."
            ),
        }),
        ("Traces", {
            "classes": ("collapse",),
            "fields": ("created_at", "updated_at"),
        }),
    )

    def image_thumb(self, obj: Offer):
        """
        Affiche une miniature de l'image dans la vue liste de l'admin.
        Utilise format_html pour un rendu sécurisé du HTML.
        """
        if obj.image:
            return format_html(
                '<img src="{}" style="height:48px;width:auto;border-radius:4px;object-fit:cover;" alt="thumb" />',
                obj.image.url,
            )
        return "—"
    image_thumb.short_description = "Image"

    def image_preview(self, obj: Offer):
        """
        Affiche un aperçu plus grand de l'image directement dans le formulaire d'édition.
        """
        if obj.image:
            return format_html(
                '<div style="margin-top:6px;">'
                '<img src="{}" style="max-height:260px;width:auto;border:1px solid #ddd;border-radius:8px;" alt="preview" />'
                "</div>",
                obj.image.url,
            )
        return "—"
    image_preview.short_description = "Aperçu"
