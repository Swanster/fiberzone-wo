"""SQLite storage untuk Fiberzone Work Order.

Schema mengikuti PRD §9.5. Setiap akses membuka koneksi baru (sqlite3 stdlib,
check_same_thread=False agar aman dipakai dari thread FastAPI).
Path DB bisa dioverride lewat env FZWO_DB (dipakai juga oleh tests/CI).
"""

from __future__ import annotations

import json
import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

DEFAULT_DB = Path(__file__).resolve().parent.parent / "data" / "wo.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS work_orders (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  wo_code TEXT NOT NULL UNIQUE,
  wo_date TEXT,
  wo_type TEXT NOT NULL,
  wo_seq INTEGER,
  identitas TEXT,
  customer_name TEXT,
  address TEXT,
  phone TEXT,
  package TEXT,
  action TEXT,
  description TEXT,
  segment TEXT,
  sn_ont TEXT,
  username TEXT,
  password TEXT,
  sharelocation TEXT,
  assignees TEXT,
  infra TEXT,
  flags TEXT,
  status TEXT NOT NULL DEFAULT 'masuk',
  report_json TEXT,
  report_raw TEXT,
  raw_text TEXT,
  created_at TEXT,
  started_at TEXT,
  verification_at TEXT,
  done_at TEXT
);

