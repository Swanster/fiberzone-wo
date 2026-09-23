"""Parser tests — PRD §11.1: 6 format, report M/P/T, wo_code, edge cases."""

import pytest

from app.parser import parse_raw, parse_wo_code

WO_M = """WO/260812/M01/FZ/BL0277
SITI SAKDEYA
JL.PULAU GALANG, GG. NILAWARSIKI, NO.10, PEMOGAN, DENPASAR SELATAN, KOTA DENPASAR, BALI
0857 0848 6239

FO CUT
@IYOOO00 @Kyy_YYY
"""

WO_P = """WO/260810/P01/FZ-ABP-2957_01
LILIK KHOLIDA
JL.PULAU GALANG, GG. NILAWARSIKI, NO.154, PEMOGAN, DENPASAR SELATAN, KOTA DENPASAR, BALI
0877 6864 6388

PSB BASIC 50Mbps
TARIK
AKTIVASI

SN ONT: ALCLB4436C21
Username: TBA
Password: TBA

Infra: @IYOOO00 @bgs_dka

Sharelocation: https://www.google.com/maps/place/Denpasar
"""

WO_T = """WO/260803/T01/V-DPS-FDT21-FAT3
V-DPS-FDT21-FAT3
JL. NAKULA, GG. JATAYU

Pengecekan FAT V-DPS-FDT21-FAT3

@yohanesharlan PKL
"""

WO_D = """WO/260812/D01/FZ/BL0288
BUDI SANTOSO
JL. MERPATI NO. 5, DENPASAR
0812 3456 7890

Dismantle ONT
@teknisi1
"""

WO_B = """WO/260812/B01/FZ-BGN-009
TIM KONSTRUKSI
JL. GATOT SUBROTO, DENPASAR

Bangun jaringan baru segmen DPS-12
@koorlap
"""

WO_S = """WO/260812/S01/FZ-SRV-003
CALON PELANGGAN
JL. FLAMBOYAN, DENPASAR

Survey lokasi penarikan kabel
@surveyor
"""

REPORT_M = """Report Maintenance

WO/260811/M01/FZ-ABQ-2212_01
RUDOLF KASENDA OKI
JL. SUBAK SARI, TIBUBENENG, KEC. KUTA UTARA, BADUNG, BALI
0813 1539 7698

Case :
- Core di box panel putus
- IP mental

Action :
- Sambung ulang core di box panel
- koordinasi dengan NE
- Test Speed

Status : Cleared
"""

REPORT_P = """Repot pasang baru

WO/260810/P01/FZ-ABP-2957_01
LILIK KHOLIDA
JL.PULAU GALANG, GG. NILAWARSIKI, NO.154, PEMOGAN, DENPASAR
0877 6864 6388

PSB BASIC 50Mbps

Detail laporan:
HARI / TANGGAL : 11 Agustus 2026
Pic teknisi : rifky dan iyo
Start  :
Finish :

PIC yang mendampingi : ybs

Solution
Tarik kabel FO 1 Core dari Splitter terdekat Mengarah ke client sepanjang meter
- Splicing kabel sisi FAT dan Client

SOLITER / FADPS-FDT10-FAT0
31] DPS-FDT10-FAT03
- port 3  1:4

Alat Yang Terpasang :
- Patchcore Biru 1 Pcs
- Pigtail Hijau 1 pcs
- ONT Nokia 1 Pcs
- Kabel ties secukupnya
- Klem kabel secukupnya

Said : Likkho
Pas : Fifiye2170

SN ONT: ALCLB4436C21
Username: TBA
Password: TBA
"""

REPORT_T = """Report troubleshoot

WO/260803/T01/V-DPS-FDT21-FAT3
V-DPS-FDT21-FAT3
JL. NAKULA, GG. JATAYU

Segmen : V-DPS-FDT21-FAT3
Description : Pengecekan FAT

Case :
- Terdapat red alarm di FAT

Action :
- Pengecekan port
- Splicing ulang

Solution :
- Normal kembali

Status: Cleared
"""


def test_wo_code_parse():
    c = parse_wo_code("WO/260812/M01/FZ/BL0277")
    assert c == {"wo_date": "2026-08-12", "wo_type": "M", "wo_seq": 1, "identitas": "FZ/BL0277"}


def test_wo_code_identitas_multipart():
    c = parse_wo_code("WO/260810/P01/FZ-ABP-2957_01")
    assert c["identitas"] == "FZ-ABP-2957_01"


@pytest.mark.parametrize("bad", ["WO/26/812/M01/X", "WO/999999/Z01/X", "NOT-A-WO", ""])
def test_wo_code_invalid(bad):
    assert parse_wo_code(bad) is None


def test_wo_maintenance():
    r = parse_raw(WO_M)
    assert r["recognized"] and r["kind"] == "wo"
    w = r["wo"]
    assert w["wo_code"] == "WO/260812/M01/FZ/BL0277"
    assert w["wo_type"] == "M" and w["customer_name"] == "SITI SAKDEYA"
    assert w["phone"] == "0857 0848 6239"
    assert w["action"] == "FO CUT"
    assert w["assignees"] == ["@IYOOO00", "@Kyy_YYY"]


