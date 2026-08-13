"""API routes — contract frontend spec §4 & §5 (snake_case, error {"detail"})."""

from __future__ import annotations

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
        return {"recognized": False, "reason": parsed["reason"]}
    if parsed["kind"] == "wo":
        wo = parsed["wo"]
        existing = db.get_wo_by_code(wo["wo_code"])
        if existing:
            return {"recognized": True, "wo_code": wo["wo_code"], "wo": existing,
                    "created": False, "reason": "WO sudah ada, data lama dipertahankan"}
        wo.setdefault("status", "masuk")
        wo["created_at"] = _now()
        saved = db.insert_wo(wo)
        return {"recognized": True, "wo_code": wo["wo_code"], "wo": saved, "created": True}
    # report → cocokkan wo_code → done
    code = parsed["wo_code"]
    wo = db.get_wo_by_code(code)
    if not wo:
        return {"recognized": True, "wo_code": code, "matched": False,
                "reason": "WO tidak ditemukan (unmatched)"}
    report = parsed["report"]
    report.pop("extra", None)
    fields = {"report_json": report, "report_raw": parsed["report_raw"],
              "status": "done", "done_at": _now()}
    updated = db.update_wo(wo["id"], fields)
    return {"recognized": True, "wo_code": code, "matched": True, "wo": updated}


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
