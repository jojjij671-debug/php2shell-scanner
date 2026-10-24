# À compléter par le propriétaire

Tout le contenu éditable est dans **`site/app/content.py`**. Les valeurs à
`None` s'affichent « à compléter » ou « Tarif à définir » : rien n'a été inventé.

## 1. Coordonnées (obligatoire avant mise en ligne)

Dans `BUSINESS` :

- [ ] `phone` — téléphone du garage (affiché dans le pied de page, la page
      contact et les données structurées)
- [ ] `email` — adresse de contact
- [ ] `address` — adresse postale
- [ ] `hours` — horaires d'ouverture (texte libre)
- [ ] `site_url` — adresse publique du site, sans slash final. Tant qu'elle est
      vide : pas de balise `canonical` et pas de `sitemap.xml`.

## 2. Prestations et tarifs

- [ ] Confirmer la liste `SERVICES` : noms, descriptions, contenu inclus.
      La liste actuelle est un catalogue de départ (lavage, intérieur, polissage,
      céramique…) à valider.
- [ ] Renseigner `price` pour chaque prestation (texte libre : `"45 €"`,
      `"à partir de 90 €"`…) et `duration` si utile.
- [ ] Valider les trois `PACKAGES` (Entretien, Complet, Protection) et leur prix.
      Un forfait reprend des prestations existantes : ne pas ajouter de contenu
      qui n'est pas réalisé.
- [ ] Valider `OPTIONS` et leurs prix.

Tant qu'un `price` reste `None`, la page affiche « Tarif à définir » et le site
indique que le prix est confirmé avant l'intervention.

## 3. Créneaux

Dans `BOOKING` :

- [ ] `time_slots` — horaires proposés dans le formulaire
- [ ] `closed_weekdays` — jours fermés (`0` = lundi … `6` = dimanche)
- [ ] `lead_days` / `horizon_days` — délai minimum et nombre de jours proposés

Le formulaire présente un **créneau souhaité**, pas une disponibilité réservée :
le garage confirme l'horaire.

## 4. Conditions de réservation

Page `/conditions`, contenu dans `CONDITIONS` :

- [ ] Vérifier le délai d'annulation souhaité (le texte actuel reste volontairement
      sans chiffre : annulation sans frais avant confirmation, puis contact du garage).
- [ ] Ajouter les garanties éventuelles et les moyens de paiement acceptés sur place.
- [ ] Compléter la section « Données personnelles » (durée de conservation,
      responsable de traitement, contact pour une demande de suppression) si
      votre juridiction l'exige.

## 5. Paiement en ligne

Aucun moyen de paiement n'est configuré : le site ne simule aucun paiement, ne
demande ni acompte ni carte bancaire, et indique clairement la prochaine étape
(confirmation par le garage, règlement convenu sur place).

Si vous ajoutez plus tard un paiement ou un acompte en ligne, il faudra aussi
mettre à jour `PAYMENT_NOTE`, la page `/conditions` et la page de confirmation.

## 6. Programme de fidélité

Aucun programme de fidélité n'est affiché : il n'existe pas de règle commerciale
à appliquer. Les demandes sont stockées, donc un système de suivi serait
techniquement possible, mais l'offre (remise, seuil, validité) doit d'abord être
décidée par le propriétaire.

## 7. Accès aux demandes

- [ ] Facultatif : créer un secret **`ADMIN_TOKEN`** dans les secrets Base44 pour
      activer la page `/admin` (identifiant `admin`, mot de passe = valeur du
      jeton). Sans jeton, la page répond 404.
- [ ] Sans jeton, les demandes restent consultables en ligne de commande :

```bash
docker compose -f docker-compose.base44.yml exec site python -m app.cli list
```

- [ ] Prévoir le suivi : aucune notification e-mail n'est envoyée (aucun service
      d'e-mail n'est configuré). Le garage doit consulter les demandes et
      recontacter le client.

## 8. Avant la mise en ligne

- [ ] Vérifier les liens du pied de page et des boutons « Réserver ».
- [ ] Envoyer une demande de test, puis la supprimer de la base.
- [ ] Mettre à jour `robots.txt` / `sitemap.xml` quand `site_url` est renseigné.
