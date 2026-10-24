"""Application web du site GLOSS GARAGE (vitrine + demande de réservation)."""

from __future__ import annotations

import base64
import hmac
import json
import os
import re
from contextlib import asynccontextmanager
from datetime import date
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, PlainTextResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.exceptions import HTTPException as StarletteHTTPException

from . import booking, content

BASE_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"


@asynccontextmanager
async def lifespan(_: FastAPI):
    booking.init_db()
    yield


app = FastAPI(title=content.BUSINESS["name"], docs_url=None, redoc_url=None, lifespan=lifespan)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

templates = Jinja2Templates(directory=str(TEMPLATES_DIR))
templates.env.filters["day"] = booking.display_date


def mask_email(value: str) -> str:
    local, _, domain = (value or "").partition("@")
    if not local or not domain:
        return value or ""
    return f"{local[0]}•••@{domain}"


def mask_phone(value: str) -> str:
    digits = re.sub(r"\D", "", value or "")
    if len(digits) < 2:
        return "•••"
    return f"•• •• •• {digits[-2:]}"


templates.env.filters["mask_email"] = mask_email
templates.env.filters["mask_phone"] = mask_phone

# Champ -> étape du formulaire qui le contient (pour rouvrir la bonne étape).
FIELD_STEP = {
    "choice": 1,
    "vehicle_type": 2,
    "vehicle_model": 2,
    "preferred_date": 3,
    "preferred_time": 3,
    "name": 4,
    "email": 4,
    "phone": 4,
    "notes": 4,
    "consent": 5,
}


def canonical_for(path: str) -> str | None:
    base = (content.BUSINESS.get("site_url") or "").rstrip("/")
    return f"{base}{path}" if base else None


def render(request: Request, template: str, status_code: int = 200, **extra) -> HTMLResponse:
    context = {
        "site": content.BUSINESS,
        "services": content.SERVICES,
        "packages": content.PACKAGES,
        "options": content.OPTIONS,
        "faq": content.FAQ,
        "conditions": content.CONDITIONS,
        "payment_note": content.PAYMENT_NOTE,
        "confirmation_note": content.CONFIRMATION_NOTE,
        "prices_missing": any(
            item.get("price") is None for item in content.SERVICES + content.PACKAGES
        ),
        "year": date.today().year,
        "canonical": canonical_for(request.url.path),
        "current_path": request.url.path,
    }
    context.update(extra)
    return templates.TemplateResponse(request, template, context, status_code=status_code)


def local_business_jsonld() -> str:
    site = content.BUSINESS
    data: dict = {
        "@context": "https://schema.org",
        "@type": "AutoWash",
        "name": site["name"],
        "description": f"{site['name']} : {site['tagline'].lower()}.",
    }
    if site.get("site_url"):
        data["url"] = site["site_url"].rstrip("/")
    if site.get("phone"):
        data["telephone"] = site["phone"]
    if site.get("email"):
        data["email"] = site["email"]
    if site.get("address"):
        data["address"] = {"@type": "PostalAddress", "streetAddress": site["address"]}
    if site.get("hours"):
        data["openingHours"] = site["hours"]

    offers = [
        {"@type": "Offer", "name": item["name"], "price": item["price"]}
        for item in content.SERVICES + content.PACKAGES
        if item.get("price")
    ]
    if offers:
        data["hasOfferCatalog"] = {
            "@type": "OfferCatalog",
            "name": "Prestations",
            "itemListElement": offers,
        }
    return json.dumps(data, ensure_ascii=False)


def faq_jsonld() -> str:
    data = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {
                "@type": "Question",
                "name": item["q"],
                "acceptedAnswer": {"@type": "Answer", "text": item["a"]},
            }
            for item in content.FAQ
        ],
    }
    return json.dumps(data, ensure_ascii=False)


def form_dates() -> list[dict]:
    days = booking.available_dates()
    labels = {day.isoformat(): booking.format_day(day) for day in days}
    return [{"iso": day.isoformat(), "label": labels[day.isoformat()]} for day in days]


# --- Pages ---------------------------------------------------------------


@app.get("/", response_class=HTMLResponse)
async def home(request: Request) -> HTMLResponse:
    return render(
        request,
        "index.html",
        jsonld_business=local_business_jsonld(),
        jsonld_faq=faq_jsonld(),
    )


