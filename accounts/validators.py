"""
Fichier : validators.py (application 'accounts')
Description : Contient des classes de validation personnalisées pour les
              mots de passe.
"""
import re
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _


class ComplexPasswordValidator:
    """
    Règles:
      - longueur ≥ 12
      - ≥ 1 minuscule
      - ≥ 1 majuscule
      - ≥ 1 chiffre
      - ≥ 1 caractère spécial
      - aucun espace
    """
    def validate(self, password, user=None):
        if " " in password:
            raise ValidationError(_("Le mot de passe ne doit pas contenir d'espaces."))

        if len(password) < 12:
            raise ValidationError(_("Le mot de passe doit contenir au moins 12 caractères."))

        if not re.search(r"[a-z]", password):
            raise ValidationError(_("Le mot de passe doit contenir au moins une lettre minuscule."))

        if not re.search(r"[A-Z]", password):
            raise ValidationError(_("Le mot de passe doit contenir au moins une lettre majuscule."))

        if not re.search(r"\d", password):
            raise ValidationError(_("Le mot de passe doit contenir au moins un chiffre."))

        # [^\w\s] = tout caractère qui n'est ni alphanumérique ni underscore, ni espace
        if not re.search(r"[^\w\s]", password):
            raise ValidationError(_("Le mot de passe doit contenir au moins un caractère spécial."))

    def get_help_text(self):
        """
        Retourne un texte d'aide qui sera affiché à l'utilisateur.
        """
        return _(
            "≥12 caractères, avec au moins une minuscule, une majuscule, un chiffre, un caractère spécial et aucun espace."
        )


class BlacklistPasswordValidator:
    """
    Vérifie qu'un mot de passe n'est pas dans une liste de mots de passe
    courants et trop simples. La comparaison est insensible à la casse.
    """
    BLACKLIST = {
        "password", "motdepasse", "azerty", "qwerty",
        "admin", "administrator", "welcome", "letmein",
        "1234567890", "12345678", "000000",
        "password123", "admin123",
    }

    def validate(self, password, user=None):
        """
        Levé d'une ValidationError si le mot de passe
        est trouvé dans la blacklist.
        """
        if password.lower() in self.BLACKLIST:
            raise ValidationError(_("Ce mot de passe est trop commun."))

    def get_help_text(self):
        """
        Retourne le message d'aide pour l'utilisateur.
        """        
        return _("Le mot de passe ne doit pas être un mot de passe commun.")
