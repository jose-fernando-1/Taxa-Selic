from __future__ import annotations

from datetime import date

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .bcb import BCBClient, BCBClientError
from .service import EconomicDataService
from .storage import SeriesStorage


storage = SeriesStorage()
service = EconomicDataService(client=BCBClient(), storage=storage)
app = FastAPI(title="Indicadores Banco Central", version="2.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _parse_iso_date(value: str | None) -> date | None:
    if not value:
        return None
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=f"Data inválida: {value}") from exc


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/api/series")
def list_series() -> list[dict]:
    return service.list_series()


@app.get("/api/series/{slug}")
def get_series(slug: str, start: str | None = None, end: str | None = None) -> dict:
    try:
        return service.get_series(slug, start=_parse_iso_date(start), end=_parse_iso_date(end))
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except BCBClientError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@app.get("/api/series/{slug}/latest")
def get_latest(slug: str) -> dict:
    payload = get_series(slug)
    return {
        "series": payload["series"],
        "latest": payload["latest"],
    }


@app.get("/api/charts/{slug}")
def get_chart(slug: str, start: str | None = None, end: str | None = None) -> dict:
    try:
        return service.get_chart(slug, start=_parse_iso_date(start), end=_parse_iso_date(end))
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except BCBClientError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@app.post("/api/refresh")
def refresh_all() -> JSONResponse:
    try:
        payload = service.update_all()
        service.export_legacy_selic()
        return JSONResponse(payload)
    except BCBClientError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@app.post("/api/refresh/{slug}")
def refresh_series(slug: str) -> dict:
    try:
        payload = service.update_series(slug)
        if slug == "selic-diaria":
            service.export_legacy_selic()
        return payload
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except BCBClientError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc