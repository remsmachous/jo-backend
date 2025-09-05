# ---------- Base ----------
FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# Dépendances nécessaires
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libmariadb-dev-compat \
    libmariadb-dev \
    pkg-config \
    netcat-openbsd \
    curl \
    libjpeg62-turbo \
    zlib1g \
    libfreetype6 \
    liblcms2-2 \
    libopenjp2-7 \
    libtiff6 \
    libwebp7 \
 && rm -rf /var/lib/apt/lists/*


WORKDIR /app

# ---------- Python deps ----------
COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt

# ---------- App ----------
COPY . /app/

RUN sed -i 's/\r$//' /app/start.sh && chmod +x /app/start.sh

RUN mkdir -p /app/staticfiles

# Port interne écouté par Gunicorn (et attendu par Fly)
ENV PORT=8080

# Module de settings par défaut 
ENV DJANGO_SETTINGS_MODULE=jo_backend.settings \
    PYTHONPATH=/app

# Healthcheck interne 
HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
  CMD curl -f http://127.0.0.1:8080/api/health || exit 1

CMD ["/app/start.sh"]
