# Frontend Design — Fiberzone WO Dashboard

| | |
|---|---|
| **Project** | fiberzone-wo |
| **Versi** | 1.0 |
| **Tanggal** | 2026-08-12 |
| **Status** | Disetujui user (deviasi: dark theme + mode demo, via brainstorming) |
| **Sumber** | PRD.md §9.1, BACKLOG T-019–T-027 |

---

## 1. Ruang Lingkup

Frontend single-page dashboard untuk Fiberzone Work Order, dibangun **lebih dulu sebelum backend** (repo saat ini hanya berisi dokumentasi). Scope:

- 4 tab status: Masuk / Dikerjakan / Menunggu Verifikasi / Done.
- Kartu WO dengan field kontekstual per tipe (P/M/T/D/B/S).
- Search (No. WO/nama/alamat/telepon) + filter tipe.
- Transisi status via tombol pada kartu.
- Modal detail WO + modal report (tab Done).
- Modal "Tambah WO" (paste teks mentah) — BACKLOG T-027, disetujui dalam brainstorming.
- Toast notification, polling 30 dtk, statistik ringkas per status.
- **Mode demo + API asli**: berjalan standalone dengan mock data, otomatis memakai `/api/*` saat backend tersedia.

## 2. Keputusan (hasil brainstorming)

1. **Stack**: HTML + CSS + vanilla JS, tanpa framework/build step, npm-free (konsisten PRD Opsi A).
2. **Tema**: dark theme ops/monitoring.
3. **Data**: layer API adapter; deteksi mode saat boot (health check, timeout 500 ms). Gagal → demo mode dengan mock store; sukses → live mode.
4. **Struktur file**: `app/static/{index.html, style.css, app.js}` (sesuai PRD §10). Nanti diserve FastAPI tanpa perubahan.
5. Tambah WO via paste teks mentah disertakan.

## 3. Struktur File

```
app/static/
├── index.html   # header, chips statistik, tabs, toolbar, kontainer kartu, modal, toast, banner
├── style.css    # dark theme, CSS variables, responsif
└── app.js       # mode detection, API adapter, mock store, render, interaksi
```

Preview tanpa backend: `python3 -m http.server 8600` dari root repo (request `/api/*` gagal → demo mode).

## 4. Contract API (didefinisikan frontend; backend wajib mengikuti)

Semua respons JSON snake_case, error FastAPI standar `{"detail": "..."}`.

### GET `/api/health`
```json
{"status": "ok"}
```

### GET `/api/wo?status=&type=&q=&limit=`
```json
{"items": [WO...], "total": 0}
```
Item WO (semua kolom `work_orders` + report):

| Field | Tipe |
|---|---|
| id | int |
| wo_code | string |
| wo_date | string (ISO) |
| wo_type | string P/M/T/D/B/S |
| wo_seq | int |
| identitas | string |
| customer_name | string |
| address | string |
| phone | string |
| package, action, description, segment | string \| null |
| sn_ont, username, password, sharelocation | string \| null |
| assignees, infra, flags | array string (JSON) |
| status | string: `masuk`/`dikerjakan`/`menunggu_verifikasi`/`done` |
| report | object \| null (dari `report_json`) |
| report_raw | string \| null |
| raw_text | string \| null |
| created_at, started_at, verification_at, done_at | string \| null |

### GET `/api/wo/{id}` → WO object (sama seperti item di atas)

### POST `/api/wo/raw` body `{"text": "..."}`
```json
{"recognized": true, "wo_code": "WO/260812/M01/FZ/BL0277", "wo": {...}}
```
`recognized: false` → `{"recognized": false, "reason": "..."}` (tidak dibuat).

### POST `/api/wo/{id}/status` body `{"status": "dikerjakan"}`
- 200 → WO object baru (dengan timestamp transisi).
- 422 → `{"detail": "transisi tidak valid: masuk -> done"}`.

## 5. Komponen UI

