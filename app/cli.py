"""CLI untuk Jack — add/move/list/report (PRD §9.4)."""

from __future__ import annotations

import argparse
import sys
from datetime import datetime, timezone

from app import db, parser


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def cmd_add(text: str | None, path: str | None) -> int:
    if path:
        with open(path, encoding="utf-8") as f:
            text = f.read()
    if not text:
        text = sys.stdin.read()
    parsed = parser.parse_raw(text)
    if not parsed["recognized"]:
        print(f"Tidak dikenali: {parsed['reason']}", file=sys.stderr)
        return 1
    if parsed["kind"] == "wo":
        wo = parsed["wo"]
        existing = db.get_wo_by_code(wo["wo_code"])
        if existing:
            print(f"WO {wo['wo_code']} sudah ada (id={existing['id']}), data lama dipertahankan")
            return 0
        wo.setdefault("status", "masuk")
        wo["created_at"] = _now()
        saved = db.insert_wo(wo)
        print(f"WO ditambahkan: {saved['wo_code']} ({parser.TYPE_LABEL.get(saved['wo_type'], saved['wo_type'])}) "
              f"→ status: masuk | dashboard: http://127.0.0.1:8600/")
        return 0
    # report → cocokkan kode → done
    wo = db.get_wo_by_code(parsed["wo_code"])
    if not wo:
        print(f"Report tidak dapat dicocokkan: WO {parsed['wo_code']} tidak ditemukan (unmatched)",
              file=sys.stderr)
        return 2
    report = parsed["report"]
    report.pop("extra", None)
    db.update_wo(wo["id"], {"report_json": report, "report_raw": parsed["report_raw"],
                            "status": "done", "done_at": _now()})
    print(f"Report dicocokkan: {parsed['wo_code']} → done")
    return 0


def cmd_move(wo_code: str, status: str) -> int:
    wo = db.get_wo_by_code(wo_code)
    if not wo:
        print(f"WO {wo_code} tidak ditemukan", file=sys.stderr)
        return 1
    stamp = {"dikerjakan": "started_at", "menunggu_verifikasi": "verification_at",
             "done": "done_at"}.get(status)
    if stamp is None:
        print(f"Status tidak dikenal: {status}", file=sys.stderr)
        return 1
    if status == wo["status"]:
        print(f"WO sudah berstatus {status}", file=sys.stderr)
        return 1
    nexts = {"masuk": "dikerjakan", "dikerjakan": "menunggu_verifikasi",
             "menunggu_verifikasi": "done"}
    if nexts.get(wo["status"]) != status:
        print(f"Transisi tidak valid: {wo['status']} → {status}", file=sys.stderr)
        return 1
    if status == "done" and not wo["report"]:
        print("Report wajib diisi sebelum WO diselesaikan", file=sys.stderr)
        return 1
    db.update_wo(wo["id"], {"status": status, stamp: _now()})
    print(f"WO {wo_code} → {status}")
    return 0


def cmd_list(status: str | None, wo_type: str | None) -> int:
    items, total = db.list_wos(status, wo_type, limit=1000)
    print(f"Total: {total} WO")
    for wo in items:
        label = parser.TYPE_LABEL.get(wo["wo_type"], wo["wo_type"])
        print(f"[{wo['id']:>4}] {wo['wo_code']}  {label:<12} {wo['status']:<18} "
              f"{wo['customer_name'] or ''}")
    return 0


def cmd_report(wo_code: str) -> int:
    wo = db.get_wo_by_code(wo_code)
    if not wo:
        print(f"WO {wo_code} tidak ditemukan", file=sys.stderr)
        return 1
    print(f"=== {wo['wo_code']} — {wo['customer_name'] or ''} ({wo['status']}) ===")
    if wo["report"]:
        for k, v in wo["report"].items():
            print(f"{k}: {v}")
    print("--- report_raw ---")
    print(wo["report_raw"] or "(tidak ada)")
    return 0


def main() -> int:
    db.init_db()
    p = argparse.ArgumentParser(prog="python -m app.cli", description="Fiberzone WO CLI")
    sub = p.add_subparsers(dest="cmd", required=True)

    pa = sub.add_parser("add", help="Tambah WO/report dari file atau stdin")
    pa.add_argument("path", nargs="?", help="file teks (default: stdin)")
    pa.set_defaults(fn=cmd_add)

    pm = sub.add_parser("move", help="Pindah status WO")
    pm.add_argument("wo_code")
    pm.add_argument("status", choices=["masuk", "dikerjakan", "menunggu_verifikasi", "done"])
    pm.set_defaults(fn=cmd_move)

    pl = sub.add_parser("list", help="Daftar WO")
    pl.add_argument("--status", choices=["masuk", "dikerjakan", "menunggu_verifikasi", "done"])
    pl.add_argument("--type")
    pl.set_defaults(fn=cmd_list)

    pr = sub.add_parser("report", help="Cetak report WO")
    pr.add_argument("wo_code")
    pr.set_defaults(fn=cmd_report)

    args = p.parse_args()
    fn = args.fn
    if fn is cmd_add:
        return fn(None, args.path)
    if fn is cmd_move:
        return fn(args.wo_code, args.status)
    if fn is cmd_list:
        return fn(args.status, args.type)
    return fn(args.wo_code)


if __name__ == "__main__":
    sys.exit(main())
