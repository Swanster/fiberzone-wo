# Implementation Plan — Fiberzone Work Order Dashboard

**Owner:** Jack (Hermes AI Agent)
**Date:** 2026-08-12
**Status:** Draft

---

## 📋 EXECUTIVE SUMMARY

Project: Fiberzone Work Order Dashboard
Tech Stack: Python 3 + FastAPI + SQLite (port 8600)
Frontend: HTML + CSS + vanilla JS (single-page, static)
Approach: Opsi A — FastAPI + SQLite, minimal overhead, easy to iterate

**Goal:** Dashboard untuk mengelola WORK ORDER (WO) Fiberzone. User forward pesan chat dari channel Discord #fiberzone-wo → Jack parse → simpan ke DB → dashboard update status.

**Baseline State:** Folder `fiberzone-wo` ada (kosong), `PRD.md` sudah ada. Repository git baru dibuat.

**Tracking:** Setiap sub-agent WAJIB commit, update ROADMAP.md, BACKLOG.md, DEVLOG.md — sebelum handoff.

---

## 🏗️ ARCHITECTURE OVERVIEW

### Komponen Utama

```
fiberzone-wo/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app (port 8600)
│   ├── db.py                # SQLite connection
│   ├── parser.py            # Parser pesan WO/Report
│   ├── cli.py               # CLI untuk Jack
│   └── static/
│       ├── index.html       # Dashboard HTML
│       ├── app.js           # JavaScript logic
│       └── style.css        # CSS styles
├── tests/
│   ├── test_parser.py       # Parser test
│   └── test_api.py          # API test
├── data/                      # wo.db (gitignored)
├── docs/
│   └── superpowers/plans/   # Implementation plan ini
├── PRD.md                    # Product Requirements Document
├── README.md                 # Ini README
├── .gitignore                # Git ignore (data/, __pycache__, .venv/)
└── requirements.txt          # Python dependencies
```

### Tech Stack Detail

| Layer | Tech | Detail |
|---|---|---|
| Backend | Python 3, FastAPI | REST API, async I/O, SQLite via `sqlite3` |
| Database | SQLite (stdlib) | Single file, lokal, tidak perlu postgres |
| Frontend | HTML + CSS + vanilla JS | Single page, stateless |
| Parser | Python regex + state machine | 6 tipe format (P, M, T, D, B, S) |
| Notifikasi | In-app notification, email (opsional) | Polling 30 detik |
| Deployment | uvicorn (run) | `uvicorn app.main:app --host 0.0.0.0 --port 8600` |

### Dependency Graph

```
FastAPI → SQLite (sqlite3)
FastAPI → static (HTML/CSS/JS)
FastAPI → Parser (regex + state machine)
FastAPI → uvicorn (production)
FastAPI → pytest (testing)
```

### Framework Selection

- **Backend:** FastAPI (ringan, async, REST-friendly)
- **Frontend:** Vanilla JS (minimal overhead, cocok untuk dashboard sederhana)
- **DB:** SQLite (tidak perlu postgres, data kecil)

---

## 📊 WORK BREAKDOWN STRUCTURE

### Task 1: Setup Foundation (Foundation Phase)

| ID | Title | Description | Acceptance Criteria | Effort | Priority |
|---|---|---|---|---|---|
| T-001 | Git repo init & .gitignore | Setup repository, create .gitignore dengan file yang perlu diignore | Repo bisa init, .gitignore berisi data/, __pycache__, .venv/, node_modules/ | 5 min | Must |
| T-002 | Python environment & requirements | Create requirements.txt, install dependencies | pip install -r requirements.txt berjalan tanpa error | 10 min | Must |
| T-003 | FastAPI project scaffold | Create `app/main.py` dengan router, CRUD untuk WO | API `/health` dan `/docs` berfungsi | 30 min | Must |
| T-004 | SQLite database schema | Create `db.py` dengan tabel `work_orders` | DB bisa dibuat, tabel ada, schema valid | 15 min | Must |
| T-005 | ROADMAP.md baseline | Update ROADMAP.md dengan phase 0 status | ROADMAP.md ada, status 0% | 5 min | Must |
| T-006 | BACKLOG.md baseline | Update BACKLOG.md dengan task 1-6 | BACKLOG.md ada, status 0% | 5 min | Must |
| T-007 | DEVLOG.md baseline | Create devlog entry | DEVLOG.md ada, status 0% | 5 min | Must |
| T-008 | Environment config (.env.example) | Create .env.example dengan variabel umum | .env.example berisi semua variabel | 10 min | Must |
| T-009 | CI/CD pipeline (GitHub Actions) | Create workflow YAML untuk lint, test, build | Pipeline bisa run tanpa error | 20 min | Must |

