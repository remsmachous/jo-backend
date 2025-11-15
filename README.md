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

## Organisation Git

Ce projet suit les bonnes pratiques Git :

- `main` contient le code stable, testé.
- le développement se fait dans des branches `feature/*` (ex : `feature/tests` pour l'intégration des tests automatisés).
- chaque évolution fait l'objet de commits fréquents et explicites (convention "Conventional Commits").

Exemples de branches utilisées dans ce projet :

- `feature/tests` : ajout et intégration des tests automatisés dans le dépôt backend.