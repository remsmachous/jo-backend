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

## Tests automatisés

Les tests automatisés unitaires et d'intégration sont inclus **dans ce dépôt**.

- le code Django du backend se trouve dans les dossiers `accounts/`, `offers/`, `orders/`, etc.
- les tests sont centralisés dans le dossier `tests/`.

Pour lancer l'ensemble des tests avec mesure de couverture :

```bash
python -m pytest --ds=jo_backend.settings_test --cov --cov-report=term-missing