CREATE TABLE IF NOT EXISTS pending_reports (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  wo_code TEXT NOT NULL,
  report_json TEXT NOT NULL,
  report_raw TEXT,
  reason TEXT,
  created_at TEXT
);
"""

SCALAR_COLS = [
    "id", "wo_code", "wo_date", "wo_type", "wo_seq", "identitas",
    "customer_name", "address", "phone", "package", "action", "description",
    "segment", "sn_ont", "username", "password", "sharelocation", "status",
    "report_json", "report_raw", "raw_text", "created_at", "started_at",
    "verification_at", "done_at",
]
JSON_COLS = {"assignees", "infra", "flags"}
ALL_COLS = SCALAR_COLS + list(JSON_COLS)


def db_path() -> Path:
    return Path(os.environ.get("FZWO_DB", DEFAULT_DB))


def get_conn() -> sqlite3.Connection:
    path = db_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def init_db() -> None:
    with get_conn() as conn:
        conn.executescript(SCHEMA)


def row_to_dict(row: sqlite3.Row) -> dict:
    d = dict(row)
    for col in JSON_COLS:
        d[col] = json.loads(d[col]) if d.get(col) else []
    d["report"] = json.loads(d["report_json"]) if d.get("report_json") else None
    d.pop("report_json", None)
    return d


def insert_wo(wo: dict) -> dict:
    """Insert WO baru. Kolom selain daftar dikenal diabaikan."""
    cols = [c for c in ALL_COLS if c in wo]
    values = []
    for c in cols:
        v = wo[c]
        if c == "report_json" and v is not None:
            v = json.dumps(v, ensure_ascii=False)
        elif c in JSON_COLS:
            v = json.dumps(v or [], ensure_ascii=False)
        values.append(v)
    placeholders = ", ".join("?" for _ in cols)
    sql = f"INSERT INTO work_orders ({', '.join(cols)}) VALUES ({placeholders})"
    with get_conn() as conn:
        cur = conn.execute(sql, values)
        conn.commit()
        wo["id"] = cur.lastrowid
    return wo


def get_wo(wo_id: int) -> dict | None:
    with get_conn() as conn:
        row = conn.execute("SELECT * FROM work_orders WHERE id = ?", (wo_id,)).fetchone()
    return row_to_dict(row) if row else None


def get_wo_by_code(wo_code: str) -> dict | None:
    with get_conn() as conn:
        row = conn.execute(
            "SELECT * FROM work_orders WHERE wo_code = ?", (wo_code,)
        ).fetchone()
    return row_to_dict(row) if row else None


def update_wo(wo_id: int, fields: dict) -> dict | None:
    """Update kolom tertentu; JSON columns di-serialize otomatis."""
    updates = []
    values = []
    for c, v in fields.items():
        if c not in ALL_COLS:
            continue
        if c == "report_json" and v is not None:
            v = json.dumps(v, ensure_ascii=False)
        elif c in JSON_COLS:
            v = json.dumps(v or [], ensure_ascii=False)
        updates.append(f"{c} = ?")
        values.append(v)
    if not updates:
        return get_wo(wo_id)
    values.append(wo_id)
    with get_conn() as conn:
        conn.execute(f"UPDATE work_orders SET {', '.join(updates)} WHERE id = ?", values)
        conn.commit()
    return get_wo(wo_id)


def list_wos(status: str | None = None, wo_type: str | None = None,
             q: str | None = None, limit: int = 500) -> tuple[list[dict], int]:
    """List + filter + search. Order: created_at DESC, id DESC."""
    where, params = [], []
    if status:
        where.append("status = ?")
        params.append(status)
    if wo_type:
        where.append("wo_type = ?")
        params.append(wo_type.upper())
    if q:
        like = f"%{q}%"
        where.append("(wo_code LIKE ? OR customer_name LIKE ? OR address LIKE ? OR phone LIKE ?)")
        params.extend([like, like, like, like])
    sql_where = f"WHERE {' AND '.join(where)}" if where else ""
    with get_conn() as conn:
        total = conn.execute(
            f"SELECT COUNT(*) FROM work_orders {sql_where}", params
        ).fetchone()[0]
        rows = conn.execute(
            f"SELECT * FROM work_orders {sql_where} ORDER BY created_at DESC, id DESC LIMIT ?",
            params + [max(1, min(limit, 1000))],
        ).fetchall()
    return [row_to_dict(r) for r in rows], total


def delete_wo(wo_id: int) -> bool:
    with get_conn() as conn:
        cur = conn.execute("DELETE FROM work_orders WHERE id = ?", (wo_id,))
        conn.commit()
    return cur.rowcount > 0


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def save_pending(wo_code: str, report: dict, report_raw: str | None, reason: str) -> int:
    """Antrian hold: report yang belum bisa dicocokkan. Idempotent per kode+teks."""
    with get_conn() as conn:
        conn.execute("DELETE FROM pending_reports WHERE wo_code = ? AND report_raw IS ?",
                     (wo_code, report_raw))
        cur = conn.execute(
            "INSERT INTO pending_reports (wo_code, report_json, report_raw, reason, created_at)"
            " VALUES (?, ?, ?, ?, ?)",
            (wo_code, json.dumps(report, ensure_ascii=False), report_raw, reason, _now_iso()))
        conn.commit()
        return cur.lastrowid


def list_pending() -> list[dict]:
    with get_conn() as conn:
        rows = conn.execute("SELECT * FROM pending_reports ORDER BY id").fetchall()
    return [{"id": r["id"], "wo_code": r["wo_code"],
             "report": json.loads(r["report_json"]), "report_raw": r["report_raw"],
             "reason": r["reason"], "created_at": r["created_at"]} for r in rows]


def apply_pending(wo: dict) -> int:
    """Tempel semua laporan tertahan untuk kode WO ini (urut id → terakhir menang).

    Laporan berstatus terbuka (Pending/Proses/...) ditempel tanpa menutup WO.
    """
    from app import parser

    with get_conn() as conn:
        rows = conn.execute("SELECT * FROM pending_reports WHERE wo_code = ? ORDER BY id",
                            (wo["wo_code"],)).fetchall()
    for r in rows:
        report = json.loads(r["report_json"])
        fields = {"report_json": report, "report_raw": r["report_raw"]}
        if parser.report_is_open(report):
            fields["status"] = "dikerjakan" if wo["status"] in ("masuk", "done") else wo["status"]
        else:
            fields.update({"status": "done", "done_at": _now_iso()})
        update_wo(wo["id"], fields)
        with get_conn() as conn:
            conn.execute("DELETE FROM pending_reports WHERE id = ?", (r["id"],))
            conn.commit()
    return len(rows)
