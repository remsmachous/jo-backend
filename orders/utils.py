"""
Fichier : utils.py (application 'orders')
Description : Contient les fonctions utilitaires pour l'application 'orders'.
              Ces fonctions gèrent des logiques comme la génération de QR codes.
"""
from pathlib import Path
from django.conf import settings
from django.core.signing import dumps 
import qrcode


def generate_ticket_qr_image(ticket) -> str:
    """
    Génère un QR code pour un billet et le sauvegarde en tant qu'image.

    Args:
        ticket (Ticket): L'instance du modèle Ticket pour laquelle générer le QR code.

    Returns:
        str: Le chemin relatif de l'image PNG générée (ex: "tickets/ticket_123.png").
    """
    # Contenu minimal pour la vérification, sans exposer de données sensibles.
    payload = {"tid": ticket.id, "rid": ticket.reservation_id, "uid": ticket.user_id}
    
    # Utilise le système de signature de Django pour créer un token sécurisé et infalsifiable.
    signed_token = dumps(payload, salt="ticket")

    # Contenu qui sera encodé dans le QR code (un URI personnalisé).
    qr_payload = f"jo://ticket/{signed_token}"

     # S'assure que le dossier de destination existe.
    out_dir = Path(settings.MEDIA_ROOT) / "tickets"
    out_dir.mkdir(parents=True, exist_ok=True)

    filename = f"ticket_{ticket.id}.png"
    full_path = out_dir / filename

    # Génération de l'image PNG avec la bibliothèque qrcode.
    img = qrcode.make(qr_payload)
    img.save(full_path)

    # Retourne le chemin relatif qui sera stocké en base de données.
    return f"tickets/{filename}"
