# Objectif: nettoyer des champs qui stockent des URLs absolues de DEV
# pour les remettre en chemins relatifs
# utilisables en PROD (/media/... ou "offers/foo.jpg" pour les FileField).
#

from urllib.parse import urlparse

FIXED = []

def strip_media_prefix(url: str) -> str:
    if not url:
        return url
    # Si URL absolue -> prendre le path
    if url.startswith("http"):
        path = urlparse(url).path  
    else:
        path = url  

    if path.startswith("/media/"):
        path = path[len("/media/"):]  
    return path.lstrip("/")


def fix_model_field(model, instance, field_name: str):
    """
    Fixe un champ d'instance pouvant contenir une URL absolue.
    """
    try:
        val = getattr(instance, field_name, None)
    except Exception:
        return False

    # FileField: on stocke un chemin relatif (le storage sait faire l'URL)
    new_val = None

    # Cas FileField-like
    try:
        name = getattr(val, "name", None)
        url  = getattr(val, "url", None)  
        if name:
            fixed_name = strip_media_prefix(str(name))
            if fixed_name and fixed_name != name:
                val.name = fixed_name
                new_val = val  
        elif url:
            fixed_name = strip_media_prefix(str(url))
            if fixed_name:
                val.name = fixed_name
                new_val = val
    except Exception:
        pass

    if new_val is None and isinstance(val, str):
        # Si c'est une URL absolue http://127.0.0.1:8000/... -> rendre relative
        if "127.0.0.1:8000" in val or "localhost:8000" in val:
            fixed = strip_media_prefix(val)
            if not fixed.startswith("http"):
                # par défaut, on met '/media/<chemin>'
                fixed = "/media/" + fixed if not fixed.startswith("/media/") else fixed
            new_val = fixed

    if new_val is not None and new_val != val:
        setattr(instance, field_name, new_val)
        instance.save(update_fields=[field_name])
        FIXED.append((model.__name__, instance.pk, field_name, str(val), str(new_val)))
        return True

    return False


def try_fix_model(app_label: str, model_name: str, fields: list[str]):
    """
    Tente d'importer un modèle et d'y corriger les champs listés.
    """
    try:
        from django.apps import apps
        Model = apps.get_model(app_label, model_name)
    except Exception:
        print(f"[skip] {app_label}.{model_name} introuvable.")
        return

    count = 0
    qs = Model.objects.all()
    for obj in qs.iterator():
        for f in fields:
            try:
                if fix_model_field(Model, obj, f):
                    count += 1
            except Exception as e:
                print(f"[warn] {app_label}.{model_name}(id={obj.pk}) field '{f}': {e}")
    print(f"[done] {app_label}.{model_name}: {count} changements.")


# ----- Liste des modèles/champs à corriger (adapte si besoin) -----
# Offre (image / image_url)
try_fix_model("offers", "Offer", ["image", "image_url"])

# Tickets / Billets
try_fix_model("orders", "Ticket", ["qr_image", "qr_url", "image", "image_url"])

# Réservations / Commandes (si des URLs ont été stockées)
try_fix_model("orders", "Reservation", ["image_url", "qr_url"])
try_fix_model("orders", "Order", ["image_url", "qr_url"])

print(f"Total corrections: {len(FIXED)}")
for row in FIXED[:10]:
    print("FIX:", row)