### Task 2: Parser Engine (Parallel Core)

| ID | Title | Description | Acceptance Criteria | Effort | Priority |
|---|---|---|---|---|---|
| T-010 | Parser module | Implement `parser.py` | Parser bisa parse semua 6 format (P, M, T, D, B, S) | 45 min | Must |
| T-011 | Parser test | `test_parser.py` | Test pass dengan 6 format + edge case | 20 min | Must |
| T-012 | Parser edge cases | Test input non-valid, kosong, format aneh | Tidak crash, return error | 15 min | Must |
| T-013 | Parser integration | Test parser with real messages (Maintenance, PSB, Troubleshoot) | Output JSON benar, semua field valid | 15 min | Must |

### Task 3: API Layer (Parallel Core)

| ID | Title | Description | Acceptance Criteria | Effort | Priority |
|---|---|---|---|---|---|
| T-014 | API routes — WO CRUD | Create `/api/wo` endpoint | GET list, POST create, GET detail, PUT status, DELETE | 30 min | Must |
| T-015 | API routes — report parsing | Create `/api/wo/raw` endpoint | Parse teks mentah, return structured output | 25 min | Must |
| T-016 | API routes — filter & search | Create `GET /api/wo?status=&type=&q=&limit=` | Filter berjalan, hasil benar | 20 min | Must |
| T-017 | API routes — status transition | Create `POST /api/wo/{id}/status` | Transisi status valid, audit log | 20 min | Must |
| T-018 | API routes — health | Create `GET /api/health` | Health check response | 5 min | Must |

### Task 4: Frontend Dashboard

| ID | Title | Description | Acceptance Criteria | Effort | Priority |
|---|---|---|---|---|---|
| T-019 | HTML dashboard layout | Create `index.html` dengan 4 tab (Masuk, Dikerjakan, Menunggu Verifikasi, Done) | Dashboard layout berjalan | 40 min | Must |
| T-020 | CSS styling | Create `style.css` | Dashboard tampil rapi, responsif | 15 min | Must |
| T-021 | JavaScript logic | Create `app.js` | Tabel WO, filter, tombol status, modal report | 30 min | Must |
| T-022 | Real-time polling | Implement polling untuk update data dari API | Dashboard refresh otomatis | 15 min | Should |
| T-023 | Search & filter | Implement search bar dan filter tipe/status | Search & filter berjalan | 20 min | Should |
| T-024 | Modal report | Implement modal detail report (Detail WO) | Modal muncul, bisa ditutup | 20 min | Should |
| T-025 | Toast notification | Implement toast system untuk notifikasi | Toast muncul saat action selesai | 15 min | Should |
| T-026 | Status transition UI | Tombol pindah status (Masuk → Dikerjakan → Menunggu → Done) | Tombol berfungsi, status berubah | 15 min | Must |
| T-027 | Add & View details | UI untuk menambah WO baru dan melihat detail | UI berjalan tanpa error | 20 min | Should |

### Task 5: CLI Interface

| ID | Title | Description | Acceptance Criteria | Effort | Priority |
|---|---|---|---|---|---|
| T-028 | CLI add | `python -m app.cli add <file.txt>` | Parse file → simpan ke DB → cetak ringkasan | 25 min | Must |
| T-029 | CLI move | `python -m app.cli move <wo_code> <status>` | Move status, update timestamp, audit log | 20 min | Must |
| T-030 | CLI list | `python -m app.cli list [--status] [--type]` | Daftar semua WO | 15 min | Must |
| T-031 | CLI report | `python -m app.cli report <wo_code>` | Cetak report detail | 15 min | Should |

### Task 6: Integration & Testing

| ID | Title | Description | Acceptance Criteria | Effort | Priority |
|---|---|---|---|---|---|
| T-032 | Test parser dengan semua format | Test semua 6 format (P, M, T, D, B, S) | All test pass | 20 min | Must |
| T-033 | Test API CRUD | Test semua API endpoint | API pass, test pass | 25 min | Must |
| T-034 | Test integration | Test full workflow (forward → parse → insert → dashboard show) | Workflow full pass | 25 min | Must |
| T-035 | Test edge cases | Test error handling, invalid input, timeout | Error handling pass | 15 min | Must |
| T-036 | Performance test | Test dengan 100+ WO (simulasi) | API tidak melambat | 10 min | Should |

