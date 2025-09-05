# JO Billetterie — Backend (Django 5 + DRF + MariaDB)

## Stack
- Django 5, Django REST Framework, SimpleJWT
- MariaDB
- Déploiement: Fly.io

## Prérequis (dev)
- Python 3.12+
- MariaDB / ou SQLite pour un démarrage rapide

## Installation (dev)
```bash
python -m venv .venv
# Windows
. .venv/Scripts/Activate.ps1
pip install -r requirements.txt

# Copie des variables
cp .env.example .env
