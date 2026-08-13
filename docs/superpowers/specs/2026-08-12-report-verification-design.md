# Design — Input Report di Status Menunggu Verifikasi (+ Paste dari Chat)

| | |
|---|---|
| **Project** | fiberzone-wo |
| **Tanggal** | 2026-08-12 (diperbarui 2026-08-13: paste report dari chat, field teknis, edit post-done, preservasi report_raw) |
| **Status** | Disetujui user (brainstorming: form terstruktur, gate done, paste report) |
| **Sumber** | PRD §8 (transisi), PRD §7 (format report), feedback user di sesi frontend |

---

## 1. Masalah

Di tab **Menunggu Verifikasi**, kartu WO hanya punya tombol `Selesai` (langsung → done). Tim tidak bisa memasukkan report pengerjaan dari dashboard. Kebutuhan user: **report harus diisi dulu di tahap verifikasi, baru bisa di-done**. Selain form, tim menerima report sebagai **teks chat (Telegram)** dan ingin menempelkannya langsung.

## 2. Keputusan (hasil brainstorming)

1. **Input jalur ganda**:
   - Form terstruktur dalam modal (`Isi Report`).
   - **Paste teks report dari chat** (`Paste Report`): teks di-parse otomatis → `wo.report` → **status langsung `done`** (keputusan user: paste = konfirmasi selesai dari teknisi; tidak melewati tombol Selesai).
2. **Gate done (form)**: tombol `Selesai` hanya tampil jika `wo.report` sudah ada. Tanpa report → tombol `Isi Report` + `Paste Report`. Mustahil skip report via UI.
3. **Field esensial + teknis**: form mencakup Status Report (wajib), Case, Action, Solution, PIC Teknisi, Tanggal Laporan, Start/Finish, PIC Pendamping, Tarik, Aktivasi, Meteran, Splitter, Alat Terpasang, Splicer, SN ONT, Username, Password. Ini memastikan data hasil paste yang kurang bisa dilengkapi.
4. Menyimpan report via form **tidak** mengubah status; done hanya via tombol `Selesai` (atau paste report).
5. **Report tetap bisa diedit setelah done** (tab Done → `Edit Report`) — untuk melengkapi data instalasi yang kurang; save form **merge** dengan report lama (key yang tidak disentuh form tidak dihapus).
6. **`report_raw` dipertahankan**: edit via form TIDAK menimpa raw hasil paste; raw hanya diregenerasi bila belum ada. Baris chat yang tidak dipetakan parser (mis. `No. Hashem`) tetap utuh.

## 3. Perilaku Kartu

| Tab | Kondisi | Aksi di kartu |
|---|---|---|
| Menunggu Verifikasi | Report belum diisi | `Isi Report` (primary) + `Paste Report` (ghost) |
| Menunggu Verifikasi | Report sudah diisi | chip "Report terisi" + `Edit Report` (ghost) + `Lihat Report` (ghost) + `Selesai` (primary) |
| Done | — | `Edit Report` (ghost) + `Lihat Report` (ghost) |

- Transisi done tetap `POST /api/wo/{id}/status` `{"status":"done"}` (backend boleh validasi report ada → 422 bila tidak).

## 4. Modal Form Report (`#report-form-overlay`)

| Field | Kontrol | Wajib | Nilai simpan |
|---|---|---|---|
| Status Report | select: Cleared / Pending / In Progress / Lainnya | ✅ | `status_report` |
| Case | textarea, 1 item per baris | — | `case: []` |
| Action | textarea, 1 item per baris | — | `action: []` |
| Solution | textarea, 1 item per baris | — | `solution: []` |
| PIC Teknisi | text | — | `pic_teknisi` |
| PIC Pendamping | text | — | `pic_pendamping` |
| Tanggal Laporan | date (default hari ini) | — | `report_date` |
| Start / Finish | time | — | `start` / `finish` |
| Tarik / Aktivasi | text | — | `tarik` / `aktivasi` |
| Meteran | textarea, 1 item per baris | — | `meteran` |
| Splitter | textarea, 1 item per baris | — | `splitter` |
| Alat Terpasang | textarea, 1 item per baris | — | `alat_terpasang: []` |
| Splicer | textarea, 1 item per baris | — | `splicer` |
| SN ONT | text | — | `sn_ont` |
| Username / Password | text | — | `username` / `password` |

- Header modal menampilkan `wo_code` + nama klient.
- Saat edit, semua field terisi nilai lama (termasuk hasil paste).
- Simpan → merge dengan report lama (`{...prev, ...form}`) → `report_raw` dipertahankan bila sudah ada → toast → re-render.

## 5. Modal Paste Report (`#paste-report-overlay`)

- Dibuka dari tombol `Paste Report` pada kartu Menunggu Verifikasi (tanpa report).
- Textarea besar + label WO tujuan (kode + nama).
- **Validasi**: parser demo mengekstrak baris `WO/...` dari teks; **harus sama persis dengan kode kartu** → mismatch = toast error, tidak ada mutasi (demo maupun live).
- Simpan → `parseReportDemo(text)` → `wo.report` + `report_raw` = **teks paste asli** + `status = done` + `done_at`.
- Live mode: `PUT /api/wo/{id}/report` (payload `{report, report_raw}`) lalu `POST /api/wo/{id}/status {"status":"done"}`.

### Parser demo `parseReportDemo(text)` (toleran, PRD §7.4)