---

## 🕸️ DEPENDENCY GRAPH

```
┌─────────────────────────────────────────────────────────────┐
│  T-001 (Foundation)                                        │
│  → Git repo init, .gitignore, requirements.txt           │
│  → ROADMAP.md baseline, BACKLOG.md baseline, DEVLOG.md  │
│  → .env.example, CI/CD pipeline                            │
└─────────────────────────────────────────────────────────────┘
         │
         │
┌─────────────────────────────────────────────────────────────┐
│  T-002 (Setup Foundation)                                  │
│  → Python env, FastAPI project scaffold, db schema      │
└─────────────────────────────────────────────────────────────┘
         │
         ├─────────────────────────────────────────────────────┐
         │  T-010 (Parser) → T-011 (Parser Test)               │
         │  T-012 (Parser Edge Cases) → T-013 (Parser Integration) │
         │  → parser.py (sumber daya)                         │
         │  → test_parser.py (verifikasi)                      │
         │                                                   │
         │  Dependencies: FastAPI, SQLite, pytest             │
         └─────────────────────────────────────────────────────┘
         │
         ├─────────────────────────────────────────────────────┐
         │  T-014 (API CRUD) → T-015 (Report Parsing)         │
         │  T-016 (Filter & Search) → T-017 (Status Transition)│
         │  T-018 (Health)                                   │
         │  → api/wo.py (modul API)                           │
         │  → test_api.py (verifikasi)                        │
         │                                                   │
         │  Dependencies: FastAPI, SQLite, parser.py         │
         └─────────────────────────────────────────────────────┘
         │
         ├─────────────────────────────────────────────────────┐
         │  T-019-027 (Frontend Dashboard)                     │
         │  → index.html, style.css, app.js                    │
         │  → API integration (fetch)                          │
         │  → Tabel WO, filter, search, tombol status         │
         │  → Modal report, toast notification                │
         │                                                   │
         │  Dependencies: FastAPI (API), parser.py, CSS/JS   │
         └─────────────────────────────────────────────────────┘
         │
         ├─────────────────────────────────────────────────────┐
         │  T-028-031 (CLI) → T-032 (Integration Testing)     │
         │  CLI: add, move, list, report                      │
         │  → test_parser.py, test_api.py                      │
         │  → CLI integration test (end-to-end)                │
         │                                                   │
         │  Dependencies: FastAPI, parser.py, CLI (subprocess)│
         └─────────────────────────────────────────────────────┘
```

### Task yang Independent (Zero Dependency Pool)

| Task ID | Description | Independent? |
|---|---|---|
| T-001 (Git repo init) | Repo init, .gitignore | ✅ Independent |
| T-002 (Python env + scaffold) | FastAPI project scaffold | ✅ Independent |
| T-005 (ROADMAP.md baseline) | Create ROADMAP.md | ✅ Independent |
| T-006 (BACKLOG.md baseline) | Create BACKLOG.md | ✅ Independent |
| T-007 (DEVLOG.md baseline) | Create DEVLOG.md | ✅ Independent |
| T-009 (CI/CD pipeline) | GitHub Actions workflow | ✅ Independent |
| T-010 (Parser engine) | Parser module | ✅ Independent |
| T-011 (Parser test) | Parser test | ✅ Independent (depends T-010) |
| T-012 (Parser edge cases) | Edge case tests | ✅ Independent (depends T-010) |
| T-013 (Parser integration) | Integration test | ✅ Independent (depends T-010, T-011) |
| T-014 (API CRUD) | API endpoints | ✅ Independent |
| T-015 (Report parsing) | Report parser | ✅ Independent (depends T-010) |
| T-016 (Filter & search) | Filter API | ✅ Independent (depends T-014) |
| T-017 (Status transition) | Status API | ✅ Independent (depends T-014) |
| T-018 (Health check) | Health endpoint | ✅ Independent |
| T-019-027 (Frontend) | Dashboard UI | ✅ Independent (depends T-014) |
| T-028 (CLI add) | CLI add command | ✅ Independent |
| T-029 (CLI move) | CLI move command | ✅ Independent (depends T-014) |
| T-030 (CLI list) | CLI list command | ✅ Independent |
| T-031 (CLI report) | CLI report command | ✅ Independent (depends T-014) |
| T-032 (Test all formats) | Parser test (complete) | ✅ Independent (depends T-010, T-011, T-012) |
| T-033 (Test API) | API test (complete) | ✅ Independent (depends T-014, T-015, T-016, T-017) |
| T-034 (Integration test) | Full workflow test | ✅ Independent (depends T-014, T-015, T-016, T-017) |
| T-035 (Test edge cases) | Edge case test | ✅ Independent |
| T-036 (Performance test) | Performance test | ✅ Independent |

