"""API tests — PRD §11.2 + contract spec §4/§5 (TestClient, DB temp per-sesi)."""

import os

import pytest

os.environ["FZWO_DB"] = "/tmp/fzwo_test.db"
if os.path.exists("/tmp/fzwo_test.db"):
    os.remove("/tmp/fzwo_test.db")

from fastapi.testclient import TestClient  # noqa: E402

from app import db  # noqa: E402
from app.main import app  # noqa: E402

db.init_db()
client = TestClient(app)

WO_M = """WO/260812/M01/FZ/BL0277
SITI SAKDEYA
JL.PULAU GALANG, GG. NILAWARSIKI, NO.10, PEMOGAN, DENPASAR SELATAN, KOTA DENPASAR, BALI
0857 0848 6239

FO CUT
@IYOOO00 @Kyy_YYY
"""

REPORT_P = """Repot pasang baru

WO/260812/P02/FZ-ABP-2957_01
LILIK KHOLIDA
JL.PULAU GALANG, GG. NILAWARSIKI, NO.154, PEMOGAN, DENPASAR
0877 6864 6388

PSB BASIC 50Mbps

Detail laporan:
HARI / TANGGAL : 11 Agustus 2026
Pic teknisi : rifky dan iyo
PIC yang mendampingi : ybs

Solution
- Splicing kabel sisi FAT dan Client

SOLITER / FADPS-FDT10-FAT0
31] DPS-FDT10-FAT03

Alat Yang Terpasang :
- Patchcore Biru 1 Pcs

Said : Likkho
Pas : Fifiye2170

SN ONT: ALCLB4436C21
Username: TBA
Password: TBA

Status : Cleared
"""


@pytest.fixture(autouse=True)
def clean_db():
    from app import db

    yield
    # biarkan data antar-test mengalir sesuai urutan; tiap test pakai kode WO unik


