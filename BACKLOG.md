# BACKLOG — Fiberzone Work Order Dashboard

> **Status:** [🟡 In Progress]
> **Version:** v1.0.0
> **Last Updated:** 2026-08-12
> **Repository:** `/home/swanster/project6661/fiberzone-wo`

---

## 📋 Legend

| Status | Meaning |
|---|---|
| ✅ **Done** | Implemented and committed |
| 🟡 **In Progress** | In process (sub-agent) |
| 🔴 **Missing** | Not yet implemented |
| ⚠️ **Blocked** | Blocked by dependency or external issue |

---

## 📌 Task List (Task Management)

| ID | Task | Status | Commit | Effort | Priority |
|---|---|---|---|---|---|
| T-001 | Git repo init & .gitignore | ✅ Done | T-001 | 5 min | Must |
| T-002 | Python environment & requirements | ✅ Done | T-002 | 10 min | Must |
| T-003 | FastAPI project scaffold | ✅ Done | T-003 | 30 min | Must |
| T-004 | SQLite database schema | ✅ Done | T-004 | 15 min | Must |
| T-005 | ROADMAP.md baseline | ✅ Done | T-005 | 5 min | Must |
| T-006 | BACKLOG.md baseline | ✅ Done | T-006 | 5 min | Must |
| T-007 | DEVLOG.md baseline | ✅ Done | T-007 | 5 min | Must |
| T-008 | Environment config (.env.example) | ✅ Done | T-008 | 10 min | Must |
| T-009 | CI/CD pipeline (GitHub Actions) | ✅ Done | T-009 | 20 min | Must |
| T-010 | Parser engine (6 formats) | ✅ Done | T-010 | 45 min | Must |
| T-011 | Parser test (6 formats + edge case) | ✅ Done | T-011 | 20 min | Must |
| T-012 | Parser edge case tests | ✅ Done | T-012 | 15 min | Must |
| T-013 | Parser integration test | ✅ Done | T-013 | 15 min | Must |
| T-014 | API CRUD endpoints | ✅ Done | T-014 | 30 min | Must |
| T-015 | Report parsing endpoint | ✅ Done | T-015 | 25 min | Must |
| T-016 | Filter & search API | ✅ Done | T-016 | 20 min | Must |
| T-017 | Status transition API | ✅ Done | T-017 | 20 min | Must |
| T-018 | Health check endpoint | ✅ Done | T-018 | 5 min | Must |
| T-019 | HTML dashboard layout | ✅ Done | T-019 | 40 min | Must |
| T-020 | CSS styling | ✅ Done | T-020 | 15 min | Must |
| T-021 | JavaScript logic | ✅ Done | T-021 | 30 min | Must |
| T-022 | Real-time polling | ✅ Done | T-022 | 15 min | Should |
| T-023 | Search & filter | ✅ Done | T-023 | 20 min | Should |
| T-024 | Modal report | ✅ Done | T-024 | 20 min | Should |
| T-025 | Toast notification | ✅ Done | T-025 | 15 min | Should |
| T-026 | Status transition UI | ✅ Done | T-026 | 15 min | Must |
| T-027 | Add & View details | ✅ Done | T-027 | 20 min | Should |
| T-028 | CLI add command | ✅ Done | T-028 | 25 min | Must |
| T-029 | CLI move command | ✅ Done | T-029 | 20 min | Must |
| T-030 | CLI list command | ✅ Done | T-030 | 15 min | Must |
| T-031 | CLI report command | ✅ Done | T-031 | 15 min | Should |
| T-032 | Parser test (all formats) | ✅ Done | T-032 | 20 min | Must |
| T-033 | API CRUD test | ✅ Done | T-033 | 25 min | Must |
| T-034 | Integration test | ✅ Done | T-034 | 25 min | Must |
| T-035 | Edge case test | ✅ Done | T-035 | 15 min | Must |
| T-036 | Performance test | ✅ Done | T-036 | 10 min | Should |

---

## 📊 Progress Summary

| Phase | Items | Complete | Progress |
|---|---|---|---|
| Fase 0 (Foundation) | 9 tasks | 9 ✅ | **100%** |
| Fase 1 (Parallel Core) | 8 tasks | 8 ✅ | **100%** |
| Fase 2 (Integration) | 19 tasks | 0 | **0%** |
| Fase 3 (Validation) | — | 0 | **0%** |

**Overall:** 25/58 tasks complete (43%)

---

## 📌 Task Overview (by task ID)

### Foundation Phase (T-001–T-009)

| ID | Title | Description |
|---|---|---|
| T-001 | Git repo init & .gitignore | Setup repository, create .gitignore dengan file yang perlu diignore |
| T-002 | Python environment & requirements | Create requirements.txt, install dependencies |
| T-003 | FastAPI project scaffold | Create app/main.py dengan router, CRUD untuk WO |
| T-004 | SQLite database schema | Create db.py dengan tabel work_orders |
| T-005 | ROADMAP.md baseline | Update ROADMAP.md dengan phase 0 status |
| T-006 | BACKLOG.md baseline | Update BACKLOG.md dengan task 1-6 |
| T-007 | DEVLOG.md baseline | Create devlog entry |
| T-008 | Environment config (.env.example) | Create .env.example dengan variabel umum |
| T-009 | CI/CD pipeline (GitHub Actions) | Create workflow YAML untuk lint, test, build |

### Parser Engine (T-010–T-013)

| ID | Title | Description |
|---|---|---|
| T-010 | Parser engine | Implement parser.py |
| T-011 | Parser test | test_parser.py |
| T-012 | Parser edge cases | Test input non-valid, kosong, format aneh |
| T-013 | Parser integration | Test parser dengan real messages |

### API Layer (T-014–T-018)

| ID | Title | Description |
|---|---|---|
| T-014 | API CRUD | Create /api/wo endpoint |
| T-015 | Report parsing | Create /api/wo/raw endpoint |
| T-016 | Filter & search | Create GET /api/wo?status=&type=&q=&limit= |
| T-017 | Status transition | Create POST /api/wo/{id}/status |
| T-018 | Health check | Create GET /api/health |

### Frontend Dashboard (T-019–T-027)

| ID | Title | Description |
|---|---|---|
| T-019 | HTML dashboard layout | Create index.html dengan 4 tab |
| T-020 | CSS styling | Create style.css |
| T-021 | JavaScript logic | Create app.js |
| T-022 | Real-time polling | Implement polling untuk update data |
| T-023 | Search & filter | Implement search bar dan filter |
| T-024 | Modal report | Implement modal detail report |
| T-025 | Toast notification | Implement toast system |
| T-026 | Status transition UI | Tombol pindah status |
| T-027 | Add & View details | UI untuk menambah WO baru |

### CLI (T-028–T-031)

| ID | Title | Description |
|---|---|---|
| T-028 | CLI add | python -m app.cli add <file.txt> |
| T-029 | CLI move | python -m app.cli move <wo_code> <status> |
| T-030 | CLI list | python -m app.cli list |
| T-031 | CLI report | python -m app.cli report <wo_code> |

### Testing (T-032–T-036)

| ID | Title | Description |
|---|---|---|
| T-032 | Parser test | Test semua format (6 tipe) |
| T-033 | API test | Test API endpoints |
| T-034 | Integration test | Test full workflow |
| T-035 | Edge case test | Test error handling |
| T-036 | Performance test | Test dengan 100+ WO |
