import multiprocessing
import os

# Fly.io écoute sur le port 8080 à l'intérieur du conteneur
bind = "0.0.0.0:8080"

# Ajustables via variables d'env 
workers = int(os.getenv("GUNICORN_WORKERS", str(max(2, multiprocessing.cpu_count() // 2))))
threads = int(os.getenv("GUNICORN_THREADS", "2"))

# Timeouts raisonnables 
timeout = int(os.getenv("GUNICORN_TIMEOUT", "60"))
graceful_timeout = int(os.getenv("GUNICORN_GRACEFUL_TIMEOUT", "30"))
keepalive = int(os.getenv("GUNICORN_KEEPALIVE", "5"))

# Logs sur stdout/stderr 
accesslog = "-"
errorlog = "-"
loglevel = os.getenv("GUNICORN_LOGLEVEL", "info")

# module WSGI :  Module principal 
wsgi_app = "jo_backend.wsgi:application"