- **Header**: judul "Fiberzone WO Dashboard" + 4 chip statistik `Masuk n · Dikerjakan n · Menunggu Verifikasi n · Done n` (dari hasil list).
- **Tabs**: `Masuk (n)` · `Dikerjakan (n)` · `Menunggu Verifikasi (n)` · `Done (n)`; tab aktif menyorot kartu status terkait.
- **Toolbar**: input search (placeholder "Cari No. WO, nama, alamat, telepon"), select tipe (Semua/PSB/Maintenance/Troubleshoot/Dismantle/Bangun Jaringan/Survey), tombol "+ Tambah WO".
- **Kartu WO**:
  - Badge tipe berwarna (P=PSB, M=Maintenance, T=Troubleshoot, D=Dismantle, B=Bangun Jaringan, S=Survey) + No. WO monospace.
  - Nama klient, alamat, telepon.
  - Field kontekstual: `package` (P), `action` (M), `segment` + `description` (T).
  - PSB: SN ONT / Username / Password + link Sharelocation (href).
  - Chip assignees & infra (@mention).
  - Timestamps status (mis. "Mulai: 12 Agu 10:15").
  - Tombol aksi per status:
    | Status | Tombol | Target |
    |---|---|---|
    | masuk | Mulai | dikerjakan |
    | dikerjakan | Minta Verifikasi | menunggu_verifikasi |
    | menunggu_verifikasi | Selesai | done |
    | done | Lihat Report | modal report |
- **Modal Detail WO**: semua field (termasuk yang kosong ditampilkan sebagai "—") + `raw_text` dalam `<pre>`.
- **Modal Report**: `status_report` badge, list Case/Action/Solution (berpeluru), Alat Terpasang, Splitter, Splicer, PIC teknisi/pendamping, start/finish, meteran, tarik/aktivasi, SN/Username/Password, dan `report_raw` dalam `<pre>`.
- **Modal Tambah WO**: textarea → `POST /api/wo/raw`. Demo: parse minimal (regex `WO/\d{6}/[PTM...]`, baris 2-4 = nama/alamat/telepon, sisanya disimpan ke `description`/`raw_text`) lalu insert mock store. Hasil: toast sukses + pindah tab Masuk.
- **Toast**: 3 dtk, warna sukses (hijau) / error (merah).
- **Banner mode demo**: "Mode Demo — backend belum terhubung. Data contoh lokal." di bawah header saat demo mode.

## 6. Data Flow

1. **Boot**: render kerangka → `health()` (fetch `/api/health`, AbortController 500 ms) → mode = LIVE | DEMO → `list()` → render.
2. **Render**: satu fetch `GET /api/wo?limit=500`; counts = agregasi client-side; kartu = filter `status` tab aktif + `type` + `q` (search client-side atas wo_code/customer_name/address/phone, case-insensitive).
3. **Polling**: live mode, tiap 30 dtk `list()` ulang, pertahankan tab/search/filter aktif; tanpa flash (diff sederhana: replace kontainer).
4. **Transisi**: `POST /api/wo/{id}/status` → toast sukses + refresh list; 422 → toast pesan detail. Demo mode: mutasi mock store (set status + timestamp), toast, re-render.
5. **Error**: fetch gagal → toast error + banner "gagal ambil data" tanpa menimpa data terakhir; JSON invalid → state error; daftar kosong per tab → empty state "Belum ada WO" + hint.

## 7. Mode Demo — Mock Store

- 10 WO contoh realistis dari PRD §6-7: M01 FZ/BL0277 (SITI SAKDEYA), P01 FZ-ABP-2957_01 (LILIK KHOLIDA), T01 V-DPS-FDT21-FAT3 (dengan report), + variasinya tersebar di 4 status.
- 3 WO done memiliki `report` (Maintenance/PSB/Troubleshoot) dengan semua bucket: case, action, solution, alat_terpasang, splitter, splicer, meteran, pic_teknisi, report_raw.
- Transisi & tambah WO memutasi store lokal; id increment; timestamp `new Date().toISOString()`.
- Mode demo tidak polling (tidak ada data baru).

## 8. Verifikasi (fase frontend)

1. `python3 -m http.server 8600` dari root → buka `http://127.0.0.1:8600/app/static/` (atau root dengan symlink sementara) — pastikan demo mode aktif, zero console error.
2. Browser drive: 4 tab tampil + count benar; search "siti" memfilter; filter tipe P; klik Mulai → kartu pindah ke Dikerjakan + timestamp; Done → modal report berisi case/action/solution/report_raw; Tambah WO paste contoh PRD §6.2 → muncul di Masuk; toast muncul; tutup/buka modal.
3. Responsif: lebar 360 px tidak pecah.
4. Contract API diverifikasi belakangan saat backend dibangun (test_api.py memakai shape di §4).

## 9. Out of Scope (v1)

Backend FastAPI, parser Python, CLI, auth, export, edit data (selain status), auto-monitor Discord.