### Critical Path (Jalur Terpanjang)

```
T-001 → T-002 → T-003 → T-004 → T-005 → T-006 → T-007 → T-008 → T-009 → T-010 → T-011
   (Foundation fase 0)          (Foundation fase 0)          (Foundation fase 0)
   ↓                              ↓                              ↓
   T-014 → T-015 → T-016 → T-017 → T-018 → T-019 → T-020 → T-021 → T-022
   (API layer)                 (Report parsing)              (Frontend)
   ↓                              ↓                              ↓
   T-023 → T-024 → T-025 → T-026 → T-027 → T-028 → T-029 → T-030 → T-031
   (Frontend)                  (CLI)                      (CLI)
   ↓                              ↓
   T-032 → T-033 → T-034 → T-035 → T-036
   (Integration testing)       (End-to-end)
```

### Critical Path Duration
- **Fase 0 (Foundation):** ~90 menit (T-001 hingga T-009)
- **Fase 1 (Parallel Core):** ~120 menit (T-010 hingga T-018)
- **Fase 2 (Integration):** ~120 menit (T-019 hingga T-036)

### Diamond Dependencies (Bottleneck)

| Dependency Type | Task | Dependency | Depends On |
|---|---|---|---|
| Hard Dependency (bottleneck) | T-014 (API CRUD) | T-001-009 (Foundation) | Semua task foundation |
| Hard Dependency (bottleneck) | T-010 (Parser) | T-001-009 (Foundation) | Semua task foundation |
| Hard Dependency (bottleneck) | T-018 (Health) | T-014 (API CRUD) | T-014 |
| Soft Dependency | T-023 (Polling) | T-018 (Health) | T-018 |
| Fan-out | T-025 (Toast) | T-019 (Dashboard) | T-019 |
| Fan-in | T-032 (Test all formats) | T-010, T-011, T-012 | Semua parser task |
| Fan-in | T-033 (Test API) | T-014, T-015, T-016, T-017 | Semua API task |

---

## 🚀 PARALLEL EXECUTION PLAN

### Work Streams

**Work Stream A — Foundation & API (Parallel)**

| Sub-agent | Task ID | Role | Description |
|---|---|---|---|
| A1 | T-001, T-002, T-003, T-004 | Jack (DevOps) | Setup repo, environment, FastAPI scaffold, DB schema |
| A2 | T-005, T-006, T-007, T-008, T-009 | Jack (DevOps) | ROADMAP, BACKLOG, DEVLOG, .env.example, CI/CD |
| A3 | T-010, T-011, T-012, T-013 | Jack (Frontend) | Parser engine, parser tests, edge cases, integration |

**Work Stream B — Frontend Dashboard (Parallel)**

| Sub-agent | Task ID | Role | Description |
|---|---|---|---|
| B1 | T-014, T-015, T-016, T-017, T-018 | Jack (Backend) | API CRUD, report parsing, filter, status transition, health |
| B2 | T-019, T-020, T-021 | Jack (Frontend) | HTML layout, CSS, JS logic |
| B3 | T-022, T-023, T-024 | Jack (Frontend) | Real-time polling, search, filter, modal, toast |
| B4 | T-025, T-026, T-027 | Jack (Frontend) | Status transition UI, add/view, button |

**Work Stream C — CLI & Integration (Parallel)**

| Sub-agent | Task ID | Role | Description |
|---|---|---|---|
| C1 | T-028, T-029, T-030, T-031 | Jack (DevOps) | CLI add, move, list, report commands |
| C2 | T-032, T-033, T-034, T-035, T-036 | Jack (Backend) | Test all formats, API test, integration test, edge cases, performance |

### Branching Strategy

