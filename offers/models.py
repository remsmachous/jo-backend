"""
Fichier : models.py (application 'offers')
Description : Définit le modèle de base de données pour les offres de billets.
              Ce modèle contient toutes les informations nécessaires pour
              afficher une offre, y compris les détails, le prix, l'image
              et les champs pour l'affichage front-end.
"""

from django.db import models
from django.core.exceptions import ValidationError
from django.utils.text import slugify
from PIL import Image  

class Offer(models.Model):
    """
    Représente une offre de billet unique dans la base de données.
    """
    name = models.CharField(max_length=120, unique=True)
    slug = models.SlugField(max_length=140, unique=True, blank=True)  
    description = models.TextField(blank=True)

    price = models.DecimalField(max_digits=9, decimal_places=2)

    persons = models.PositiveSmallIntegerField(default=1)

    is_active = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    CATEGORY_CHOICES = [
        ("solo", "Solo"),
        ("duo", "Duo"),
        ("famille", "Famille"),
    ]
    category = models.CharField(
        max_length=16,
        choices=CATEGORY_CHOICES,
        default="solo",
        help_text="Catégorie front (solo / duo / famille)."
    )

    # Image portrait 900x1025
    image = models.ImageField(
        upload_to="offres/",
        blank=True,
        null=True,
        help_text="Image 900×1225 px."
    )
    alt = models.CharField(
        "Texte alternatif (alt)",
        max_length=160,
        blank=True,
        help_text="Alt pour l’accessibilité."
    )

    titre = models.CharField(
        max_length=120,
        blank=True,
        help_text="Titre affiché (défaut = name)."
    )
    btnLabel = models.CharField(
        max_length=60,
        blank=True,
        help_text="Libellé du bouton (ex: “Choisir”)."
    )

    class Meta:
        ordering = ["sort_order", "name"]
        indexes = [
            models.Index(fields=["is_active"]),
            models.Index(fields=["slug"]),
        ]

    def __str__(self) -> str:
        """Représentation textuelle de l'objet, utilisée dans l'admin."""
        return f"{self.name} ({self.price} €)"

    def clean(self):
        """
        Logique de validation et de remplissage automatique appelée avant la sauvegarde.
        """
        if not self.slug and self.name:
            self.slug = slugify(self.name)

        if not self.titre and self.name:
            self.titre = self.name

        # Vérification stricte de la taille de l'image si fournie : 900x1025
        if self.image:
            try:
                self.image.open()
                with Image.open(self.image) as im:
                    w, h = im.size
                    if (w, h) != (900, 1225):
                        raise ValidationError(
                            {"image": f"L'image doit faire exactement 900×1225 px (actuelle : {w}×{h})."}
                        )
            except FileNotFoundError:
                pass

    def save(self, *args, **kwargs):
        """
        Surcharge la méthode save pour s'assurer que `full_clean` est toujours appelé.
        """
        self.full_clean(exclude=None)
        return super().save(*args, **kwargs)
