# PRD — Fiberzone Work Order Dashboard

| | |
|---|---|
| **Project** | fiberzone-wo |
| **Versi** | 1.0 (Draft) |
| **Tanggal** | 2026-08-12 |
| **Status** | Menunggu review user |
| **Channel** | Discord #fiberzone-wo |
| **Workdir** | `/home/swanster/project6661/fiberzone-wo` |

---

## 1. Ringkasan Produk

Dashboard web untuk mengelola **Work Order (WO) tim Broadband Fiberzone**. WO masuk lewat chat group dengan format pesan tertentu; user mem-forward pesan tersebut ke Jack (Hermes) di channel Discord, Jack mem-parse dan menyimpannya ke database. Dashboard menampilkan WO berdasarkan status:

**Masuk → Dikerjakan → Menunggu Verifikasi → Done**

Ketika report penyelesaian WO di-forward, WO otomatis berpindah ke tab **Done** beserta detail report-nya.

## 2. Latar Belakang & Masalah

- Tim Fiberzone menerima WO (Pasang Baru, Maintenance, Troubleshoot, dll) melalui chat group dengan format pesan yang sudah mapan.
- Saat ini tidak ada tampilan terpusat: WO tersebar di chat, tidak ada cara melihat antrian, status pengerjaan, atau riwayat selesai dalam satu layar.
- Laporan selesai juga datang sebagai pesan chat terpisah dan tidak terhubung dengan WO asalnya.

## 3. Tujuan & Kriteria Sukses

1. Setiap WO yang di-forward dapat masuk ke dashboard secara otomatis (parse → simpan) tanpa ketik ulang manual.
2. Status WO terlihat jelas dalam 4 tab: Masuk, Dikerjakan, Menunggu Verifikasi, Done.
3. Report selesai yang di-forward otomatis mencocokkan No. WO yang sama dan memindahkannya ke tab Done beserta detail report.
4. Dashboard bisa dicari & difilter (tipe WO: P/M/D/B/T/S, kata kunci: No. WO/nama/alamat/telepon).
5. Statistik ringkas (jumlah per status, per tipe) terlihat di halaman utama.

## 4. Pengguna & Peran

| Peran | Kebutuhan |
|---|---|
| **Swans / Jack (Hermes)** | Menambah WO dari forward chat via CLI/API; memindahkan status atas permintaan chat |
| **Tim Fiberzone (via dashboard)** | Melihat antrian WO, memindahkan status via tombol, melihat report WO selesai |

v1 tanpa login/auth (aplikasi lokal). Multi-user & role dianggap future work.

## 5. Alur Kerja

```
[Chat group] ──forward──▶ [Discord #fiberzone-wo] ──parse──▶ Jack
                                                               │
                          ┌────────────────────────────────────┤
                          ▼                                    ▼
              WO baru (format WO/...)             Report selesai (format "Report/Repot ...")
              → status: masuk                     → cocokkan No. WO → status: done + simpan report
                          │
                          ▼
              Dashboard (browser lokal)
              Masuk → Dikerjakan → Menunggu Verifikasi → Done
              (pindah status via tombol di kartu WO)
```

## 6. Format WO Masuk (dari chat)

### 6.1 Kode WO

```
WO/YYMMDD/<TYPE><SEQ>/<IDENTITAS>
```

| Bagian | Keterangan | Contoh |
|---|---|---|
| `YYMMDD` | Tahun-bulan-tanggal (2 digit) | `260812` = 12 Agu 2026 |
| `TYPE` | P=PSB, M=Maintenance, T=Troubleshoot, D=Dismantle, B=Bangun Jaringan, S=Survey | `M` |
| `SEQ` | Nomor urut WO pada tanggal itu (01, 02, ...) | `01` |
| `IDENTITAS` | Nama klient / segmen / kode area (bisa 1-2 segmen, format bebas) | `FZ/BL0277`, `FZ-ABP-2957_01`, `V-DPS-FDT21-FAT3` |

> Aturan parse: tipe WO = huruf pertama setelah tanggal; angka setelah huruf = urutan ke-N pada hari itu (bukan tipe baru).

### 6.2 Format Maintenance (M)

```
WO/260812/M01/FZ/BL0277
SITI SAKDEYA
JL.PULAU GALANG, GG. NILAWARSIKI, NO.10, PEMOGAN, DENPASAR SELATAN, KOTA DENPASAR, BALI
0857 0848 6239

FO CUT
@IYOOO00 @Kyy_YYY
```

| Field | Sumber |
|---|---|
| wo_code | Baris 1 |
| customer_name | Baris 2 |
| address | Baris 3 |
| phone | Baris 4 |
| action | Baris setelah kosong (mis. `FO CUT`) |
| assignees | Baris berisi `@mention` |