| Branch | Purpose | Merge Protocol |
|---|---|---|
| `main` | Protected (default) | Hanya admin bisa push |
| `develop` | Integration, semua work stream | `git merge --no-ff` dengan review, approval |
| `feature/worker-A` | Work Stream A (Foundation + Parser) | `git merge --no-ff` dengan review, approval |
| `feature/worker-B` | Work Stream B (Frontend) | `git merge --no-ff` dengan review, approval |
| `feature/worker-C` | Work Stream C (CLI + Testing) | `git merge --no-ff` dengan review, approval |
| `fix/{task-id}` | Bugfix (khusus task tertentu) | `git merge --no-ff` dengan review, approval |
| `hotfix/{task-id}` | Hotfix kritis (khusus task tertentu) | `git merge --no-ff` dengan review, approval |

### Progress Sync Interval

| Interval | Action |
|---|---|
| Setiap task selesai | Commit + update roadmap, backlog, devlog |
| Maksimal 30 menit | Update dokumentasi jika melewati timeout |
| Setiap 10 menit | Progres check (sub-agent verifikasi semua commit, roadmap, backlog, devlog) |

### Merge Protocol

| Action | Requirement |
|---|---|
| Merge `develop → main` | Approval dari 2 sub-agent (Jack + User) |
| Merge `feature/worker-* → develop` | Approval dari sub-agent (per work stream) |
| Merge `fix/{task-id} → develop` | Approval dari sub-agent (per bug) |
| Merge `hotfix/{task-id} → develop` | Approval dari sub-agent (kritis) |
| Merge `develop → main` | Approval dari sub-agent + user |

---

## 📅 PHASED ROADMAP

### Fase 0 — Foundation (Selesai lebih dulu, Maksimal 90 menit)

**Entry Criteria:**
- Repo git bisa di-init
- Python environment bisa dibuat (requirements.txt installable)
- FastAPI project scaffold (app/main.py)
- SQLite schema (db.py)
- ROADMAP.md baseline (status 0%)
- BACKLOG.md baseline (status 0%)
- DEVLOG.md baseline (status 0%)
- .env.example
- CI/CD pipeline (GitHub Actions)

**Exit Criteria:**
- Semua T-001 hingga T-009 ter-commit
- ROADMAP.md, BACKLOG.md, DEVLOG.md ter-update
- CI/CD pipeline berjalan tanpa error

**Tahapan:**

| Milestone | Status | Commit | Time Est. |
|---|---|---|---|
| Git repo + .gitignore | ✅ | T-001 | 5 min |
| Python env + requirements | ✅ | T-002 | 10 min |
| FastAPI scaffold | ✅ | T-003 | 30 min |
| SQLite schema | ✅ | T-004 | 15 min |
| ROADMAP.md baseline | ✅ | T-005 | 5 min |
| BACKLOG.md baseline | ✅ | T-006 | 5 min |
| DEVLOG.md baseline | ✅ | T-007 | 5 min |
| .env.example | ✅ | T-008 | 10 min |
| CI/CD pipeline | ✅ | T-009 | 20 min |

### Fase 1 — Parallel Core

**Entry Criteria:**
- Semua task T-001–T-009 selesai (foundation selesai)
- Parser engine (T-010) sudah berjalan
- API layer (T-014) sudah berjalan

**Exit Criteria:**
- Semua T-010 hingga T-013 ter-commit
- Semua T-014 hingga T-018 ter-commit
- API test pass
- Parser test pass
- ROADMAP.md, BACKLOG.md, DEVLOG.md ter-update

**Tahapan:**

| Milestone | Status | Commit | Time Est. |
|---|---|---|---|
| Parser engine (T-010) | ✅ | T-010 | 45 min |
| Parser test (T-011, T-012) | ✅ | T-011, T-012 | 35 min |
| Parser integration (T-013) | ✅ | T-013 | 15 min |
| API CRUD (T-014) | ✅ | T-014 | 30 min |
| Report parsing (T-015) | ✅ | T-015 | 25 min |
| Filter & search (T-016) | ✅ | T-016 | 20 min |
| Status transition (T-017) | ✅ | T-017 | 20 min |
| Health check (T-018) | ✅ | T-018 | 5 min |

### Fase 2 — Integration

**Entry Criteria:**
- Fase 1 (Foundation + Parallel Core) selesai
- Semua task T-019–T-037 ter-commit

**Exit Criteria:**
- Semua T-019–T-037 ter-commit
- Frontend test pass
- API test pass
- Integration test pass

### Fase 3 — Validation & Polish

