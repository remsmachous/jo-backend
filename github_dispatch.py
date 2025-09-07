import json
import os
import time
from typing import Optional, Dict

import requests

GITHUB_API = "https://api.github.com"

class RepoDispatchError(Exception):
    pass

def send_repository_dispatch(
    owner: str,
    repo: str,
    token: str,
    event_type: str,
    client_payload: Optional[Dict] = None,
    retries: int = 2,
    timeout: int = 10,
):
    """
    Envoie un repository_dispatch à GitHub Actions.

    Nécessite un PAT avec permissions Actions/Contents sur le repo cible.
    """
    url = f"{GITHUB_API}/repos/{owner}/{repo}/dispatches"
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
        "X-GitHub-Api-Version": "2022-11-28",
        "Content-Type": "application/json",
    }
    payload = {"event_type": event_type}
    if client_payload:
        payload["client_payload"] = client_payload

    last_err = None
    for attempt in range(retries + 1):
        try:
            resp = requests.post(url, headers=headers, data=json.dumps(payload), timeout=timeout)
            if resp.status_code in (201, 204):  # GitHub renvoie souvent 204
                return
            last_err = RepoDispatchError(f"GitHub API {resp.status_code}: {resp.text}")
        except requests.RequestException as e:
            last_err = e

        # backoff simple
        time.sleep(1 + attempt)

    raise last_err