### 6.3 Format PSB / Instalasi (P)

```
WO/260810/P01/FZ-ABP-2957_01
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

Sharelocation: https://www.google.com/maps/place/...
```

| Field | Sumber |
|---|---|
| wo_code | Baris 1 |
| customer_name | Baris 2 |
| address | Baris 3 |
| phone | Baris 4 |
| package | Baris setelah kosong (mis. `PSB BASIC 50Mbps`) |
| flags | `TARIK`, `AKTIVASI` (baris berikutnya) |
| sn_ont | `SN ONT: ...` |
| username / password | `Username: ...` / `Password: ...` |
| infra | `Infra: @mention ...` |
| sharelocation | `Sharelocation: <URL>` |

### 6.4 Format Troubleshoot (T)

```
WO/260803/T01/V-DPS-FDT21-FAT3
V-DPS-FDT21-FAT3
JL. NAKULA, GG. JATAYU

Pengecekan FAT V-DPS-FDT21-FAT3

@yohanesharlan PKL
```

| Field | Sumber |
|---|---|
| wo_code | Baris 1 |
| segment | Baris 2 (nama segmen, juga muncul di baris 1 sebagai identitas) |
| address | Baris 3 |
| description | Baris setelah kosong (mis. `Pengecekan FAT ...`) |
| assignees | Baris `@mention` |

## 7. Format Report Selesai (dari chat)

Report dikenali dari baris pertama berisi kata kunci: `Report Maintenance`, `Repot pasang baru` (atau `Report pasang baru`), `Report troubleshoot`. WO di-cocokkan via `wo_code` (baris yang dimulai `WO/`). Jika kode tidak ditemukan → ditandai sebagai **unmatched** (tidak otomatis masuk, menunggu keputusan).

### 7.1 Report Maintenance

```
Report Maintenance

WO/260811/M01/FZ-ABQ-2212_01
RUDOLF KASENDA OKI
JL. SUBAK SARI, TIBUBENENG, KEC. KUTA UTARA, KABUPATEN BADUNG, BALI 80361, SAMPING CAFE DELMAR BEACH CLUB
0813 1539 7698

Case :
- Core di box panel putus
- IP mental

Action :
- Sambung ulang core di box panel
- koordinasi dengan NE
- Test Speed

Status : Cleared
```

### 7.2 Report PSB

```
Repot pasang baru

WO/260810/P01/FZ-ABP-2957_01
LILIK KHOLIDA
JL.PULAU GALANG, GG. NILAWARSIKI, NO.154, PEMOGAN, DENPASAR SELATAN, KOTA DENPASAR, BALI
0877 6864 6388

PSB BASIC 50Mbps

Detail laporan:
HARI / TANGGAL : 11 Agustus 2026
Pic teknisi : rifky dan iyo
Start  :
Finish :

PIC yang mendampingi : ybs
...
Solution
Tarik kabel FO 1 Core dari Splitter terdekat Mengarah ke client sepanjang meter
- Splicing kabel sisi FAT dan Client
...

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
```

### 7.3 Report Troubleshoot

```
Report troubleshoot

WO/260803/T01/V-DPS-FDT21-FAT3
V-DPS-FDT21-FAT3
JL. NAKULA, GG. JATAYU

Pengecekan FAT V-DPS-FDT21-FAT3

Cek redaman input dan output

Status: Cleared
```

### 7.4 Field Report yang Disimpan (JSON fleksibel)

| Key | Contoh |
|---|---|
| `status_report` | `Cleared` |
| `case` (list) | `["Core di box panel putus", "IP mental"]` |
| `action` (list) | `["Sambung ulang core di box panel", ...]` |
| `solution` (list) | `["Tarik kabel FO 1 Core ...", ...]` |
| `report_date` | `11 Agustus 2026` |
| `pic_teknisi` | `rifky dan iyo` |
| `start` / `finish` | jam kerja (bisa kosong) |
| `pic_pendamping` | `ybs` |
| `tarik` / `aktivasi` | `ok` |
| `meteran` | `Tarikan awal - meter`, `Meteran akhir: 0`, `Total tarikan` |
| `splitter` | `FADPS-FDT10-FAT0`, `DPS-FDT10-FAT03`, `port 3 1:4` |
| `alat_terpasang` (list) | `Patchcore Biru 1 Pcs`, `ONT Nokia 1 Pcs`, ... |
| `splicer` | `Said : Likkho`, `Pas : Fifiye2170` |
| `sn_ont`, `username`, `password` | seperti WO asal |

