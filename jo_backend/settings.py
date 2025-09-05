"""
Fichier : settings.py
Description : Fichier de configuration principal du projet Django.
              Contient tous les réglages pour l'application, y compris la base de données,
              les applications installées, la sécurité, etc.
              Ce fichier est conçu pour charger des variables d'environnement
              différentes pour le développement et la production.
"""
from pathlib import Path
import os
from datetime import timedelta
from dotenv import load_dotenv
import urllib.parse

def env_list(name: str, default=""):
    raw = os.getenv(name, default)
    return [item.strip() for item in raw.split(",") if item.strip()]

# Évite que Django réécrive les URLs avec slash
APPEND_SLASH = False

# Définit le répertoire de base du projet
BASE_DIR = Path(__file__).resolve().parent.parent

# --- Sélection dynamique du fichier .env ---
# Charge les variables d'environnement depuis .env.development ou .env.production
# en fonction de la variable système DJANGO_ENV.
DJANGO_ENV = os.getenv("DJANGO_ENV", "development").lower()
env_file_map = {
    "development": BASE_DIR / ".env.development",
    "production": BASE_DIR / ".env.production",
}
env_file = env_file_map.get(DJANGO_ENV)
if env_file and env_file.exists():
    load_dotenv(env_file)
else:
    load_dotenv(BASE_DIR / ".env")

# --- Utilitaire pour dériver les noms d'hôtes depuis les URLs CORS ---
def _hosts_from_urls(urls: list[str]) -> list[str]:
    hosts: list[str] = []
    for u in urls:
        try:
            parsed = urllib.parse.urlparse(u)
            if parsed.hostname:
                hosts.append(parsed.hostname)
        except Exception:
            pass
    return hosts

# --- Sécurité de base ---
SECRET_KEY = os.getenv("SECRET_KEY", "unsafe-dev-key-change-me")
DEBUG = os.getenv("DEBUG", "False").lower() in ("1", "true", "yes")

# ALLOWED_HOSTS
cors_origins = [o.strip() for o in os.getenv("CORS_ALLOWED_ORIGINS", "").split(",") if o.strip()]
derived_hosts = _hosts_from_urls(cors_origins)
ALLOWED_HOSTS = ["jobackend.fly.dev", ".fly.dev", "localhost", "127.0.0.1"]

# --- Apps ---
INSTALLED_APPS = [
    # Django
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # Tiers
    "rest_framework",
    "corsheaders",

    # Projet
    "accounts",
    "orders",
    "offers.apps.OffersConfig",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "jo_backend.urls"

# --- Templates ---

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "jo_backend.wsgi.application"
ASGI_APPLICATION = "jo_backend.asgi.application"

# --- Base de données ---
# La configuration est entièrement lue depuis les variables d'environnement.
DATABASES = {
    "default": {
        "ENGINE": os.getenv("DB_ENGINE", "django.db.backends.mysql"),
        "NAME": os.getenv("DB_NAME", "jobackend"),
        "USER": os.getenv("DB_USER", "jobackend_user"),
        "PASSWORD": os.getenv("DB_PASSWORD", ""),
        "HOST": os.getenv("DB_HOST", "127.0.0.1"),
        "PORT": os.getenv("DB_PORT", "3306"),
        "OPTIONS": {
            "init_command": "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    }
}

# --- Modèle Utilisateur Personnalisé ---
AUTH_USER_MODEL = "accounts.User"

# --- Politique de sécurité des mots de passe ---
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator", "OPTIONS": {"min_length": 12}},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
    {"NAME": "accounts.validators.ComplexPasswordValidator"},
    {"NAME": "accounts.validators.BlacklistPasswordValidator"},
]

# --- Locale ---
LANGUAGE_CODE = "fr-fr"
TIME_ZONE = "Europe/Paris"
USE_I18N = True
USE_TZ = True

# --- Static & Media ---
STATIC_URL = "/static/"
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent

STATICFILES_DIRS = [
    BASE_DIR / "static",
]

STATIC_ROOT = Path(BASE_DIR) / "staticfiles"
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# --- CORS ---
_default_cors = "http://localhost:5173,http://127.0.0.1:5173"
CORS_ALLOWED_ORIGINS = [
    "http://127.0.0.1:8080",
    "http://localhost:8080",
]
CORS_ALLOW_CREDENTIALS = True
CSRF_TRUSTED_ORIGINS = env_list("CSRF_TRUSTED_ORIGINS", "https://jobackend.fly.dev")

# --- DRF ---
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.AllowAny",
    ),
}

# --- Configuration de SimpleJWT ---
SIMPLE_JWT = {
    "ALGORITHM": "HS256",
    "SIGNING_KEY": SECRET_KEY,
    "AUTH_HEADER_TYPES": ("Bearer",),
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=30 if DEBUG else 5),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7 if DEBUG else 1),
    "ROTATE_REFRESH_TOKENS": False,
    "BLACKLIST_AFTER_ROTATION": False,
    "UPDATE_LAST_LOGIN": False,
}

# --- Sécurité renforcée en prod ---
# Ces paramètres ne sont activés que si DEBUG=False.
if not DEBUG:
    USE_X_FORWARDED_HOST = True
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SECURE_SSL_REDIRECT = os.getenv("SECURE_SSL_REDIRECT", "False").lower() in ("1", "true", "yes")
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = int(os.getenv("SECURE_HSTS_SECONDS", "0"))
    SECURE_HSTS_INCLUDE_SUBDOMAINS = os.getenv("SECURE_HSTS_INCLUDE_SUBDOMAINS", "False").lower() == "true"
    SECURE_HSTS_PRELOAD = os.getenv("SECURE_HSTS_PRELOAD", "False").lower() == "true"
