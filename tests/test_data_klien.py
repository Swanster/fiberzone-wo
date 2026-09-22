"""Test parsing Data Klien (tanpa jaringan)."""

from app.api.data_klien import parse_sheets

FLAT = [
    ["No", "POP", "FDT", "FAT", "Port", "Client ID", "Nama Klien",
     "Tipe", "Status", "Sumber", "Via Splitter"],
    ["1", "Canggu", "", "ODP VARNION", "1", "", "Varnion",
     "CLIENT_NOID", "ACTIVE", "FAT", ""],
    ["2", "Imam Bonjol", "V-DPS-FDT16", "V-DPS-FDT16-FAT01", "5", "FZBL-0342",
     "ATIM SRIANAH", "CLIENT", "ACTIVE", "SPLITER", "SPLITER [42] 1:8"],
    ["3", "Imam Bonjol", "V-DPS-FDT16", "V-DPS-FDT16-FAT01", "6", "FZBL-0999",
     "CEK DISCONNECT", "CLIENT", "DISCONNECT", "SPLITER", ""],
    ["4", "", "", "", "", "", "", "", "", "", ""],  # baris kosong → dilewati
]

FAT = [
    ["No", "POP", "FDT", "FAT", "Total Port", "Port Terisi", "Klien Aktif",
     "Klien Disconnect", "Total Klien", "Power In (dBm)", "Power Out (dBm)",
     "Koordinat"],
    ["1", "Imam Bonjol", "V-DPS-FDT16", "V-DPS-FDT16-FAT01", "8", "7", "1",
     "1", "2", "-7.10", "-18.10", "-8.6585,115.1813"],
]


def test_parse_counts():
    payload = parse_sheets(FLAT, FAT)
    assert payload["summary"] == {
        "total": 3, "aktif": 2, "disconnect": 1,
        "fdt_count": 1, "fat_count": 2, "tanpa_fdt": 1,
        "by_pop": {"Imam Bonjol": 2, "Canggu": 1},
        "by_tipe": {"CLIENT": 2, "CLIENT_NOID": 1},
        "fat_meta_count": 1,
    }


def test_parse_item_fields():
    item = parse_sheets(FLAT, FAT)["items"][1]
    assert item["client_id"] == "FZBL-0342"
    assert item["fdt"] == "V-DPS-FDT16"
    assert item["fat"] == "V-DPS-FDT16-FAT01"
    assert item["via_splitter"] == "SPLITER [42] 1:8"


def test_parse_fat_summary():
    fat = parse_sheets(FLAT, FAT)["fat_summary"][0]
    assert fat["total_port"] == 8 and fat["port_terisi"] == 7
    assert fat["power_in"] == "-7.10"
    assert fat["koordinat"] == "-8.6585,115.1813"


def test_empty_sheet_raises():
    try:
        parse_sheets([], [])
    except ValueError:
        return
    raise AssertionError("sheet kosong harus raise ValueError")
