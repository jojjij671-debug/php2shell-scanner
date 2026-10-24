"""Tests de bout en bout du site (pages, formulaire, persistance)."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app import booking, content, main


@pytest.fixture()
def client(tmp_path, monkeypatch):
    monkeypatch.setenv("DATABASE_PATH", str(tmp_path / "test.db"))
    monkeypatch.delenv("ADMIN_TOKEN", raising=False)
    with TestClient(main.app) as test_client:
        yield test_client


def valid_payload(**overrides) -> dict:
    payload = {
        "choice": f"service:{content.SERVICES[0]['slug']}",
        "vehicle_type": content.VEHICLE_TYPES[0],
        "vehicle_model": "Peugeot 208",
        "preferred_date": booking.available_dates()[0].isoformat(),
        "preferred_time": content.BOOKING["time_slots"][0],
        "name": "Camille Test",
        "email": "camille@example.com",
        "phone": "06 12 34 56 78",
        "notes": "Sièges en tissu clair",
        "consent": "on",
    }
    payload.update(overrides)
    return payload


def test_home_lists_services_and_prices(client):
    response = client.get("/")
    assert response.status_code == 200
    body = response.text
    for service in content.SERVICES:
        assert service["name"] in body
    assert "Tarif à définir" in body
    assert "Aucun paiement en ligne" in body
    assert "application/ld+json" in body


def test_reservation_form_renders(client):
    response = client.get("/reservation")
    assert response.status_code == 200
    assert 'name="choice"' in response.text
    assert "J'ai lu les conditions" in response.text


def test_valid_booking_is_stored_and_shown(client):
    response = client.post("/reservation", data=valid_payload(), follow_redirects=False)
    assert response.status_code == 303
    location = response.headers["location"]
    assert location.startswith("/reservation/confirmation/GG-")

    confirmation = client.get(location)
    assert confirmation.status_code == 200
    assert "Merci Camille Test" in confirmation.text
    assert "Peugeot 208" in confirmation.text
    # Les coordonnées sont masquées sur la page publique.
    assert "camille@example.com" not in confirmation.text

    reference = location.rsplit("/", 1)[-1]
    record = booking.get_booking(reference)
    assert record is not None
    assert record["email"] == "camille@example.com"
    assert record["options"] == ""


def test_invalid_email_is_rejected(client):
    response = client.post("/reservation", data=valid_payload(email="pas-un-email"))
    assert response.status_code == 400
    assert "adresse e-mail valide" in response.text
    assert 'data-open-step="4"' in response.text
    assert booking.list_bookings() == []


def test_missing_consent_is_rejected(client):
    payload = valid_payload()
    payload.pop("consent")
    response = client.post("/reservation", data=payload)
    assert response.status_code == 400
    assert "Cochez cette case" in response.text


def test_options_are_saved(client):
    payload = valid_payload()
    payload["options"] = [content.OPTIONS[0]["slug"], content.OPTIONS[1]["slug"]]
    response = client.post("/reservation", data=payload, follow_redirects=False)
    assert response.status_code == 303
    reference = response.headers["location"].rsplit("/", 1)[-1]
    record = booking.get_booking(reference)
    assert record["options"] == f"{content.OPTIONS[0]['name']}, {content.OPTIONS[1]['name']}"


def test_honeypot_is_ignored(client):
    payload = valid_payload(website="http://spam.example")
    response = client.post("/reservation", data=payload, follow_redirects=False)
    assert response.status_code == 303
    assert response.headers["location"] == "/reservation"
    assert booking.list_bookings() == []


def test_conditions_page(client):
    response = client.get("/conditions")
    assert response.status_code == 200
    assert "Annulation" in response.text
    assert "Données personnelles" in response.text


def test_unknown_page_is_not_found(client):
    assert client.get("/pas-de-page").status_code == 404


def test_confirmation_unknown_reference(client):
    assert client.get("/reservation/confirmation/GG-XXXXXX").status_code == 404


def test_admin_is_disabled_without_token(client):
    assert client.get("/admin").status_code == 404


def test_robots(client):
    response = client.get("/robots.txt")
    assert response.status_code == 200
    assert "Disallow: /admin" in response.text
