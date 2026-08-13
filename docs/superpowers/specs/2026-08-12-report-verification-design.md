# Design — Input Report di Status Menunggu Verifikasi

| | |
|---|---|
| **Project** | fiberzone-wo |
| **Tanggal** | 2026-08-12 |
| **Status** | Disetujui user (brainstorming: form terstruktur, gate done, field esensial) |
| **Sumber** | PRD §8 (transisi), feedback user di sesi frontend |

---

## 1. Masalah

Di tab **Menunggu Verifikasi**, kartu WO hanya punya tombol `Selesai` (langsung → done). Tim tidak bisa memasukkan report pengerjaan dari dashboard. Kebutuhan user: **report harus diisi dulu di tahap verifikasi, baru bisa di-done**.

## 2. Keputusan (hasil brainstorming)

1. **Input**: form terstruktur dalam modal (konsisten dengan modal yang sudah ada).
2. **Gate done**: tombol `Selesai` hanya tampil jika `wo.report` sudah ada. Tanpa report → tombol `Isi Report`. Mustahil skip report via UI.
3. **Field esensial**: Status Report (wajib), Case, Action, Solution, PIC Teknisi, Tanggal Laporan, Start/Finish. Kolom teknis (alat, splitter, meteran, splicer, SN) tetap ditampilkan di modal report bila ada (dari forward/backend), tapi tidak wajib di form.
4. Menyimpan report **tidak** mengubah status; done hanya via tombol `Selesai`.
5. Report bisa diedit selama masih `menunggu_verifikasi` (tombol berubah jadi `Edit Report`).

## 3. Perilaku Kartu (tab Menunggu Verifikasi)

| Kondisi | Aksi di kartu |
|---|---|
| Report belum diisi | `Isi Report` (primary) → modal form |
| Report sudah diisi | chip "Report terisi" + `Lihat Report` (ghost) + `Selesai` (primary) |

- Transisi done tetap `POST /api/wo/{id}/status` `{"status":"done"}` (backend boleh validasi report ada → 422 bila tidak).
- Tab Done tidak berubah: `Lihat Report` → modal report.

## 4. Modal Form Report (`#report-form-overlay`)

| Field | Kontrol | Wajib | Nilai simpan |
|---|---|---|---|
| Status Report | select: Cleared / Pending / In Progress / Lainnya | ✅ | `status_report` |
| Case | textarea, 1 item per baris | — | `case: []` |
| Action | textarea, 1 item per baris | — | `action: []` |
| Solution | textarea, 1 item per baris | — | `solution: []` |
| PIC Teknisi | text | — | `pic_teknisi` |
| Tanggal Laporan | date (default hari ini) | — | `report_date` |
| Start / Finish | time | — | `start` / `finish` |

- Header modal menampilkan `wo_code` + nama klient.
- Saat edit, semua field terisi nilai lama.
- Simpan → `wo.report = {...}` + `wo.report_raw` (representasi teks, kompatibel format report PRD §7) → toast → re-render.

## 5. Contract API Baru (ditambahkan ke spec frontend §4; backend wajib mengikuti)

### PUT `/api/wo/{id}/report`

Body:
```json
{"report": {"status_report": "Cleared", "case": ["..."], "action": ["..."], "solution": ["..."],
            "pic_teknisi": "...", "report_date": "2026-08-12", "start": "09:00", "finish": "11:30"},
 "report_raw": "teks representasi report"}
```
- 200 → WO object baru (dengan `report` tersimpan).
- 404 → `{"detail": "WO tidak ditemukan"}`.
- Semua key report opsional kecuali `status_report` (validasi backend disarankan, frontend memvalidasi).

Demo mode: `mockSaveReport(id, report)` mutasi mock store (upsert + set `report_raw`).

## 6. File yang Berubah

- `app/static/index.html` — markup `#report-form-overlay` (form fields).
- `app/static/style.css` — `.form-grid`, label/input/select/textarea form, `.chip.ok`.
- `app/static/app.js`:
  - `API.report(id, payload)` (live, PUT)
  - `mockSaveReport(id, report)` + `reportRawText(wo, report)` (demo)
  - `saveReport(id, report)` (dispatch live/demo)
  - `actionButton(wo)` — gate done untuk `menunggu_verifikasi`
  - `cardHTML(wo)` — chip "Report terisi"
  - `openReportForm(id)` (isi/edit) + `reportFormId` state
  - handler submit + cancel/backdrop di `bindEvents()`
  - klik handler kartu: action `report-form`

## 7. Verifikasi (browser, mode demo)

1. Tab Menunggu Verifikasi: kartu tanpa report hanya tombol `Isi Report`; tanpa tombol `Selesai`.
2. Isi form (Status wajib; kosong → toast error) → toast sukses, chip "Report terisi" + `Selesai` + `Lihat Report` muncul.
3. `Selesai` → pindah ke Done; modal report menampilkan Case/Action/Solution/PIC/tanggal/start/finish yang diisi.
4. Edit report (ubah Case) → tersimpan; tampilan konsisten.
5. Tab Done: report tampil normal; zero console error; responsif tidak rusak.

## 8. Out of Scope

Backend (endpoint PUT /api/wo/{id}/report menyusul di fase backend), validasi server-side, upload foto/lampiran report.