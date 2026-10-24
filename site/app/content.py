"""Contenu éditable du site GLOSS GARAGE.

Source unique de vérité : textes, prestations, forfaits et réglages de réservation.
Toute valeur à ``None`` s'affiche comme « à définir » : le propriétaire doit la
compléter (voir site/OWNER_TODO.md). Aucun prix, avis, garantie ou moyen de
paiement n'est inventé ici.
"""

BUSINESS = {
    "name": "GLOSS GARAGE",
    "tagline": "Nettoyage et protection automobile",
    # --- Coordonnées : à compléter par le propriétaire -------------------
    "phone": None,
    "email": None,
    "address": None,
    "hours": None,
    # Adresse publique du site, sans slash final (ex. "https://glossgarage.fr").
    # Tant qu'elle est vide : pas de balise canonical, pas de sitemap.
    "site_url": None,
}

# Durée de réponse/confirmation : pas d'engagement inventé.
CONFIRMATION_NOTE = (
    "Nous vous confirmons le rendez-vous et le tarif avant toute intervention."
)

PAYMENT_NOTE = "Aucun paiement en ligne : ni acompte, ni carte bancaire."

SERVICES = [
    {
        "slug": "lavage-exterieur",
        "name": "Lavage extérieur",
        "summary": "Nettoyage complet de la carrosserie, des jantes et des vitres.",
        "includes": [
            "Prélavage et lavage de la carrosserie",
            "Jantes et passages de roues",
            "Vitres extérieures",
            "Séchage",
        ],
        "price": None,
        "duration": None,
    },
    {
        "slug": "nettoyage-interieur",
        "name": "Nettoyage intérieur",
        "summary": "Habitacle propre, dépoussiéré et aspiré.",
        "includes": [
            "Aspiration des sièges, tapis et coffre",
            "Dépoussiérage des plastiques et du tableau de bord",
            "Vitres intérieures",
        ],
        "price": None,
        "duration": None,
    },
    {
        "slug": "lavage-complet",
        "name": "Lavage complet intérieur + extérieur",
        "summary": "L'ensemble du véhicule, intérieur et extérieur, en une seule visite.",
        "includes": [
            "Toutes les prestations du lavage extérieur",
            "Toutes les prestations du nettoyage intérieur",
        ],
        "price": None,
        "duration": None,
    },
    {
        "slug": "polissage",
        "name": "Polissage / lustrage",
        "summary": "Correction des micro-rayures et retour de la brillance.",
        "includes": [
            "Lavage préalable",
            "Polissage de la peinture",
            "Finition lustrée",
        ],
        "price": None,
        "duration": None,
    },
    {
        "slug": "protection-ceramique",
        "name": "Traitement céramique",
        "summary": "Protection de la peinture sur la durée, après préparation.",
        "includes": [
            "Préparation et décontamination de la peinture",
            "Application du traitement céramique",
        ],
        "price": None,
        "duration": None,
    },
    {
        "slug": "sieges-tapis",
        "name": "Nettoyage des sièges et tapis",
        "summary": "Nettoyage en profondeur des tissus de l'habitacle.",
        "includes": [
            "Injection-extraction sur les sièges et tapis",
            "Séchage",
        ],
        "price": None,
        "duration": None,
    },
]

# Forfaits : regroupements de prestations existantes, sans prix inventé.
PACKAGES = [
    {
        "slug": "entretien",
        "name": "Forfait Entretien",
        "summary": "Le nécessaire pour garder le véhicule propre au quotidien.",
        "includes": ["Lavage extérieur", "Nettoyage intérieur"],
        "price": None,
        "duration": None,
    },
    {
        "slug": "complet",
        "name": "Forfait Complet",
        "summary": "Intérieur, extérieur et brillance de la peinture.",
        "includes": ["Lavage complet intérieur + extérieur", "Polissage / lustrage"],
        "price": None,
        "duration": None,
    },
    {
        "slug": "protection",
        "name": "Forfait Protection",
        "summary": "Préparer la peinture puis la protéger durablement.",
        "includes": ["Polissage / lustrage", "Traitement céramique"],
        "price": None,
        "duration": None,
    },
]

# Options à ajouter à une prestation ou à un forfait.
OPTIONS = [
    {
        "slug": "phares",
        "name": "Rénovation des phares",
        "summary": "Phares ternis ou jaunis remis en état.",
        "price": None,
    },
    {
        "slug": "anti-odeurs",
        "name": "Traitement anti-odeurs",
        "summary": "Traitement de l'habitacle contre les mauvaises odeurs.",
        "price": None,
    },
    {
        "slug": "poils-animaux",
        "name": "Poils d'animaux",
        "summary": "Retrait des poils incrustés dans les tissus.",
        "price": None,
    },
]

