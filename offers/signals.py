"""
Fichier : signals.py (application 'offers')
Description : Ce fichier met en place une automatisation:
              chaque fois qu'une offre est créée, modifiée ou supprimée
              dans l'admin Django, un signal est envoyé pour déclencher
              la regénération automatique du fichier `offres.js` utilisé
              par le front-end React.
"""
from __future__ import annotations
import json
import os
from urllib.parse import urljoin
from pathlib import Path
from django.conf import settings
from django.conf import settings
from jo_backend.github_dispatch import send_repository_dispatch
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from .models import Offer

# --- Configuration des chemins (modifiable via les variables d'environnement) ---
DEFAULT_RELATIVE_FRONT = Path("..") / "react-app" / "src" / "data" / "offres.js"


def _resolve_target_path() -> Path:
    """
    Détermine le chemin absolu où le fichier `offres.js` doit être écrit.
    Priorise la variable d'environnement `FRONT_OFFRES_JS_PATH` si elle existe.
    """
    env_path = os.environ.get("FRONT_OFFRES_JS_PATH")
    if env_path:
        return Path(env_path).resolve()
    base_dir = Path(getattr(settings, "BASE_DIR", "."))
    return (base_dir / DEFAULT_RELATIVE_FRONT).resolve()


def _absolute_media_url(rel_path: str | None) -> str:
    """
    Construit une URL complète pour les images.
    Si `FRONT_MEDIA_BASE_URL` est définie (ex: http://127.0.0.1:8000),
    l'URL sera absolue. Sinon, elle sera relative au serveur.
    """
    if not rel_path:
        return ""
    media_url = getattr(settings, "MEDIA_URL", "/media/")
    base = os.environ.get("FRONT_MEDIA_BASE_URL", "").strip()  # ex: http://127.0.0.1:8000
    if not media_url.startswith("/"):
        media_url = "/" + media_url
    media_path = media_url.rstrip("/") + "/" + rel_path.lstrip("/")
    return urljoin(base if base.endswith("/") else base + "/", media_path.lstrip("/")) if base else media_path


def _offers_qs_grouped() -> dict[str, list[Offer]]:
    """Récupère toutes les offres actives et les regroupe par catégorie."""
    by_cat: dict[str, list[Offer]] = {"solo": [], "duo": [], "famille": []}
    for o in Offer.objects.filter(is_active=True).order_by("sort_order", "name"):
        cat = (o.category or "solo").lower()
        if cat not in by_cat:
            cat = "solo"
        by_cat[cat].append(o)
    return by_cat


def _js_string(value: str) -> str:
    """Sérialise une chaîne Python en une chaîne de caractères JSON/JS valide."""
    return json.dumps(value or "", ensure_ascii=False)


def _serialize_js_module() -> str:
    """
    Construit le contenu complet du fichier JavaScript `offres.js`.
    """
    groups = _offers_qs_grouped()

    def item_js(o: Offer) -> str:
        image_url = _absolute_media_url(getattr(o.image, "name", None))
        alt = o.alt or ""
        titre = (o.titre or o.name or "").strip()
        desc = (o.description or "").strip()
        prix = float(o.price) if o.price is not None else 0.0
        btn_label = o.btnLabel or "Choisir"
        btn_href = "/reservation"  

        return (
            "{ "
            f"image: {_js_string(image_url)}, "
            f"alt: {_js_string(alt)}, "
            f"titre: {_js_string(titre)}, "
            f"description: {_js_string(desc)}, "
            f"prix: {prix}, "
            f"btnLabel: {_js_string(btn_label)}, "
            f"btnClass: BTN_CLASS, "
            f"btnHref: {_js_string(btn_href)} "
            "}"
        )

    def list_js(items: list[Offer]) -> str:
        # Formate une liste d'offres en un tableau JavaScript.
        return "[\n  " + ",\n  ".join(item_js(o) for o in items) + ("\n" if items else "") + "]"

    solo_js = list_js(groups.get("solo", []))
    duo_js = list_js(groups.get("duo", []))
    famille_js = list_js(groups.get("famille", []))

    header = (
        "/**\n"
        " * ⚠️ FICHIER GÉNÉRÉ AUTOMATIQUEMENT — NE PAS ÉDITER\n"
        " * Origine : Django (offers/signals.py)\n"
        " * Tout changement manuel sera écrasé lors de la prochaine sauvegarde d'une offre.\n"
        " */\n\n"
    )

    body = (
        'const BTN_CLASS = "btn btn-custom";\n\n'
        f"export const offresSolo = {solo_js};\n\n"
        f"export const offresDuo = {duo_js};\n\n"
        f"export const offresFamille = {famille_js};\n\n"
        "export default { offresSolo, offresDuo, offresFamille };\n"
    )

    return header + body


def _write_offres_js():
    """Écrit le contenu généré dans le fichier cible."""
    target = _resolve_target_path()
    target.parent.mkdir(parents=True, exist_ok=True)
    content = _serialize_js_module()
    with open(target, "w", encoding="utf-8") as f:
        f.write(content)

def _trigger_front_sync(why: str, offer_id: int):
    cfg = getattr(settings, "GITHUB_DISPATCH", {})
    token = cfg.get("TOKEN")
    owner = cfg.get("OWNER")
    repo  = cfg.get("REPO")
    event = cfg.get("EVENT", "offres_updated")

    if not (token and owner and repo):
        return

    payload = {
        "reason": why,
        "offer_id": offer_id,
        "backend": "fly:jobackend",
    }
    try:
        send_repository_dispatch(owner, repo, token, event, client_payload=payload)
    except Exception:
        import logging
        logging.exception("Repository dispatch failed")


# --- Connexion des signaux ---
@receiver(post_save, sender=Offer)
def offer_saved(sender, instance, created, **kwargs):
    try:
        _write_offres_js()
    except Exception as e:
        print("[offers.signals] WARN: génération offres.js échouée:", e)
    _trigger_front_sync("created" if created else "updated", instance.id)


@receiver(post_delete, sender=Offer)
def offer_deleted(sender, instance, **kwargs):
    try:
        _write_offres_js()
    except Exception as e:
        print("[offers.signals] WARN: génération offres.js échouée:", e)
    _trigger_front_sync("deleted", instance.id)


