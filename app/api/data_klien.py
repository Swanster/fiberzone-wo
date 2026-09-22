"""API Data Klien per FDT/FAT — sinkron dari Google Sheets.

Sumber: spreadsheet Fiberzone ODP Bali & Nusra 2026, sheet "Data Klien (Flat)"
dan "Ringkasan FAT". Hasil di-cache in-memory 15 menit; kalau fetch Sheets
gagal, endpoint tetap 200 dengan data cache terakhir (field `stale`).

OAuth memakai token yang sama dengan route export (`/api/*/export`).
"""

from __future__ import annotations

import json
import os
import threading
import time
from pathlib import Path
from typing import Any

import httpx
from fastapi import APIRouter, Query

TOKEN_PATH = Path(
    os.environ.get("GOOGLE_TOKEN_PATH", "/home/infra/.hermes/google_token.json")
)
SHEET_ID = os.environ.get(
    "DATA_KLIEN_SHEET_ID", "1IaXndCgD2fmPbgRAb7LvppyKqrBxal_cXWXH7AhIc50"
)
SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/edit#gid=1500672746"
RANGE_FLAT = "'Data Klien (Flat)'!A1:Z2000"
RANGE_FAT = "'Ringkasan FAT'!A1:Z2000"
TOKEN_URL = "https://oauth2.googleapis.com/token"
SHEETS_VALUES_URL = (
    f"https://sheets.googleapis.com/v4/spreadsheets/{SHEET_ID}/values"
)
CACHE_TTL_SECONDS = 900

router = APIRouter(prefix="/api/data-klien", tags=["data-klien"])

_lock = threading.Lock()
_cache: dict[str, Any] | None = None
_fetched_at = 0.0
_last_good: dict[str, Any] | None = None
_last_error: str | None = None


def _cell(row: list[Any], idx: int | None) -> str:
    if idx is None or idx >= len(row):
        return ""
    value = row[idx]
    if value is None:
        return ""
    return str(value).strip()


def _number(value: str) -> int:
    try:
        digits = "".join(ch for ch in str(value) if ch.isdigit() or ch in "-.")
        return int(float(digits)) if digits else 0
    except ValueError:
        return 0


def _header_index(header_row: list[Any]) -> dict[str, int]:
    return {str(h or "").strip(): i for i, h in enumerate(header_row)}


def parse_sheets(flat_rows: list[list[Any]], fat_rows: list[list[Any]]) -> dict[str, Any]:
    """Parsing murni (tanpa jaringan) → payload siap kirim ke frontend."""
    if not flat_rows:
        raise ValueError("Sheet 'Data Klien (Flat)' kosong")

    flat = _header_index(flat_rows[0])
    items: list[dict[str, Any]] = []
    fat_set: set[str] = set()
    fdt_set: set[str] = set()
    by_pop: dict[str, int] = {}
    by_tipe: dict[str, int] = {}
    aktif = disconnect = tanpa_fdt = 0

    for row in flat_rows[1:]:
        fdt = _cell(row, flat.get("FDT"))
        fat = _cell(row, flat.get("FAT"))
        nama = _cell(row, flat.get("Nama Klien"))
        if not nama and not fdt and not fat:
            continue
        status = _cell(row, flat.get("Status"))
        pop = _cell(row, flat.get("POP")) or "-"
        tipe = _cell(row, flat.get("Tipe")) or "-"
        items.append(
            {
                "no": _number(_cell(row, flat.get("No"))) or len(items) + 1,
                "pop": pop,
                "fdt": fdt,
                "fat": fat,
                "port": _cell(row, flat.get("Port")),
                "client_id": _cell(row, flat.get("Client ID")),
                "nama": nama,
                "tipe": tipe,
                "status": status,
                "sumber": _cell(row, flat.get("Sumber")),
                "via_splitter": _cell(row, flat.get("Via Splitter")),
            }
        )
        fat_set.add(fat) if fat else None
        fdt_set.add(fdt) if fdt else None
        tanpa_fdt += 0 if fdt else 1
        by_pop[pop] = by_pop.get(pop, 0) + 1
        by_tipe[tipe] = by_tipe.get(tipe, 0) + 1
        if status.upper() == "ACTIVE":
            aktif += 1
        elif status.upper() == "DISCONNECT":
            disconnect += 1

    fat_map = _header_index(fat_rows[0]) if fat_rows else {}
    fat_summary: list[dict[str, Any]] = []
    for row in fat_rows[1:]:
        fat = _cell(row, fat_map.get("FAT"))
        if not fat:
            continue
        fat_summary.append(
            {
                "pop": _cell(row, fat_map.get("POP")),
                "fdt": _cell(row, fat_map.get("FDT")),
                "fat": fat,
                "total_port": _number(_cell(row, fat_map.get("Total Port"))),
                "port_terisi": _number(_cell(row, fat_map.get("Port Terisi"))),
                "klien_aktif": _number(_cell(row, fat_map.get("Klien Aktif"))),
                "klien_disconnect": _number(_cell(row, fat_map.get("Klien Disconnect"))),
                "total_klien": _number(_cell(row, fat_map.get("Total Klien"))),
                "power_in": _cell(row, fat_map.get("Power In (dBm)")),
                "power_out": _cell(row, fat_map.get("Power Out (dBm)")),
                "koordinat": _cell(row, fat_map.get("Koordinat")),
            }
        )

    return {
        "items": items,
        "fat_summary": fat_summary,
        "summary": {
            "total": len(items),
            "aktif": aktif,
            "disconnect": disconnect,
            "fdt_count": len(fdt_set),
            "fat_count": len(fat_set),
            "tanpa_fdt": tanpa_fdt,
            "by_pop": dict(sorted(by_pop.items(), key=lambda kv: -kv[1])),
            "by_tipe": dict(sorted(by_tipe.items(), key=lambda kv: -kv[1])),
            "fat_meta_count": len(fat_summary),
        },
    }


