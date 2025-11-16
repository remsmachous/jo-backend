# JO Billetterie --- Backend

Backend du système de réservation des Jeux Olympiques.\
Développé avec **Django 5**, **Django REST Framework**, **MariaDB**,
**Pytest**, et **Docker Compose**.

------------------------------------------------------------------------

## Stack 

-   Python 3.12+
-   Django 5
-   Django REST Framework (DRF)
-   MariaDB
-   Pytest / pytest-django / pytest-cov
-   Docker + Docker Compose
-   Déploiement Fly.io

------------------------------------------------------------------------

##  Installation locale (sans Docker)

Cette méthode permet de travailler avec Python directement.

``` bash
python -m venv .venv
# Windows
. .venv/Scripts/Activate.ps1
pip install -r requirements.txt

# Copier le fichier d'environnement
cp .env.example .env
```

Configurez ensuite votre base **MariaDB locale**\
et adaptez les valeurs du fichier `.env`.

------------------------------------------------------------------------

## Démarrage complet avec Docker + MariaDB

Le projet utilise MariaDB en local comme en production.\
Le fichier `docker-compose.yml` permet de lancer automatiquement :

-   un conteneur **MariaDB** (`db`)
-   un conteneur **Django** (`web`)

### 1 Préparer le fichier `.env`

``` bash
cp .env.example .env
```

Vérifiez les variables suivantes :

``` env
DB_NAME=jo_db
DB_USER=jo_user
DB_PASSWORD=jo_password
DB_HOST=db
DB_PORT=3306
DB_NAME_TEST=jo_db_test

DEBUG=True
SECRET_KEY=change-me
```

### 2 Lancer tout l'environnement

``` bash
docker compose up --build
```

Cette commande :

-   démarre MariaDB\
-   attend qu'elle soit prête\
-   applique les migrations\
-   démarre Django automatiquement

Accès à l'API :

http://localhost:8000

------------------------------------------------------------------------

## Tests automatisés

Les tests sont intégrés directement dans le dépôt, dans :

    tests/

Ils utilisent une configuration dédiée :

    jo_backend/settings_test.py

### Lancer tous les tests avec couverture :

``` bash
python -m pytest --ds=jo_backend.settings_test --cov --cov-report=term-missing
```

Affiche :

-   tests exécutés\
-   couverture de code\
-   lignes non testées

------------------------------------------------------------------------

## Organisation Git (bonnes pratiques)

-   `main` : branche stable
-   `feature/tests` : intégration des tests
-   `feature/demonstration` : documentation et README
-   `feature/local-startup` : configuration Docker + MariaDB
-   autres branches `feature/*` selon les évolutions

## Conventions de commits

-   `feat:` --- nouvelle fonctionnalité\
-   `fix:` --- correction\
-   `docs:` --- documentation\
-   `test:` --- tests\
-   `chore:` --- maintenance

Plus d'informations dans :

    CONTRIBUTING.md

------------------------------------------------------------------------

## Arborescence Résumée

    jo_backend/
    accounts/
    offers/
    orders/
    tests/
    .env.example
    docker-compose.yml
    pytest.ini
    README.md

------------------------------------------------------------------------

## À propos

Projet développé dans le cadre du **Bloc 3 --- Développement Backend
Django**,\
dans un objectif de création d'un système de billetterie pour les Jeux
Olympiques.

Fonctionnalités intégrées :

-   gestion des utilisateurs\
-   gestion des offres\
-   gestion des billets\
-   gestion des commandes\
-   API REST complète\
-   tests unitaires et d'intégration\
-   conteneurisation Docker\
-   base MariaDB

------------------------------------------------------------------------

## Auteur

Développé par **Rémi Montussac**\
Bloc 3 --- Développement Backend Django.
