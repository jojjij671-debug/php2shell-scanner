"""Réservations : validation, créneaux et stockage SQLite."""

from __future__ import annotations

import os
import re
import secrets
import sqlite3
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

from . import content

JOURS = (
    "lundi",
    "mardi",
    "mercredi",
    "jeudi",
    "vendredi",
    "samedi",
    "dimanche",
)
MOIS = (
    "janvier",
    "février",
    "mars",
    "avril",
    "mai",
    "juin",
    "juillet",
    "août",
    "septembre",
    "octobre",
    "novembre",
    "décembre",
)

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[A-Za-z]{2,}$")
PHONE_RE = re.compile(r"^[+0-9 ()./-]{6,24}$")

REFERENCE_ALPHABET = "ACDEFGHJKLMNPQRSTUVWXYZ23456789"

SCHEMA = """
CREATE TABLE IF NOT EXISTS bookings (
    reference TEXT PRIMARY KEY,
    created_at TEXT NOT NULL,
    choice TEXT NOT NULL,
    choice_label TEXT NOT NULL,
    options TEXT NOT NULL DEFAULT '',
    vehicle_type TEXT NOT NULL,
    vehicle_model TEXT NOT NULL DEFAULT '',
    preferred_date TEXT NOT NULL,
    preferred_time TEXT NOT NULL,
    name TEXT NOT NULL,
    email TEXT NOT NULL,
    phone TEXT NOT NULL,
    notes TEXT NOT NULL DEFAULT '',
    consent INTEGER NOT NULL DEFAULT 0
)
"""


def database_path() -> Path:
    """Chemin de la base, surchargeable avec DATABASE_PATH (volume Docker)."""
    default = Path(__file__).resolve().parent.parent / "data" / "bookings.db"
    return Path(os.environ.get("DATABASE_PATH", default))


def connect() -> sqlite3.Connection:
    path = database_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with connect() as conn:
        conn.execute(SCHEMA)


def format_day(day: date) -> str:
    """« samedi 25 octobre » — sans dépendre de la locale du système."""
    return f"{JOURS[day.weekday()]} {day.day} {MOIS[day.month - 1]}"


def available_dates(today: date | None = None) -> list[date]:
    today = today or date.today()
    start = today + timedelta(days=content.BOOKING["lead_days"])
    closed = set(content.BOOKING["closed_weekdays"])
    days = []
    for offset in range(content.BOOKING["horizon_days"]):
        day = start + timedelta(days=offset)
        if day.weekday() not in closed:
            days.append(day)
    return days


def catalogue() -> dict[str, str]:
    """Identifiants réservables -> libellé."""
    items = {}
    for service in content.SERVICES:
        items[f"service:{service['slug']}"] = service["name"]
    for package in content.PACKAGES:
        items[f"forfait:{package['slug']}"] = package["name"]
    return items


def option_labels() -> dict[str, str]:
    return {option["slug"]: option["name"] for option in content.OPTIONS}


def _clean_text(value: str, limit: int) -> str:
    return " ".join((value or "").split())[:limit]


def validate(payload: dict) -> tuple[dict, dict[str, str]]:
    """Nettoie et valide une demande. Retourne (données, erreurs par champ)."""
    errors: dict[str, str] = {}
    choices = catalogue()
    options = option_labels()

    choice = (payload.get("choice") or "").strip()
    if choice not in choices:
        errors["choice"] = "Choisissez une prestation ou un forfait."

    selected_options = [item for item in payload.get("options") or [] if item in options]

    vehicle_type = (payload.get("vehicle_type") or "").strip()
    if vehicle_type not in content.VEHICLE_TYPES:
        errors["vehicle_type"] = "Indiquez le type de véhicule."

    vehicle_model = _clean_text(payload.get("vehicle_model", ""), 80)
    if not vehicle_model:
        errors["vehicle_model"] = "Indiquez la marque et le modèle du véhicule."

    allowed_days = {day.isoformat() for day in available_dates()}
    preferred_date = (payload.get("preferred_date") or "").strip()
    if preferred_date not in allowed_days:
        errors["preferred_date"] = "Choisissez un jour parmi ceux proposés."

    preferred_time = (payload.get("preferred_time") or "").strip()
    if preferred_time not in content.BOOKING["time_slots"]:
        errors["preferred_time"] = "Choisissez un créneau horaire."

    name = _clean_text(payload.get("name", ""), 80)
    if len(name) < 2:
        errors["name"] = "Indiquez votre nom."

    email = (payload.get("email") or "").strip()[:120]
    if not EMAIL_RE.match(email):
        errors["email"] = "Indiquez une adresse e-mail valide."

    phone = (payload.get("phone") or "").strip()[:24]
    if not PHONE_RE.match(phone) or len(re.sub(r"\D", "", phone)) < 6:
        errors["phone"] = "Indiquez un numéro de téléphone valide."

    notes = (payload.get("notes") or "").strip()[:500]

    consent = payload.get("consent") in {"on", "1", "true", "yes"}
    if not consent:
        errors["consent"] = "Cochez cette case pour envoyer votre demande."

    data = {
        "choice": choice,
        "choice_label": choices.get(choice, ""),
        "options": selected_options,
        "vehicle_type": vehicle_type,
        "vehicle_model": vehicle_model,
        "preferred_date": preferred_date,
        "preferred_time": preferred_time,
        "name": name,
        "email": email,
        "phone": phone,
        "notes": notes,
        "consent": consent,
    }
    return data, errors


def _new_reference(conn: sqlite3.Connection) -> str:
    while True:
        reference = "GG-" + "".join(secrets.choice(REFERENCE_ALPHABET) for _ in range(6))
        row = conn.execute(
            "SELECT 1 FROM bookings WHERE reference = ?", (reference,)
        ).fetchone()
        if row is None:
            return reference


def create_booking(data: dict) -> dict:
    created_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    with connect() as conn:
        reference = _new_reference(conn)
        conn.execute(
            """INSERT INTO bookings (
                reference, created_at, choice, choice_label, options, vehicle_type,
                vehicle_model, preferred_date, preferred_time, name, email, phone,
                notes, consent
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                reference,
                created_at,
                data["choice"],
                data["choice_label"],
                ", ".join(option_labels()[slug] for slug in data["options"]),
                data["vehicle_type"],
                data["vehicle_model"],
                data["preferred_date"],
                data["preferred_time"],
                data["name"],
                data["email"],
                data["phone"],
                data["notes"],
                1 if data["consent"] else 0,
            ),
        )
    data["reference"] = reference
    data["created_at"] = created_at
    return data


def get_booking(reference: str) -> dict | None:
    with connect() as conn:
        row = conn.execute(
            "SELECT * FROM bookings WHERE reference = ?", (reference,)
        ).fetchone()
    return dict(row) if row else None


def list_bookings(limit: int = 200) -> list[dict]:
    with connect() as conn:
        rows = conn.execute(
            "SELECT * FROM bookings ORDER BY created_at DESC LIMIT ?", (limit,)
        ).fetchall()
    return [dict(row) for row in rows]


def display_date(iso_date: str) -> str:
    """« samedi 25 octobre 2026 » depuis « 2026-10-25 »."""
    try:
        return f"{format_day(date.fromisoformat(iso_date))} {iso_date[:4]}"
    except ValueError:
        return iso_date
