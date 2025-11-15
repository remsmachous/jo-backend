
import json
import logging
import urllib.request
import urllib.error

_GH_API = "https://api.github.com"

def send_repository_dispatch(owner: str, repo: str, token: str, event_type: str, client_payload: dict | None = None):
    """
    Envoie un Repository Dispatch vers GitHub pour déclencher le workflow du front.
    Retourne True si OK, sinon lève une exception.
    """
    if not owner or not repo or not token or not event_type:
        raise ValueError("Missing owner/repo/token/event_type for repository_dispatch")

    url = f"{_GH_API}/repos/{owner}/{repo}/dispatches"
    body = {
        "event_type": event_type,
        "client_payload": client_payload or {}
    }
    data = json.dumps(body).encode("utf-8")

    req = urllib.request.Request(url, data=data, method="POST")
    req.add_header("Authorization", f"token {token}")
    req.add_header("Content-Type", "application/json")
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("User-Agent", "jo-backend/dispatch")

    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            if resp.status in (200, 201, 202, 204):
                logging.info("Repository dispatch sent: %s/%s event=%s", owner, repo, event_type)
                return True
            raise RuntimeError(f"GitHub dispatch unexpected status: {resp.status}")
    except urllib.error.HTTPError as e:
        text = e.read().decode("utf-8", errors="ignore") if hasattr(e, "read") else ""
        logging.error("GitHub dispatch failed: %s %s", e, text)
        raise
    except Exception:
        logging.exception("GitHub dispatch failed (network/unknown)")
        raise