@app.get("/reservation", response_class=HTMLResponse)
async def reservation_form(request: Request) -> HTMLResponse:
    choice = request.query_params.get("service") or request.query_params.get("choice") or ""
    values = {"choice": choice, "options": []}
    return render(
        request,
        "reservation.html",
        values=values,
        errors={},
        dates=form_dates(),
        time_slots=content.BOOKING["time_slots"],
        vehicle_types=content.VEHICLE_TYPES,
        error_step=1,
    )


@app.post("/reservation", response_class=HTMLResponse)
async def reservation_submit(request: Request):
    form = await request.form()

    # Piège à robots : un humain ne remplit jamais ce champ invisible.
    if (form.get("website") or "").strip():
        return RedirectResponse("/reservation", status_code=303)

    payload = {
        "choice": form.get("choice") or "",
        "options": form.getlist("options"),
        "vehicle_type": form.get("vehicle_type") or "",
        "vehicle_model": form.get("vehicle_model") or "",
        "preferred_date": form.get("preferred_date") or "",
        "preferred_time": form.get("preferred_time") or "",
        "name": form.get("name") or "",
        "email": form.get("email") or "",
        "phone": form.get("phone") or "",
        "notes": form.get("notes") or "",
        "consent": form.get("consent") or "",
    }
    data, errors = booking.validate(payload)

    if errors:
        error_step = min(FIELD_STEP[field] for field in errors if field in FIELD_STEP)
        values = dict(payload)
        values["consent"] = payload["consent"] in {"on", "1", "true", "yes"}
        return render(
            request,
            "reservation.html",
            status_code=400,
            values=values,
            errors=errors,
            dates=form_dates(),
            time_slots=content.BOOKING["time_slots"],
            vehicle_types=content.VEHICLE_TYPES,
            error_step=error_step,
        )

    record = booking.create_booking(data)
    return RedirectResponse(f"/reservation/confirmation/{record['reference']}", status_code=303)


@app.get("/reservation/confirmation/{reference}", response_class=HTMLResponse)
async def reservation_confirmation(request: Request, reference: str) -> HTMLResponse:
    record = booking.get_booking(reference)
    if record is None:
        return not_found(request)
    return render(request, "confirmation.html", booking=record)


@app.get("/conditions", response_class=HTMLResponse)
async def conditions(request: Request) -> HTMLResponse:
    return render(request, "conditions.html")


@app.get("/robots.txt", response_class=PlainTextResponse)
async def robots() -> PlainTextResponse:
    lines = ["User-agent: *", "Allow: /", "Disallow: /admin", "Disallow: /reservation/confirmation/"]
    if content.BUSINESS.get("site_url"):
        lines += ["", f"Sitemap: {content.BUSINESS['site_url'].rstrip('/')}/sitemap.xml"]
    return PlainTextResponse("\n".join(lines) + "\n")


@app.get("/sitemap.xml", response_class=PlainTextResponse)
async def sitemap() -> PlainTextResponse:
    base = (content.BUSINESS.get("site_url") or "").rstrip("/")
    if not base:
        # Pas d'adresse publique configurée : sitemap inutile.
        raise StarletteHTTPException(status_code=404)
    urls = ["/", "/reservation", "/conditions"]
    body = "".join(f"<url><loc>{base}{path}</loc></url>" for path in urls)
    xml = f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{body}</urlset>'
    return PlainTextResponse(xml, media_type="application/xml")


@app.get("/admin", response_class=HTMLResponse)
async def admin(request: Request):
    token = os.environ.get("ADMIN_TOKEN", "").strip()
    if not token:
        return not_found(request)
    if not _authorized(request, token):
        return HTMLResponse(
            "Authentification requise.",
            status_code=401,
            headers={"WWW-Authenticate": 'Basic realm="Réservations"'},
        )
    return render(request, "admin.html", bookings=booking.list_bookings())


def _authorized(request: Request, token: str) -> bool:
    header = request.headers.get("authorization", "")
    if not header.lower().startswith("basic "):
        return False
    try:
        decoded = base64.b64decode(header.split(" ", 1)[1]).decode("utf-8")
    except (ValueError, UnicodeDecodeError):
        return False
    _, _, password = decoded.partition(":")
    return hmac.compare_digest(password, token)


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    if exc.status_code == 404:
        return not_found(request)
    return HTMLResponse(str(exc.detail), status_code=exc.status_code)


def not_found(request: Request) -> HTMLResponse:
    return render(request, "404.html", status_code=404)