def test_health():
    r = client.get("/api/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


_seq = [0]


def add_wo(code: str | None = None) -> dict:
    """Insert WO maintenance via /raw dengan kode unik, return WO."""
    _seq[0] += 1
    c = code or f"WO/260812/M{_seq[0]:02d}/FZ/BL0{_seq[0]:03d}"
    text = WO_M.replace("WO/260812/M01/FZ/BL0277", c)
    return client.post("/api/wo/raw", json={"text": text}).json()["wo"]


def test_raw_wo_insert():
    r = client.post("/api/wo/raw", json={"text": WO_M})
    assert r.status_code == 200
    body = r.json()
    assert body["recognized"] and body["created"] is True
    assert body["wo"]["status"] == "masuk"
    assert body["wo"]["assignees"] == ["@IYOOO00", "@Kyy_YYY"]


def test_raw_wo_duplicate_keeps_existing():
    client.post("/api/wo/raw", json={"text": WO_M})
    r = client.post("/api/wo/raw", json={"text": WO_M})
    body = r.json()
    assert body["recognized"] and body["created"] is False
    assert body["wo"]["id"] is not None


def test_raw_report_matched_done():
    wo = add_wo()
    r = client.post("/api/wo/raw",
                    json={"text": REPORT_P.replace("WO/260812/P02/FZ-ABP-2957_01", wo["wo_code"])})
    assert r.status_code == 200
    body = r.json()
    assert body["matched"] is True
    assert body["wo"]["status"] == "done"
    assert body["wo"]["done_at"] is not None
    rep = body["wo"]["report"]
    assert rep["pic_teknisi"] == "rifky dan iyo"
    assert rep["alat_terpasang"] == ["Patchcore Biru 1 Pcs"]
    assert "SOLITER / FADPS-FDT10-FAT0" in rep["splitter"]
    assert body["wo"]["report_raw"].startswith("Repot pasang baru")


def test_raw_report_unmatched():
    r = client.post("/api/wo/raw", json={"text": REPORT_P})
    body = r.json()
    assert body["recognized"] and body["matched"] is False
    assert body["reason"]


def test_transition_valid_and_timestamps():
    wo = add_wo()
    wid = wo["id"]
    r = client.post(f"/api/wo/{wid}/status", json={"status": "dikerjakan"})
    assert r.status_code == 200
    assert r.json()["started_at"] is not None
    r = client.post(f"/api/wo/{wid}/status", json={"status": "menunggu_verifikasi"})
    assert r.json()["verification_at"] is not None


def test_transition_done_requires_report():
    wo = add_wo()
    client.post(f"/api/wo/{wo['id']}/status", json={"status": "dikerjakan"})
    client.post(f"/api/wo/{wo['id']}/status", json={"status": "menunggu_verifikasi"})
    r = client.post(f"/api/wo/{wo['id']}/status", json={"status": "done"})
    assert r.status_code == 422
    assert "Report" in r.json()["detail"]


def test_transition_invalid_jump_422():
    wo = add_wo()
    r = client.post(f"/api/wo/{wo['id']}/status", json={"status": "done"})
    assert r.status_code == 422
    r = client.post(f"/api/wo/{wo['id']}/status", json={"status": "nonsense"})
    assert r.status_code == 422


def test_put_report_contract():
    wo = add_wo()
    payload = {"report": {"status_report": "Cleared", "case": ["A"], "action": ["B"],
                          "solution": ["C"], "pic_teknisi": "x", "pic_pendamping": "y",
                          "report_date": "2026-08-12", "start": "08:00", "finish": "11:00",
                          "tarik": "ok", "aktivasi": "ok", "meteran": "Tarikan awal - meter",
                          "splitter": "FADPS-FDT10-FAT0", "alat_terpasang": ["Patchcore"],
                          "splicer": "Said : Likkho", "sn_ont": "SN1", "username": "u",
                          "password": "p"},
               "report_raw": "Report Maintenance\n\nWO/260812/M01/FZ/BL0277\nraw"}
    r = client.put(f"/api/wo/{wo['id']}/report", json=payload)
    assert r.status_code == 200
    rep = r.json()["report"]
    assert rep["status_report"] == "Cleared"
    assert rep["alat_terpasang"] == ["Patchcore"]
    assert r.json()["report_raw"] == payload["report_raw"]
    # status tidak berubah
    assert r.json()["status"] == "masuk"


def test_put_report_requires_status():
    wo = add_wo()
    r = client.put(f"/api/wo/{wo['id']}/report", json={"report": {"case": []}})
    assert r.status_code == 422


def test_put_report_404():
    r = client.put("/api/wo/999999/report", json={"report": {"status_report": "Cleared"}})
    assert r.status_code == 404


def test_list_filter_search():
    client.post("/api/wo/raw", json={"text": WO_M})
    # transisi ke dikerjakan supaya ada 2 status
    r = client.get("/api/wo")
    assert r.status_code == 200
    body = r.json()
    assert body["total"] >= 1 and isinstance(body["items"], list)
    r = client.get("/api/wo", params={"type": "M"})
    assert all(w["wo_type"] == "M" for w in r.json()["items"])
    r = client.get("/api/wo", params={"q": "SAKDEYA"})
    assert any("SAKDEYA" in w["customer_name"] for w in r.json()["items"])
    r = client.get("/api/wo", params={"q": "0857 0848"})
    assert r.json()["total"] >= 1


def test_get_detail_and_delete():
    wo = add_wo()
    r = client.get(f"/api/wo/{wo['id']}")
    assert r.status_code == 200 and r.json()["wo_code"] == wo["wo_code"]
    r = client.delete(f"/api/wo/{wo['id']}")
    assert r.json()["ok"] is True
    assert client.get(f"/api/wo/{wo['id']}").status_code == 404


def test_raw_garbage_no_crash():
    r = client.post("/api/wo/raw", json={"text": "asdf qwer zxcv"})
    assert r.status_code == 200
    assert r.json()["recognized"] is False


def test_root_serves_dashboard():
    r = client.get("/")
    assert r.status_code == 200
    assert "Fiberzone WO Dashboard" in r.text
    assert client.get("/style.css").status_code == 200
    assert client.get("/app.js").status_code == 200


def test_performance_100_plus_wos():
    """T-036: 120 insert via /raw + list + search dalam batas wajar."""
    import time
    t0 = time.monotonic()
    for i in range(120):
        r = client.post("/api/wo/raw", json={"text": f"WO/260813/P{i:02d}/FZ-ABP-{4000 + i}_0{i % 10}\nCUST {i}\nJL. TEST NO. {i}\n0812 0000 {i:04d}\n\nPSB BASIC 30Mbps\nTARIK\n\n@teknisi{i}"})
        assert r.status_code == 200 and r.json()["created"] is True, i
    insert_el = time.monotonic() - t0
    t0 = time.monotonic()
    r = client.get("/api/wo?limit=500")
    body = r.json()
    list_el = time.monotonic() - t0
    assert body["total"] >= 120
    assert len(body["items"]) >= 120
    r = client.get("/api/wo?q=FZ-ABP-4017")
    assert r.json()["total"] == 1
    assert insert_el < 30 and list_el < 5, (insert_el, list_el)