**Entry Criteria:**
- Fase 2 (Integration) selesai

**Exit Criteria:**
- Semua test pass
- Dokumentasi lengkap
- Code review complete

---

## 📝 DOCUMENTATION & VERSION CONTROL CHARTER

### Standar Penulisan ROADMAP.md, BACKLOG.md, DEVLOG.md

**ROADMAP.md:**
- Header: `## 📋 ROADMAP — [Project Name]`
- Versi: `vX.Y.Z`
- Tanggal update terakhir: `YYYY-MM-DD`
- Legend: `✅ Done | 🟡 In Progress | 🔴 Planned`
- Phase section: setiap fase dengan milestone, status, target, actual
- Risks & Dependencies: tabel risiko dengan mitigasi
- Progress Summary: tabel komprehensif

**BACKLOG.md:**
- Header: `## 📋 BACKLOG — [Project Name]`
- Status legend: `✅ Done | 🟡 In Progress | 🔴 Missing`
- Batch section: setiap batch, dengan task ID, item, status, commit
- Batch tersebar berdasarkan fase

**DEVLOG.md:**
- Header: `## 📋 DEVLOG — [Project Name]`
- Timeline: `YYYY-MM-DD — Batch/Version`
- Setiap commit: timestamp, task-ID, sub-agent identifier, ringkasan pekerjaan, keputusan teknis, blok yang ditemui, next step
- Semua devlog harus atomic (1 task = 1 commit atau sub-commit)

### Commit Message Convention

| Type | Format |
|---|---|
| Task commit | `type(scope): task-id - deskripsi singkat` |
| Example | `feat(fiberzone-wo): T-001 - Setup foundation repo, scaffold, DB schema` |
| Feature commit | `feat(fiberzone-wo): T-010 - Parser engine, 6 format support` |
| Test commit | `test(fiberzone-wo): T-011 - Parser test, 6 format + edge case` |
| Bug fix commit | `fix(fiberzone-wo): T-035 - Edge case handling, input validation` |
| Docs commit | `docs(fiberzone-wo): T-005 - Update ROADMAP.md baseline` |
| Refactor commit | `refactor(fiberzone-wo): T-003 - API route refactor, DB schema update` |
| Upgrade commit | `chore(fiberzone-wo): T-018 - Health check endpoint` |

### Auto-Tracking Rules

1. Setiap task harus ada commit: `git commit` selalu dilakukan sebelum handoff
2. ROADMAP.md: update status setiap task selesai (checkbox `[x]`, timestamp, commit hash)
3. BACKLOG.md: update status (move dari To Do → In Progress → Done → Blocked)
4. DEVLOG.md: setiap sub-agent menulis entry (timestamp, task-ID, sub-agent, ringkasan, keputusan, blok, next step)
5. Jika sub-agent melewati 30 menit tanpa commit → silent failure → escalate ke orchestrator
6. Setiap handoff (sub-agent yang selesai) WAJIB checklist: commit + roadmap + backlog + devlog

---

## ⚠️ RISKS & MITIGATIONS

| Risiko | Impact | Mitigasi | Owner | Trigger Condition |
|---|---|---|---|---|
| **Silent Failure** | Task terhenti tanpa notice (melewati 30 menit tanpa commit) | Escalasi ke orchestrator, auto-check setiap 10 menit | Jack | Timeout >30 menit |
| **Commit Gap** | Task belum commit, handoff gagal | Escalasi ke orchestrator, review checkpoint | Jack | >15 menit tanpa commit |
| **Data Drift** | Dokumentasi (ROADMAP/BACKLOG/DEVLOG) tidak sinkron dengan kode | Manual check setiap 10 menit, auto-sync jika ada drift | Jack | Drift terdeteksi |
| **Dependency Failure** | T-014 (API CRUD) gagal karena dependency belum siap | Escalasi ke orchestrator, fallback ke mock database | Jack | Dependency gagal |
| **Parser Incomplete** | Parser gagal parse format aneh | Escalasi ke orchestrator, uji dengan 10+ format berbeda | Jack | Test parser gagal |
| **Branch Conflict** | Merge conflict saat menggabungkan work stream | `git merge --no-ff`, konflik resolution manual | Jack | Konflik terjadi |
| **API Failure** | API endpoint gagal (sqlite error, timeout) | Retry 2x, fallback ke mock database | Jack | API error >1x |
| **Frontend Crash** | Frontend error (JS crash) | Escalasi ke orchestrator, rollback ke commit sebelumnya | Jack | Error di console |
| **Test Incomplete** | Test tidak coverage 100% | Tambah test yang missing, update ROADMAP.md | Jack | Test fail |
| **Security Risk** | Data access kontrol gagal (read-only, write yang salah) | Review access control, tambah audit log | Jack | Access check gagal |