> Parsing report dibuat **toleran**: semua baris `Key : value` dikumpulkan, semua list berpeluru (`-`) dikumpulkan ke bucket kontekstual (Case/Action/Solution/Alat), sisanya disimpan sebagai teks mentah. Seluruh report mentah juga disimpan (field `report_raw`) agar tidak ada informasi yang hilang.

## 8. Status & Transisi

| Status | Arti | Masuk dari | Keluar ke |
|---|---|---|---|
| `masuk` | WO baru tiba | forward WO baru | `dikerjakan` (tombol Mulai) |
| `dikerjakan` | Sedang dikerjakan teknisi | `masuk` | `menunggu_verifikasi` (tombol Minta Verifikasi) |
| `menunggu_verifikasi` | Menunggu konfirmasi/verifikasi | `dikerjakan` | `done` (tombol Selesai atau report masuk) |
| `done` | Selesai + ada report (atau ditandai selesai manual) | `menunggu_verifikasi` | — (read-only, lihat report) |

Aturan:
- **Forward report** → langsung `done` (bisa dari status apa pun; waktu selesai dicatat).
- Tombol hanya jalan maju (validasi transisi di backend).
- Setiap transisi mencatat timestamp (`started_at`, `verification_at`, `done_at`).
- WO yang di-forward ulang (kode sama) → **tidak duplikat**; jika sudah ada, data lama dipertahankan dan laporan ditambahkan.

## 9. Spesifikasi Fungsional

### 9.1 Dashboard (halaman utama)
- Header: judul + ringkasan jumlah per status.
- **Tabs**: `Masuk (n)` · `Dikerjakan (n)` · `Menunggu Verifikasi (n)` · `Done (n)`.
- **Filter tipe**: Semua, PSB (P), Maintenance (M), Troubleshoot (T), Dismantle (D), Bangun Jaringan (B), Survey (S).
- **Search**: No. WO, nama klient, alamat, telepon.
- **Kartu WO** menampilkan:
  - Badge tipe berwarna (P/M/T/D/B/S) + No. WO (monospace)
  - Nama klient, alamat, telepon
  - Field kontekstual: paket (PSB), aksi (Maintenance), segmen + deskripsi (Troubleshoot)
  - SN ONT / Username / Password (PSB), link Sharelocation
  - Assignees/infra (@mention)
  - Timestamps status
  - Tombol aksi sesuai status (lihat §8)
- **Modal Report** (tab Done): tampilkan detail report (Case/Action/Solution/Status/alat/splitter dll + report mentah).
- Auto-refresh ringan (polling 30 dtk) agar update dari forward langsung terlihat.

### 9.2 API (FastAPI)

| Method | Path | Fungsi |
|---|---|---|
| GET | `/` | Serve dashboard (index.html) |
| GET | `/api/wo` | List WO; query: `status`, `type`, `q` (search), `limit` |
| GET | `/api/wo/{id}` | Detail WO + report |
| POST | `/api/wo/raw` | Terima teks pesan mentah → parse → insert/update → kembalikan hasil |
| POST | `/api/wo/{id}/status` | Transisi status; body `{status: "dikerjakan"}` (validasi transisi) |

### 9.3 Parser
- Modul `parser.py`: input teks mentah → dict terstruktur.
- Deteksi: report vs WO baru (kata kunci baris pertama vs baris `WO/`).
- Parse `wo_code` → `wo_date`, `wo_type`, `wo_seq`, `identitas`.
- Ekstraksi field per tipe (Tabel §6, §7).
- Robust: abaikan baris kosong berlebih, normalisasi spasi, toleransi huruf besar/kecil, `@`-mention dikumpulkan sebagai list.
- Error handling: teks tidak dikenal → return `{recognized: false, reason}` tanpa crash.

### 9.4 CLI untuk Jack
- `python -m app.cli add <file.txt>` / stdin: parse teks → simpan → cetak ringkasan + link WO di dashboard.
- `python -m app.cli move <wo_code> <status>`: pindah status (mis. saat user bilang "WO X selesai").
- `python -m app.cli list [--status] [--type]`: lihat antrian dari terminal.

### 9.5 Penyimpanan
- SQLite (`data/wo.db`), tabel `work_orders`:

```sql
CREATE TABLE work_orders (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  wo_code TEXT NOT NULL UNIQUE,
  wo_date TEXT,                -- ISO dari YYMMDD
  wo_type TEXT NOT NULL,       -- P/M/T/D/B/S
  wo_seq INTEGER,
  identitas TEXT,              -- bagian setelah kode tipe
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
  assignees TEXT,              -- JSON list @mention
  infra TEXT,                  -- JSON list
  flags TEXT,                  -- JSON list (TARIK/AKTIVASI)
  status TEXT NOT NULL DEFAULT 'masuk',
  report_json TEXT,            -- detail report (JSON)
  report_raw TEXT,             -- teks mentah report
  raw_text TEXT,               -- teks mentah WO asal
  created_at TEXT,
  started_at TEXT,
  verification_at TEXT,
  done_at TEXT
);
```

## 10. Arsitektur Teknis

### Stack (Opsi A — disetujui)
- **Backend**: Python 3 + FastAPI + Uvicorn, port **8600**.
- **DB**: SQLite (stdlib `sqlite3`, tanpa ORM — cukup untuk skala ini).
- **Frontend**: HTML + CSS + vanilla JS (single page, diserve FastAPI static). Tanpa framework/build step.
- **Testing**: pytest (parser + API dengan TestClient).

### Struktur File
```
fiberzone-wo/
├── PRD.md
├── README.md
├── requirements.txt        # fastapi, uvicorn, pytest, httpx
├── app/
│   ├── __init__.py
│   ├── main.py             # FastAPI app + routes
│   ├── db.py               # koneksi & query SQLite
│   ├── parser.py           # parser pesan WO & report
│   ├── cli.py              # CLI Jack (add/move/list)
│   └── static/
│       ├── index.html
│       ├── app.js
│       └── style.css
├── tests/
│   ├── test_parser.py      # fixture 6 format nyata + edge case
│   └── test_api.py         # add raw, list, filter, transisi
└── data/                   # wo.db (gitignored)
```

## 11. Strategi Testing

1. **Parser** (`test_parser.py`):
   - Parse ketiga format WO masuk (M/P/T) → semua field benar.
   - Parse ketiga format report (M/P/T) → `status_report`, list, dsb.
   - Parse kode WO: `WO/260812/M01/FZ/BL0277` → date `2026-08-12`, type `M`, seq `1`.
   - Edge: teks kosong, tanpa kode WO, tipe tidak dikenal (`X01`), format aneh → tidak crash, `recognized=false`.
   - Duplikat WO code → insert kedua tidak menggandakan.
2. **API** (`test_api.py`):
   - `POST /api/wo/raw` dengan teks maintenance → 200 + status `masuk`.
   - Report PSB dengan kode yang sudah ada → status jadi `done`, report tersimpan.
   - Report dengan kode tidak ada → 200 + `matched: false` + reason (WO dianggap unmatched, tidak dibuat otomatis).
   - Transisi valid (masuk→dikerjakan) → 200; transisi invalid (masuk→done langsung) → 422.
   - Filter `?type=M`, `?status=done`, search `?q=nama` → hasil sesuai.
3. **Browser**: buka `http://127.0.0.1:8600`, cek tab/kartu/filter/tombol/modal report, zero JS error di console.

## 12. Definisi Selesai (DoD)

- [ ] Parser lolos seluruh test parser (6 format + edge case).
- [ ] API lolos test (raw insert, report→done, transisi, filter).
- [ ] Dashboard tampil di port 8600, 4 tab berfungsi, search & filter jalan.
- [ ] Tombol transisi status jalan + timestamp tercatat.
- [ ] Forward WO nyata dari chat → muncul di tab Masuk.
- [ ] Forward report nyata → WO pindah ke Done + report terlihat di modal.
- [ ] `npm`-free; `python -m app.cli add/move/list` berfungsi.

## 13. Out of Scope (v1)

- Login/auth & multi-user.
- Auto-monitor channel Discord (cron) — forward tetap manual ke Jack.
- SLA / deadline / prioritas.
- Edit data WO (selain status).
- Export Excel/CSV.
- Integrasi dengan FiberMap / sistem lain.

## 14. Future Enhancements

- Export CSV/Excel untuk kebutuhan laporan quartal (reuse aturan parsing kode WO yang sudah ada di memory).
- Statistik harian/mingguan (WO per tipe, rata-rata durasi).
- Auth ringan (PIN/basic) jika diakses dari perangkat lain.
- Integrasi Google Sheets sebagai sumber tambahan.

## 15. Catatan Kunci

- Kode tipe WO: **P**=PSB, **M**=Maintenance, **T**=Troubleshoot, **D**=Dismantle, **B**=Bangun Jaringan, **S**=Survey (konsisten dengan aturan quartal report Fiberzone).
- SOP Fiberzone: tim wajib ambil 3 WO/hari; jika tidak ada WO PSB/Troubleshoot, dibuat WO Maintenance patroli — dashboard mendukung melihat antrian harian untuk memenuhi SOP ini.