VEHICLE_TYPES = ["Citadine", "Berline", "SUV / 4x4", "Utilitaire", "Autre"]

BOOKING = {
    # Créneaux souhaités proposés dans le formulaire (le garage confirme ensuite).
    "time_slots": ["08:00", "09:30", "11:00", "14:00", "15:30", "17:00"],
    # Jours fermés, 0 = lundi … 6 = dimanche.
    "closed_weekdays": [6],
    # Délai minimum avant le créneau souhaité, en jours.
    "lead_days": 1,
    # Nombre de jours proposés à partir d'aujourd'hui.
    "horizon_days": 45,
}

# Conditions affichées avant la confirmation (page /conditions).
CONDITIONS = [
    {
        "title": "Votre demande de réservation",
        "paragraphs": [
            "Le formulaire enregistre une demande avec la prestation, le véhicule et "
            "le créneau souhaités. Le créneau choisi n'est pas encore réservé : il "
            "devient un rendez-vous lorsque le garage vous le confirme.",
            "Le garage vous recontacte avec les coordonnées que vous avez indiquées "
            "pour confirmer le rendez-vous et le tarif.",
        ],
    },
    {
        "title": "Prix",
        "paragraphs": [
            "Le tarif de la prestation vous est communiqué avant l'intervention. "
            "Tant qu'un prix n'est pas publié sur le site, il est indiqué "
            "« à définir » : ce n'est ni un prix ferme ni un engagement.",
            "Le prix peut dépendre de l'état et de la taille du véhicule. Le tarif "
            "annoncé avant l'intervention reste celui appliqué.",
        ],
    },
    {
        "title": "Annulation et report",
        "paragraphs": [
            "Vous pouvez annuler votre demande à tout moment avant la confirmation, "
            "sans frais.",
            "Après confirmation, prévenez le garage dès que possible en rappelant "
            "votre référence de demande : le rendez-vous peut être annulé ou reporté "
            "selon les disponibilités.",
        ],
    },
    {
        "title": "Paiement et remboursement",
        "paragraphs": [
            PAYMENT_NOTE + " Aucun acompte n'est demandé en ligne et aucune donnée "
            "bancaire n'est collectée par ce site.",
            "Le règlement de la prestation est convenu directement avec le garage. "
            "En cas de litige sur un montant déjà réglé, le garage applique ses "
            "propres conditions de remboursement, communiquées sur demande.",
        ],
    },
    {
        "title": "Données personnelles",
        "paragraphs": [
            "Le formulaire collecte uniquement : la prestation choisie, le type et le "
            "modèle du véhicule, le créneau souhaité, votre nom, votre e-mail et votre "
            "téléphone, ainsi que vos remarques si vous en ajoutez.",
            "Ces informations servent uniquement à traiter votre demande de "
            "réservation et à vous contacter à ce sujet.",
            "Pour consulter, corriger ou supprimer vos informations, contactez le "
            "garage en indiquant votre référence de demande.",
        ],
    },
]

FAQ = [
    {
        "q": "Le créneau que je choisis est-il réservé immédiatement ?",
        "a": "Non. C'est un créneau souhaité. Il devient un rendez-vous quand le "
        "garage vous le confirme, avec le tarif.",
    },
    {
        "q": "Dois-je payer en ligne ?",
        "a": "Non. Aucun paiement en ligne n'est proposé aujourd'hui : pas d'acompte, "
        "pas de carte bancaire. Le règlement est convenu directement avec le garage.",
    },
    {
        "q": "Pourquoi certains prix indiquent-ils « à définir » ?",
        "a": "Le garage publie ses tarifs lui-même. Tant qu'un prix n'est pas publié, "
        "il est confirmé avec vous avant l'intervention : le site n'affiche pas de "
        "prix estimé.",
    },
    {
        "q": "Puis-je annuler ma demande ?",
        "a": "Oui, sans frais tant que le rendez-vous n'est pas confirmé. Les "
        "modalités d'annulation et de report sont détaillées dans les conditions de "
        "réservation.",
    },
    {
        "q": "Quelles informations sont collectées ?",
        "a": "Uniquement ce qui est nécessaire pour traiter la demande : prestation, "
        "véhicule, créneau souhaité, nom, e-mail, téléphone et remarques éventuelles.",
    },
]

# Réponse de secours si une page n'existe pas.
NOT_FOUND = "Cette page n'existe pas ou plus."