def _access_token() -> str:
    token = json.loads(TOKEN_PATH.read_text())
    if not token.get("refresh_token") or not token.get("client_id"):
        return token.get("token") or ""
    resp = httpx.post(
        TOKEN_URL,
        data={
            "grant_type": "refresh_token",
            "refresh_token": token["refresh_token"],
            "client_id": token["client_id"],
            "client_secret": token.get("client_secret", ""),
        },
        timeout=20.0,
    )
    resp.raise_for_status()
    return resp.json()["access_token"]


def _values(range_name: str, access_token: str) -> list[list[Any]]:
    # values:batchGet = range sebagai query param aman (path /values/{range} rawan 404/encoding)
    resp = httpx.get(
        f"{SHEETS_VALUES_URL}:batchGet",
        params={"ranges": range_name, "valueRenderOption": "UNFORMATTED_VALUE"},
        headers={"Authorization": f"Bearer {access_token}"},
        timeout=30.0,
    )
    resp.raise_for_status()
    ranges = resp.json().get("valueRanges") or []
    return ranges[0].get("values") or [] if ranges else []


def _fetch() -> dict[str, Any]:
    token = _access_token()
    flat_rows, fat_rows = _values(RANGE_FLAT, token), _values(RANGE_FAT, token)
    payload = parse_sheets(flat_rows, fat_rows)
    payload["source"] = {
        "spreadsheet_id": SHEET_ID,
        "url": SHEET_URL,
        "sheets": ["Data Klien (Flat)", "Ringkasan FAT"],
    }
    return payload


def get_data(refresh: bool = False) -> dict[str, Any]:
    global _cache, _fetched_at, _last_good, _last_error
    with _lock:
        if _cache is None or refresh or (time.time() - _fetched_at) > CACHE_TTL_SECONDS:
            try:
                _cache = _fetch()
                _fetched_at = time.time()
                _last_good, _last_error = _cache, None
            except Exception as exc:  # noqa: BLE001 — fallback ke cache terakhir
                _last_error = str(exc)
                if _last_good is None:
                    raise
                _cache = _last_good
        age = int(time.time() - _fetched_at)
        payload = dict(_cache)
    payload["synced_at_epoch"] = int(_fetched_at)
    payload["stale"] = bool(_last_error) or age > CACHE_TTL_SECONDS
    payload["cache_age_seconds"] = age
    if _last_error:
        payload["error"] = _last_error
    return payload


@router.get("")
def list_data_klien(refresh: int = Query(default=0)):
    try:
        return get_data(refresh=bool(refresh))
    except Exception as exc:  # noqa: BLE001
        return {"detail": f"Gagal ambil data klien: {exc}", "items": []}
