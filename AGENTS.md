# AGENTS.md — notes pour les sessions suivantes

## Deux projets distincts dans ce dépôt

- `scanner.py` (+ `Dockerfile`, `requirements.txt` racine) : scanner PHP en ligne
  de commande. **Ne pas modifier** quand la demande concerne le site.
- `site/` : site GLOSS GARAGE (FastAPI + Jinja2 + SQLite). C'est ce que sert la
  preview sur le port 3000.

## Lancer / vérifier

```bash
docker compose -f docker-compose.base44.yml up -d --build
docker compose -f docker-compose.base44.yml ps
curl -s -o /dev/null -w '%{http_code}\n' http://localhost:3000/
```

- Pas de Dockerfile pour le site : l'image est `python:3.12-slim`, le dépôt est
  monté sur `/app`, et `pip install` s'exécute au démarrage du conteneur (les
  dépendances ne sont pas dans l'image). Un changement de `site/requirements.txt`
  n'est donc pris en compte qu'au prochain redémarrage du service.
- `uvicorn --reload` avec `WATCHFILES_FORCE_POLLING=true` : les modifications de
  `site/app/**` sont rechargées automatiquement (templates et CSS compris).
- Port hôte **3000** → uvicorn **8000** dans le conteneur.

## Données

- Les demandes de réservation sont dans SQLite, hors du dépôt :
  `DATABASE_PATH=/data/bookings.db`, volume Docker nommé `bookings-data`.
  **Ne jamais supprimer ce volume** (perte des demandes réelles).
- Tests : `docker compose -f docker-compose.base44.yml exec site sh -ec "pip install --no-cache-dir -r requirements-dev.txt && python -m pytest -q"`.
  Les tests utilisent une base temporaire via `DATABASE_PATH`, jamais le volume.
- Les tests créent leurs propres demandes dans une base jetable : ne pas écrire
  de données de test dans le volume partagé.

## Contenu et règles éditoriales

- Tout le texte et les tarifs sont dans `site/app/content.py`. Une valeur `None`
  est affichée « à compléter » / « Tarif à définir » : c'est volontaire.
- **Ne jamais inventer** de prix, d'avis client, de garantie, de moyen de
  paiement, d'urgence ou de délai de réponse. Le propriétaire complète
  `site/OWNER_TODO.md`.
- Pas de paiement en ligne : aucun connecteur de paiement n'est configuré, le
  site ne doit simuler ni acompte ni transaction.

## Administration

- `/admin` liste les demandes. Elle répond 404 tant que `ADMIN_TOKEN` n'est pas
  défini (secret Base44 livré via `/run/base44/app.env`). Authentification
  HTTP Basic, identifiant `admin`.
- Sans jeton : `python -m app.cli list` (exécuté dans le conteneur).

## Pièges

- `site/app/templates/base.html` pose `html.no-js` puis la retire dans un script
  inline : sans cette classe, l'assistant de réservation resterait affiché en
  entier. Ne pas retirer cette ligne.
- Le formulaire de réservation est utilisable sans JavaScript (toutes les étapes
  visibles) ; `booking.js` ne fait qu'ajouter la navigation par étapes.
- La page de confirmation masque e-mail et téléphone (filtres `mask_email`,
  `mask_phone`) : la référence seule ne doit pas exposer les coordonnées.