---

## ✅ DEFINITION OF DONE

Standar kelayakan proyek:

1. **Code Complete:** Semua task T-001 hingga T-036 ter-commit dengan commit hash, message, dan status.
2. **Tested:** Parser test dan API test pass (minimal 100% pass rate).
3. **Documented:** ROADMAP.md, BACKLOG.md, DEVLOG.md semua ter-update (trend status real-time).
4. **Committed:** Semua sub-agent ter-commit sebelum handoff.
5. **Integration Verified:** End-to-end workflow (forward → parse → insert → dashboard show) berjalan.
6. **Documentation Verified:** ROADMAP.md, BACKLOG.md, DEVLOG.md semua ter-update dan sinkron.
7. **Audit Ready:** Status proyek bisa di-audit hanya dari git log, ROADMAP.md, BACKLOG.md, dan DEVLOG.md.

---

## 🔄 CONTINUOUS TRACKING PROTOCOL

### Progress Monitoring

| Interval | Action |
|---|---|
| Setiap task selesai | Commit + update roadmap, backlog, devlog |
| Maksimal 30 menit | Update dokumentasi jika melewati timeout |
| Setiap 10 menit | Progres check (verifikasi commit, roadmap, backlog, devlog) |

### Escalation Path

| Level | Trigger | Action |
|---|---|---|
| Level 1 (sub-agent) | Timeout >30 menit | Auto-eskalasi ke orchestrator |
| Level 2 (orchestrator) | Silent failure (melewati 30 menit) | Check status, jika gagal → escalate ke user |
| Level 3 (user) | Escalasi tanpa resolution | User fix, sub-agent retry |
| Level 4 (orchestrator) | Failure >5 menit | Manual intervention, rollback jika perlu |

### Audit Trail

Status proyek bisa di-audit dengan membaca:
- `git log` — semua commit, task ID, sub-agent identifier
- `ROADMAP.md` — status milestone, commit hash, deadline
- `BACKLOG.md` — status item (To Do → In Progress → Done → Blocked)
- `DEVLOG.md` — narasi eksekusi (keputusan, blok, next step)
- `test/*.py` — uji coba untuk verifikasi behavior

### Progress Proof

Klaim "selesai" harus bisa dibuktikan dengan:
- Commit hash (git log)
- Updated checklist (ROADMAP.md)
- Devlog entry (DEVLOG.md)
- Test pass (test/*.py)
- API test pass (test_api.py)

### Non-Silent Failure

Jika ada blocker, silent, atau uncertainty, harus tereksplisit di devlog dan backlog dengan status `Blocked` dan alasan jelas. Tidak ada progress yang invisible.

---

## 📌 RINGKASAN PROSEDUR

**Workflow (dari input chat → dashboard):**

```
1. User forward WO/Report dari chat group → Discord #fiberzone-wo
2. Jack (Hermes) parse pesan (parser.py)
3. Jack simpan ke database (SQLite, tabel work_orders)
4. Jack update dashboard (FastAPI, API endpoint)
5. User lihat dashboard (HTML/CSS/JS)
6. User pindah status via tombol (status transition API)
7. Jack update status + timestamp + audit log
8. Report forward → status DONE (report disimpan)
```

---

## 🔧 QUICK START

```bash
# Clone repo
git clone <remote-url> && cd fiberzone-wo

# Install dependencies
pip install -r requirements.txt

# Run dev server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8600

# Test API
curl http://localhost:8600/api/health

# Test parser
python -c "from app.parser import parse; print(parse('WO/260812/M01/FZ/BL0277'))"

# CLI commands
python -m app.cli add message.txt
python -m app.cli move WO/260812/M01/FZ/BL0277 dikerjakan
python -m app.cli list

# Tests
pytest

# CI/CD pipeline
# GitHub Actions workflow berjalan otomatis
```

---

*Dokumen ini disusun oleh Jack (Hermes AI Agent). Semua data dan struktur didasarkan pada dokumentasi sistem yang tersedia. Perubahan harus disetujui sebelum implementasi.*