- Strip karakter tak terlihat (U+200E/U+200F/U+200B/U+FEFF).
- Baris `WO/\d{6}/[A-Z]\d+/...` → `wo_code`; teks tanpa baris WO → `recognized: false`.
- Mapping key → field:

| Pola teks | Field |
|---|---|
| `Status : ...` | `status_report` |
| `HARI / TANGGAL : ...` | `report_date` |
| `Pic teknisi : ...` | `pic_teknisi` |
| `PIC yang mendampingi : ...` (juga `PIC Pendamping`) | `pic_pendamping` |
| `Start :` / `Finish :` | `start` / `finish` |
| `Tarik :` / `Aktivasi :` | `tarik` / `aktivasi` |
| `Meteran akhir:` / `Total tarikan :` / baris berisi "tarikan"/"meter" | `meteran` (multi-baris) |
| header `Case :` + baris `- item` | `case: []` |
| header `Action :` + baris `- item` | `action: []` |
| header `Solution` + baris `- item` | `solution: []` |
| header `SOLITER / ...` / `Splitter` + baris berikut | `splitter` (header ikut tersimpan) |
| header `Alat Yang Terpasang :` + baris `- item` | `alat_terpasang: []` |
| `Said : ...` / `Pas : ...` | `splicer` (baris header ikut) |
| `SN ONT:` / `Username:` / `Password:` | `sn_ont` / `username` / `password` |

Urutan prioritas per baris: (1) key:value yang dikenal → field (termasuk `said`/`pas` → splicer); (2) header section → set mode (+ append baris header utk splitter/splicer); (3) bullet → append ke section aktif; (4) baris polos → append ke section aktif (splitter/splicer/solution) atau `meteran` bila berisi "tarikan"/"meter"; (5) sisanya diabaikan (tetap utuh di `report_raw`).

## 6. Contract API Baru (ditambahkan ke spec frontend §4; backend wajib mengikuti)

### PUT `/api/wo/{id}/report`

Body:
```json
{"report": {"status_report": "Cleared", "case": ["..."], "action": ["..."], "solution": ["..."],
            "pic_teknisi": "...", "pic_pendamping": "...", "report_date": "2026-08-12",
            "start": "09:00", "finish": "11:30", "tarik": "ok", "aktivasi": "ok",
            "meteran": "...", "splitter": "...", "alat_terpasang": ["..."], "splicer": "...",
            "sn_ont": "...", "username": "...", "password": "..."},
 "report_raw": "teks representasi report (dari paste atau regenerasi form)"}
```
- 200 → WO object baru (dengan `report` tersimpan).
- 404 → `{"detail": "WO tidak ditemukan"}`.
- Semua key report opsional kecuali `status_report` (validasi backend disarankan, frontend memvalidasi).

Demo mode: `mockSaveReport(id, report)` mutasi mock store (upsert, preserve `report_raw` bila ada); `applyParsedReport(wo, report, rawText)` untuk jalur paste (simpan `report_raw` = teks asli + status done).

## 7. File yang Berubah

- `app/static/index.html` — `#report-form-overlay` diperluas (field teknis), `#paste-report-overlay` (baru).
- `app/static/style.css` — `.form-grid` (reuse), `p.dim`.
- `app/static/app.js`:
  - `API.report(id, payload)` (live, PUT) + `API.transition(id, status)`
  - `mockSaveReport(id, report)` (demo; preserve `report_raw` yang sudah ada)
  - `reportRawText(wo, report)` (demo; termasuk field teknis)
  - `applyParsedReport(wo, report, rawText)` (paste demo: report + raw asli + status done)
  - `parseReportDemo(text)` (parser toleran) + `openPasteReport(id)` + `pasteReportId`
  - `saveReport(id, report)` (merge dengan report lama; dispatch live/demo)
  - `actionButton(wo)` — `Paste Report` di menunggu_verifikasi, `Edit Report` di done
  - `cardHTML(wo)` — chip "Report terisi"
  - `openReportForm(id)` (isi/edit, prefill semua field termasuk teknis)
  - handler submit/cancel/backdrop di `bindEvents()`; klik handler kartu: action `paste-report`

## 8. Verifikasi (browser, mode demo)

1. Menunggu Verifikasi: kartu tanpa report → `Isi Report` + `Paste Report`, tanpa `Selesai`.
2. Paste teks report PSB (format chat, baris `WO/...` cocok) → kartu pindah ke **Done**; modal report menampilkan status/tanggal/PIC/pendamping/tarik/aktivasi/meteran/solution/splitter (header SOLITER ikut)/alat/splicer/SN/username/password sebagai field terpisah.
3. `report_raw` menyimpan **teks paste asli** (baris tidak dikenal seperti `No. Hashem` tetap ada).
4. Kode WO tidak cocok → toast error, tidak ada mutasi.
5. Tab Done: `Edit Report` → prefill semua field (hasil paste) → ubah SN → simpan → SN berubah, splitter/alat/solution tetap (merge), `report_raw` asli tetap memuat `No. Hashem` (preservasi).
6. Form wajib Status Report (kosong → toast error); zero console error.

## 9. Out of Scope

Backend (endpoint PUT /api/wo/{id}/report menyusul di fase backend), validasi server-side, upload foto/lampiran report, parser server-side penuh (PRD §7.4) — demo memakai regex JS; live mode mengirim hasil parse client + `report_raw` asli ke backend.