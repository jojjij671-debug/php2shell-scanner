# Site GLOSS GARAGE

Site vitrine + demande de réservation, en français, sans dépendance front-end
(pas de framework CSS, pas de police distante, pas d'image lourde). Une seule
petite application FastAPI sert les pages et enregistre les demandes dans SQLite.

> Ce dossier est indépendant du scanner Python présent à la racine du dépôt
> (`scanner.py`), qui n'est pas modifié.

## Lancer en local

```bash
docker compose -f docker-compose.base44.yml up -d     # http://localhost:3000
docker compose -f docker-compose.base44.yml logs -f site
```

Tests :

```bash
docker compose -f docker-compose.base44.yml exec site \
  sh -ec "pip install --no-cache-dir -r requirements-dev.txt && python -m pytest -q"
```

## Structure

| Chemin | Rôle |
| --- | --- |
| `app/content.py` | **Tout le contenu éditable** : coordonnées, prestations, forfaits, options, créneaux, conditions, FAQ |
| `app/booking.py` | Validation de la demande, créneaux disponibles, stockage SQLite |
| `app/main.py` | Routes HTTP, métadonnées SEO, JSON-LD |
| `app/templates/` | Pages Jinja2 (accueil, réservation, confirmation, conditions, admin, 404) |
| `app/static/` | `styles.css` et `booking.js` (assistant en 5 étapes, sans dépendance) |
| `app/cli.py` | Consultation / export des demandes en ligne de commande |
| `tests/test_site.py` | Vérifications des pages et du formulaire |

## Pages

- `/` — prestations, forfaits, options, déroulement, transparence, FAQ, contact
- `/reservation` — assistant en 5 étapes (prestation → véhicule → créneau →
  coordonnées → récapitulatif + conditions). Fonctionne aussi sans JavaScript.
- `/reservation/confirmation/<référence>` — récapitulatif, prochaine étape,
  coordonnées masquées, page en `noindex`
- `/conditions` — réservation, prix, annulation, remboursement, données
  personnelles
- `/admin` — liste des demandes, protégée par `ADMIN_TOKEN` (404 si absent)
- `/robots.txt`, `/sitemap.xml` (sitemap seulement si `site_url` est configuré)

## Consulter les demandes

```bash
# jeton d'administration (facultatif) : variable ADMIN_TOKEN dans les secrets Base44
docker compose -f docker-compose.base44.yml exec site python -m app.cli list
docker compose -f docker-compose.base44.yml exec site \
  python -m app.cli export --output /data/bookings.json
```

La base vit dans le volume Docker `bookings-data` (`/data/bookings.db`), donc
elle survit aux redémarrages.

## Ce que le site ne fait pas (volontairement)

- Aucun prix inventé : les tarifs non publiés s'affichent « Tarif à définir ».
- Aucun paiement ni acompte en ligne, aucune donnée bancaire collectée.
- Aucun avis client, aucune garantie, aucune urgence artificielle.
- Aucun compte client ni programme de fidélité : rien dans l'application ne
  permettrait de le gérer honnêtement aujourd'hui.

Voir `OWNER_TODO.md` pour la liste des éléments à compléter.