def test_wo_psb():
    r = parse_raw(WO_P)
    w = r["wo"]
    assert w["wo_type"] == "P"
    assert w["package"] == "PSB BASIC 50Mbps"
    assert w["flags"] == ["TARIK", "AKTIVASI"]
    assert w["sn_ont"] == "ALCLB4436C21"
    assert w["username"] == "TBA" and w["password"] == "TBA"
    assert w["infra"] == ["@IYOOO00", "@bgs_dka"]
    assert w["sharelocation"] == "https://www.google.com/maps/place/Denpasar"


def test_wo_troubleshoot():
    r = parse_raw(WO_T)
    w = r["wo"]
    assert w["wo_type"] == "T"
    assert w["segment"] == "V-DPS-FDT21-FAT3"
    assert w["description"] == "Pengecekan FAT V-DPS-FDT21-FAT3"
    assert w["assignees"] == ["@yohanesharlan"]


def test_wo_dismantle_bangun_survey():
    for text, t in ((WO_D, "D"), (WO_B, "B"), (WO_S, "S")):
        r = parse_raw(text)
        assert r["recognized"], t
        assert r["wo"]["wo_type"] == t
        assert r["wo"]["description"]


def test_report_maintenance():
    r = parse_raw(REPORT_M)
    assert r["recognized"] and r["kind"] == "report"
    assert r["wo_code"] == "WO/260811/M01/FZ-ABQ-2212_01"
    rep = r["report"]
    assert rep["case"] == ["Core di box panel putus", "IP mental"]
    assert rep["action"] == ["Sambung ulang core di box panel", "koordinasi dengan NE", "Test Speed"]
    assert rep["status_report"] == "Cleared"
    assert r["report_raw"] == REPORT_M


def test_report_psb_tolerant():
    r = parse_raw(REPORT_P)
    assert r["recognized"] and r["wo_code"] == "WO/260810/P01/FZ-ABP-2957_01"
    rep = r["report"]
    assert rep["report_date"] == "11 Agustus 2026"
    assert rep["pic_teknisi"] == "rifky dan iyo"
    assert rep["pic_pendamping"] == "ybs"
    assert rep["solution"] == ["Tarik kabel FO 1 Core dari Splitter terdekat Mengarah ke client sepanjang meter",
                               "Splicing kabel sisi FAT dan Client"]
    assert "SOLITER / FADPS-FDT10-FAT0" in rep["splitter"]
    assert "31] DPS-FDT10-FAT03" in rep["splitter"]
    assert rep["alat_terpasang"] == ["Patchcore Biru 1 Pcs", "Pigtail Hijau 1 pcs",
                                     "ONT Nokia 1 Pcs", "Kabel ties secukupnya", "Klem kabel secukupnya"]
    assert rep["splicer"] == "Said : Likkho\nPas : Fifiye2170"
    assert rep["sn_ont"] == "ALCLB4436C21"
    assert rep["username"] == "TBA" and rep["password"] == "TBA"


def test_report_troubleshoot():
    r = parse_raw(REPORT_T)
    assert r["recognized"]
    assert r["report"]["status_report"] == "Cleared"
    assert r["report"]["segmen"] == "V-DPS-FDT21-FAT3"
    assert r["report"]["description"] == "Pengecekan FAT"
    assert r["report"]["case"] == ["Terdapat red alarm di FAT"]
    assert r["report"]["action"] == ["Pengecekan port", "Splicing ulang"]
    assert r["report"]["solution"] == ["Normal kembali"]


def test_report_invisible_chars_stripped():
    text = "Report Maintenance\n\nWO/260811/M01/FZ-ABQ-2212_01\n\nStatus : Cleared\nPIC yang mendampingi : ybs"
    text = text.replace("mendampingi", "mendamping\u200ei")
    r = parse_raw(text)
    assert r["report"]["pic_pendamping"] == "ybs"


def test_empty_and_garbage():
    assert parse_raw("")["recognized"] is False
    assert parse_raw("   \n\n  ")["recognized"] is False
    r = parse_raw("lorem ipsum dolor")
    assert r["recognized"] is False and r["reason"]


def test_report_status_typo_staatus():
    """Typo lapangan 'Staatus : Cleared' harus tetap terbaca sebagai status_report."""
    text = """Report Pasang Baru

WO/260921/P01/FZ-ABP-3076_01
SUWANTO
JL. TUKAD BARU, PEMOGAN, DENPASAR
0813 5330 6867

Detail laporan :
Hari / Tanggal : 21 September 2026
PIC Teknisi : Rhei, Risky
Start   :
Finish :
Total Tarikan : 10 Meter
TARIK: OK
AKTIVASI : OK

Staatus : Cleared
"""
    d = parse_raw(text)
    assert d["recognized"] and d["kind"] == "report"
    assert d["report"]["status_report"] == "Cleared"
    assert d["report"]["report_date"] == "21 September 2026"
    assert d["report"]["start"] is None
