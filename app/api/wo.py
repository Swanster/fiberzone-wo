"""API routes — contract frontend spec §4 & §5 (snake_case, error {"detail"})."""

from __future__ import annotations

import difflib
import json
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from app import db, parser

router = APIRouter(prefix="/api/wo", tags=["wo"])

VALID_STATUS = ["masuk", "dikerjakan", "menunggu_verifikasi", "done"]
NEXT_STATUS = {"masuk": "dikerjakan", "dikerjakan": "menunggu_verifikasi",
               "menunggu_verifikasi": "done"}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


class RawIn(BaseModel):
    text: str


class StatusIn(BaseModel):
    status: str


class ReportIn(BaseModel):
    report: dict
    report_raw: str | None = None


@router.get("")
def list_wos(status: str | None = Query(default=None),
             type: str | None = Query(default=None, alias="type"),
             q: str | None = Query(default=None),
             limit: int = Query(default=500, ge=1, le=1000)):
    items, total = db.list_wos(status, type, q, limit)
    return {"items": items, "total": total}


@router.get("/{wo_id}")
def get_wo(wo_id: int):
    wo = db.get_wo(wo_id)
    if not wo:
        raise HTTPException(404, "WO tidak ditemukan")
    return wo


@router.post("/raw")
def raw_wo(payload: RawIn):
    parsed = parser.parse_raw(payload.text or "")
    if not parsed["recognized"]:
        _log_reject(parsed["reason"], None, payload.text)
        return {"recognized": False, "reason": parsed["reason"]}
    if parsed["kind"] == "wo":
        wo = parsed["wo"]
        existing = db.get_wo_by_code(wo["wo_code"])
        if existing:
            applied = db.apply_pending(existing)
            if applied:
                existing = db.get_wo(existing["id"])
            return {"recognized": True, "wo_code": wo["wo_code"], "wo": existing,
                    "created": False, "applied_reports": applied,
                    "reason": "WO sudah ada, data lama dipertahankan"}
        wo.setdefault("status", "masuk")
        wo["created_at"] = _now()
        saved = db.insert_wo(wo)
        applied = db.apply_pending(saved)
        if applied:
            saved = db.get_wo(saved["id"])
        return {"recognized": True, "wo_code": wo["wo_code"], "wo": saved,
                "created": True, "applied_reports": applied}
    # report → cocokkan wo_code → done
    code = parsed["wo_code"]
    report = parsed["report"]
    report.pop("extra", None)
    wo = db.get_wo_by_code(code)
    if not wo:
        # A: tahan di antrian — otomatis ditempel begitu WO-nya masuk
        db.save_pending(code, report, parsed["report_raw"], "WO tidak ditemukan (unmatched)")
        cands = _candidates(code)
        _log_reject("unmatched", code, payload.text)
        return {"recognized": True, "wo_code": code, "matched": False,
                "reason": "WO tidak ditemukan (unmatched)",
                "held": True, "candidates": cands}
    fields = {"report_json": report, "report_raw": parsed["report_raw"]}
    if parser.report_is_open(report):
        # Status laporan Pending/Proses/... → pekerjaan belum tuntas: jangan tutup WO.
        if wo["status"] == "masuk":
            fields.update({"status": "dikerjakan", "started_at": _now()})
        updated = db.update_wo(wo["id"], fields)
        return {"recognized": True, "wo_code": code, "matched": True, "open": True,
                "wo": updated}
    fields.update({"status": "done", "done_at": _now()})
    updated = db.update_wo(wo["id"], fields)
    return {"recognized": True, "wo_code": code, "matched": True, "wo": updated}


def _log_reject(reason: str, wo_code: str | None, text: str) -> None:
    """C: audit penolakan — satu baris JSON di log pm2. Hanya baris PERTAMA teks
    (header) yang dicatat, tidak pernah isi laporan, agar password SSID/ONT tidak masuk log."""
    head = next((ln.strip() for ln in (text or "").splitlines() if ln.strip()), "")[:120]
    print("REJECT " + json.dumps({"ts": _now(), "reason": reason, "wo_code": wo_code,
                                  "head": head}, ensure_ascii=False), flush=True)


def _candidates(wo_code: str, limit: int = 3) -> list[dict]:
    """B: kode mirip saat unmatched (salah tahun/urutan/tipografi) → saran ke pengirim."""
    items, _ = db.list_wos(limit=1000)
    by_code = {w["wo_code"]: w for w in items}
    close = difflib.get_close_matches(wo_code, list(by_code), n=limit, cutoff=0.6)
    return [{"id": by_code[c]["id"], "wo_code": c,
             "customer_name": by_code[c]["customer_name"], "status": by_code[c]["status"]}
            for c in close]


@router.post("/{wo_id}/status")
def transition_status(wo_id: int, payload: StatusIn):
    wo = db.get_wo(wo_id)
    if not wo:
        raise HTTPException(404, "WO tidak ditemukan")
    target = payload.status
    if target not in VALID_STATUS:
        raise HTTPException(422, f"Status tidak dikenal: {target}")
    if target == wo["status"]:
        raise HTTPException(422, f"WO sudah berstatus {target}")
    if NEXT_STATUS.get(wo["status"]) != target:
        raise HTTPException(422, f"Transisi tidak valid: {wo['status']} → {target}")
    if target == "done" and not wo["report"]:
        raise HTTPException(422, "Report wajib diisi sebelum WO diselesaikan")
    stamp = {"dikerjakan": "started_at", "menunggu_verifikasi": "verification_at",
             "done": "done_at"}[target]
    updated = db.update_wo(wo_id, {"status": target, stamp: _now()})
    return updated


@router.put("/{wo_id}/report")
def put_report(wo_id: int, payload: ReportIn):
    wo = db.get_wo(wo_id)
    if not wo:
        raise HTTPException(404, "WO tidak ditemukan")
    report = payload.report
    if not report.get("status_report"):
        raise HTTPException(422, "Status Report wajib diisi")
    fields = {"report_json": report}
    if payload.report_raw is not None:
        fields["report_raw"] = payload.report_raw
    updated = db.update_wo(wo_id, fields)
    return updated


@router.delete("/{wo_id}")
def delete_wo(wo_id: int):
    if not db.delete_wo(wo_id):
        raise HTTPException(404, "WO tidak ditemukan")
    return {"ok": True}
