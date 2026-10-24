"""Consultation des demandes de réservation enregistrées.

Exemples (depuis le conteneur) :
    docker compose -f docker-compose.base44.yml exec site python -m app.cli list
    docker compose -f docker-compose.base44.yml exec site python -m app.cli export --output /data/bookings.json
"""

from __future__ import annotations

import argparse
import json

from . import booking


def main() -> None:
    parser = argparse.ArgumentParser(description="Demandes de réservation GLOSS GARAGE")
    subparsers = parser.add_subparsers(dest="command", required=True)

    list_parser = subparsers.add_parser("list", help="Afficher les demandes récentes")
    list_parser.add_argument("--limit", type=int, default=50)

    export_parser = subparsers.add_parser("export", help="Exporter les demandes en JSON")
    export_parser.add_argument("--output", default="bookings.json")
    export_parser.add_argument("--limit", type=int, default=1000)

    args = parser.parse_args()
    booking.init_db()

    if args.command == "list":
        rows = booking.list_bookings(args.limit)
        if not rows:
            print("Aucune demande enregistrée.")
            return
        for row in rows:
            print(
                f"{row['reference']}  {row['preferred_date']} {row['preferred_time']}  "
                f"{row['choice_label']}  {row['vehicle_type']} {row['vehicle_model']}  "
                f"{row['name']} <{row['email']}> {row['phone']}"
                + (f"  — {row['options']}" if row["options"] else "")
                + (f"  — {row['notes']}" if row["notes"] else "")
            )
        return

    rows = booking.list_bookings(args.limit)
    with open(args.output, "w", encoding="utf-8") as handle:
        json.dump(rows, handle, ensure_ascii=False, indent=2)
    print(f"{len(rows)} demande(s) exportée(s) vers {args.output}")


if __name__ == "__main__":
    main()
