# Workflow Git du projet

Ce projet utilise un workflow Git simple inspiré des bonnes pratiques professionnelles.

## Branches principales

- `main` : branche stable, toujours dans un état déployable.  
- `feature/*` : branches de développement pour les nouvelles fonctionnalités ou améliorations.

## Création d'une nouvelle fonctionnalité

1. Se mettre à jour sur `main` :

```bash
git checkout main
git pull
