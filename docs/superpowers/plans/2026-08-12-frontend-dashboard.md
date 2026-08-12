# Frontend Dashboard Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the vanilla-JS dark-theme Fiberzone WO dashboard (`app/static/`) with demo+live mode, per spec `docs/superpowers/specs/2026-08-12-frontend-design.md`.

**Architecture:** Single-page static frontend — `index.html` (structure) + `style.css` (dark theme) + `app.js` (all logic: data layer, render, interaction). No build step, no npm, no framework. At boot, `app.js` probes `GET /api/health` (500 ms timeout); success → live mode against `/api/*`, failure → demo mode with an in-memory mock store so every UI feature works standalone. Backend does not exist yet; the API contract in spec §4 is binding for the future backend.

**Tech Stack:** HTML5, CSS (custom properties), vanilla JS (ES2017+), fetch + AbortController. Serving for preview: `python3 -m http.server 8600`.

## Global Constraints

- No build step, no npm, no framework, no external CDN — three files only: `app/static/index.html`, `app/static/style.css`, `app/static/app.js`.
- UI copy in Indonesian (tab labels: `Masuk`, `Dikerjakan`, `Menunggu Verifikasi`, `Done`).
- API contract: exactly as spec §4 — GET `/api/health`, GET `/api/wo?status=&type=&q=&limit=`, GET `/api/wo/{id}`, POST `/api/wo/{id}/status` `{"status": ...}`, POST `/api/wo/raw` `{"text": ...}`; error shape `{"detail": "..."}`.
- Status values: `masuk`, `dikerjakan`, `menunggu_verifikasi`, `done` (valid forward-only transitions per PRD §8).
- Type filter values: `all`, `P`, `M`, `T`, `D`, `B`, `S`.
- Poll interval 30 s, live mode only.
- Timestamps displayed as `12 Agu 10:15` style (Indonesian short), from ISO strings.
- Every user-visible string must be `escapeHTML`-escaped before insertion (no `innerHTML` with raw data).
- Verification is browser-driven (no JS test framework per Global Constraints): each task ends with a concrete browser check; final task runs the full checklist from spec §8.

## File Structure

```
app/static/
├── index.html   # Task 1 — full page skeleton
├── style.css    # Task 2 — dark theme + components
└── app.js       # Tasks 3-7 — data layer, render, interactions
```

All files are created (repo has no `app/` yet). `app.js` is built incrementally in Tasks 3-6; later tasks modify the file created in Task 3.

---

### Task 1: Page skeleton (`index.html`)

**Files:**
- Create: `app/static/index.html`

**Interfaces:**
- Consumes: nothing.
- Produces: element IDs later tasks bind to — `#stats-chips`, `#tabs`, `#tab-masuk`, `#tab-dikerjakan`, `#tab-menunggu_verifikasi`, `#tab-done`, `#search-input`, `#type-select`, `#btn-add`, `#cards`, `#demo-banner`, `#error-banner`, `#toast-container`, `#modal-overlay`, `#modal-title`, `#modal-body`, `#modal-close`, `#add-modal-overlay`, `#add-text`, `#add-submit`, `#add-cancel`.

- [ ] **Step 1: Create `app/static/index.html`**

```html
<!DOCTYPE html>
<html lang="id">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Fiberzone WO Dashboard</title>
<link rel="stylesheet" href="style.css">
</head>
<body>
<header class="topbar">
  <div class="topbar-inner">
    <h1>Fiberzone WO Dashboard</h1>
    <div id="stats-chips" class="chips"></div>
  </div>
  <div id="demo-banner" class="banner demo hidden">Mode Demo — backend belum terhubung. Data contoh lokal.</div>
  <div id="error-banner" class="banner error hidden"></div>
</header>

<nav id="tabs" class="tabs" aria-label="Status WO">
  <button class="tab active" data-status="masuk" id="tab-masuk">Masuk <span class="tab-count"></span></button>
  <button class="tab" data-status="dikerjakan" id="tab-dikerjakan">Dikerjakan <span class="tab-count"></span></button>
  <button class="tab" data-status="menunggu_verifikasi" id="tab-menunggu_verifikasi">Menunggu Verifikasi <span class="tab-count"></span></button>
  <button class="tab" data-status="done" id="tab-done">Done <span class="tab-count"></span></button>
</nav>

<div class="toolbar">
  <input id="search-input" type="search" placeholder="Cari No. WO, nama, alamat, telepon">
  <select id="type-select">
    <option value="all">Semua Tipe</option>
    <option value="P">PSB</option>
    <option value="M">Maintenance</option>
    <option value="T">Troubleshoot</option>
    <option value="D">Dismantle</option>
    <option value="B">Bangun Jaringan</option>
    <option value="S">Survey</option>
  </select>
  <button id="btn-add" class="btn primary">+ Tambah WO</button>
</div>

<main id="cards" class="cards" aria-live="polite"></main>

<div id="toast-container" class="toast-container"></div>

<div id="modal-overlay" class="modal-overlay hidden" role="dialog" aria-modal="true">
  <div class="modal">
    <div class="modal-head">
      <h2 id="modal-title"></h2>
      <button id="modal-close" class="modal-x" aria-label="Tutup">&times;</button>
    </div>
    <div id="modal-body" class="modal-body"></div>
  </div>
</div>

<div id="add-modal-overlay" class="modal-overlay hidden" role="dialog" aria-modal="true">
  <div class="modal">
    <div class="modal-head">
      <h2>Tambah WO (paste pesan)</h2>
      <button id="add-cancel" class="modal-x" aria-label="Tutup">&times;</button>
    </div>
    <div class="modal-body">
      <textarea id="add-text" rows="12" placeholder="Tempel pesan WO dari chat di sini..."></textarea>
      <button id="add-submit" class="btn primary">Simpan</button>
    </div>
  </div>
</div>

<script src="app.js"></script>
</body>
</html>
```

- [ ] **Step 2: Serve and visually verify**

Run: `python3 -m http.server 8600` (from repo root, background). Open `http://127.0.0.1:8600/app/static/` in browser. Expected: header, 4 tab buttons, toolbar (search + select + button), empty `#cards`, no console errors (app.js is missing → only a 404 on the script tag, acceptable this task).

- [ ] **Step 3: Commit**

```bash
git add app/static/index.html
git commit -m "feat(frontend): dashboard page skeleton"
```

---

### Task 2: Dark theme styles (`style.css`)

**Files:**
- Create: `app/static/style.css`

**Interfaces:**
- Consumes: element IDs/classes from Task 1.
- Produces: class names render code must use — `.card`, `.badge` (with modifier `.type-P|M|T|D|B|S`), `.chip`, `.btn` (`.primary`, `.ghost`), `.modal-overlay`, `.modal`, `.modal-body`, `.toast` (`.success`, `.error`), `.banner` (`.demo`, `.error`), `.hidden`, `.empty`, `.mono`, `.field`, `.timestamps`, `.actions`, `.kw` (key-value rows), `.report-list`, `.raw-pre`.

- [ ] **Step 1: Create `app/static/style.css`**

```css
:root {
  --bg: #0f1419;
  --bg-elev: #1a2129;
  --bg-card: #1e2730;
  --border: #2b3642;
  --text: #e6edf3;
  --text-dim: #8b98a5;
  --accent: #2f81f7;
  --green: #2ea043;
  --amber: #d29922;
  --red: #f85149;
  --purple: #bc8cff;
  --cyan: #39c5cf;
  --blue: #58a6ff;
}
* { box-sizing: border-box; }
body {
  margin: 0; background: var(--bg); color: var(--text);
  font: 14px/1.5 system-ui, -apple-system, "Segoe UI", sans-serif;
}
.hidden { display: none !important; }
.mono { font-family: ui-monospace, "Cascadia Code", Consolas, monospace; }

/* header */
.topbar { background: var(--bg-elev); border-bottom: 1px solid var(--border); padding: 12px 16px; }
.topbar-inner { max-width: 1200px; margin: 0 auto; display: flex; align-items: center; justify-content: space-between; gap: 12px; flex-wrap: wrap; }
.topbar h1 { font-size: 18px; margin: 0; }
.chips { display: flex; gap: 8px; flex-wrap: wrap; }
.chip { background: var(--bg-card); border: 1px solid var(--border); border-radius: 999px; padding: 2px 10px; font-size: 12px; color: var(--text-dim); }
.chip.infra { border-color: var(--blue); color: var(--blue); }
.chip strong { color: var(--text); }
.banner { max-width: 1200px; margin: 10px auto 0; border-radius: 6px; padding: 8px 12px; font-size: 13px; }
.banner.demo { background: rgba(210, 153, 34, .12); border: 1px solid var(--amber); color: var(--amber); }
.banner.error { background: rgba(248, 81, 73, .12); border: 1px solid var(--red); color: var(--red); }

/* tabs */
.tabs { max-width: 1200px; margin: 16px auto 0; display: flex; gap: 4px; padding: 0 16px; overflow-x: auto; }
.tab { background: none; border: none; border-bottom: 2px solid transparent; color: var(--text-dim); padding: 8px 14px; cursor: pointer; font-size: 14px; white-space: nowrap; }
.tab.active { color: var(--text); border-bottom-color: var(--accent); }
.tab-count { color: var(--text-dim); font-size: 12px; }

/* toolbar */
.toolbar { max-width: 1200px; margin: 12px auto; display: flex; gap: 8px; padding: 0 16px; flex-wrap: wrap; }
#search-input { flex: 1 1 240px; background: var(--bg-card); border: 1px solid var(--border); border-radius: 6px; color: var(--text); padding: 8px 12px; }
#search-input::placeholder { color: var(--text-dim); }
#type-select { background: var(--bg-card); border: 1px solid var(--border); border-radius: 6px; color: var(--text); padding: 8px; }

/* cards */
.cards { max-width: 1200px; margin: 0 auto; padding: 0 16px 40px; display: grid; grid-template-columns: repeat(auto-fill, minmax(340px, 1fr)); gap: 12px; }
.card { background: var(--bg-card); border: 1px solid var(--border); border-radius: 8px; padding: 14px; cursor: pointer; transition: border-color .15s; }
.card:hover { border-color: var(--accent); }
.card-head { display: flex; align-items: center; gap: 8px; margin-bottom: 8px; }
.card-title { font-weight: 600; font-size: 13px; word-break: break-all; }
.badge { border-radius: 4px; padding: 2px 8px; font-size: 11px; font-weight: 700; color: #0f1419; }
.badge.type-P { background: var(--green); }
.badge.type-M { background: var(--amber); }
.badge.type-T { background: var(--red); color: #fff; }
.badge.type-D { background: var(--purple); }
.badge.type-B { background: var(--cyan); }
.badge.type-S { background: var(--blue); }
.field { margin: 4px 0; }
.kw { display: flex; justify-content: space-between; gap: 10px; margin: 3px 0; font-size: 13px; }
.kw span:first-child { color: var(--text-dim); flex-shrink: 0; }
.kw a { color: var(--blue); word-break: break-all; }
.timestamps { margin-top: 8px; border-top: 1px dashed var(--border); padding-top: 6px; }
.actions { margin-top: 10px; display: flex; gap: 8px; }

/* buttons */
.btn { border: none; border-radius: 6px; padding: 7px 14px; cursor: pointer; font-size: 13px; font-weight: 600; }
.btn.primary { background: var(--accent); color: #fff; }
.btn.primary:hover { filter: brightness(1.1); }
.btn.ghost { background: none; border: 1px solid var(--border); color: var(--text); }
.btn.ghost:hover { border-color: var(--accent); color: var(--accent); }

.empty { grid-column: 1 / -1; text-align: center; color: var(--text-dim); padding: 60px 0; }

/* modal */
.modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,.6); display: flex; align-items: center; justify-content: center; z-index: 100; padding: 16px; }
.modal { background: var(--bg-elev); border: 1px solid var(--border); border-radius: 10px; width: 100%; max-width: 720px; max-height: 85vh; display: flex; flex-direction: column; }
.modal-head { display: flex; align-items: center; justify-content: space-between; padding: 12px 16px; border-bottom: 1px solid var(--border); }
.modal-head h2 { margin: 0; font-size: 16px; }
.modal-x { background: none; border: none; color: var(--text-dim); font-size: 22px; cursor: pointer; }
.modal-x:hover { color: var(--text); }
.modal-body { padding: 16px; overflow-y: auto; }
#add-text { width: 100%; background: var(--bg-card); border: 1px solid var(--border); border-radius: 6px; color: var(--text); padding: 10px; font-family: ui-monospace, Consolas, monospace; font-size: 13px; resize: vertical; margin-bottom: 12px; }

/* report */
.report-list { margin: 4px 0 10px; padding-left: 18px; }
.report-list li { margin: 2px 0; }
.raw-pre { background: #0b0f14; border: 1px solid var(--border); border-radius: 6px; padding: 10px; overflow-x: auto; white-space: pre-wrap; font-size: 12px; font-family: ui-monospace, Consolas, monospace; color: var(--text-dim); max-height: 240px; overflow-y: auto; }
.section-title { font-weight: 700; margin: 14px 0 6px; color: var(--text); }

/* toast */
.toast-container { position: fixed; right: 16px; bottom: 16px; display: flex; flex-direction: column; gap: 8px; z-index: 200; }
.toast { background: var(--bg-elev); border: 1px solid var(--border); border-left: 3px solid var(--green); border-radius: 6px; padding: 10px 14px; font-size: 13px; max-width: 340px; opacity: 0; transform: translateY(8px); transition: opacity .3s, transform .3s; box-shadow: 0 4px 16px rgba(0,0,0,.4); }
.toast.show { opacity: 1; transform: translateY(0); }
.toast.error { border-left-color: var(--red); }

@media (max-width: 640px) {
  .toolbar { flex-direction: column; }
  .cards { grid-template-columns: 1fr; }
  .topbar-inner { flex-direction: column; align-items: flex-start; }
}
```

- [ ] **Step 2: Visual check**

Reload `http://127.0.0.1:8600/app/static/`. Expected: dark background, styled tabs/toolbar/buttons; open modal via devtools (`document.getElementById('modal-overlay').classList.remove('hidden')`) → centered dialog with close button; no visual overflow at 360 px width (devtools device toolbar).

- [ ] **Step 3: Commit**

```bash
git add app/static/style.css
git commit -m "feat(frontend): dark theme styles"
```

### Task 3: Data layer — mode detection, API adapter, mock store (`app.js` part 1)

**Files:**
- Create: `app/static/app.js`

**Interfaces:**
- Consumes: element IDs from Task 1; class names from Task 2.
- Produces (later tasks consume these exact names):
  - `const State = { mode: 'live'|'demo', items: [], tab: 'masuk', type: 'all', q: '', timer: null }`
  - `const STATUS_ORDER = ['masuk', 'dikerjakan', 'menunggu_verifikasi', 'done']`
  - `const NEXT_STATUS = { masuk: 'dikerjakan', dikerjakan: 'menunggu_verifikasi', menunggu_verifikasi: 'done' }`
  - `const TYPE_LABEL = { P: 'PSB', M: 'Maintenance', T: 'Troubleshoot', D: 'Dismantle', B: 'Bangun Jaringan', S: 'Survey' }`
  - `function escapeHTML(s)` → escaped string
  - `async function detectMode()` → `'live'` | `'demo'`
  - `async function fetchList()` → `Array<wo>` (live: `API.list({limit:500})` → items; demo: `[...MOCK_ITEMS]`)
  - `async function transition(id, status)` → `wo` | throws `{detail}`
  - `async function submitRaw(text)` → `{recognized, wo_code, wo}` | `{recognized:false, reason}` | throws
  - `const MOCK_ITEMS` — 10 WO spread across all 4 statuses (3 masuk, 2 dikerjakan, 2 menunggu_verifikasi, 3 done; types P/M/T/D/B/S)
  - `function mockTransition(id, status)`, `function mockAdd(parsed)`, `function parseRawDemo(text)`

- [ ] **Step 1: Write `app/static/app.js` — helpers, API adapter, mode detection**

```js
'use strict';

const STATUS_ORDER = ['masuk', 'dikerjakan', 'menunggu_verifikasi', 'done'];
const NEXT_STATUS = {
  masuk: 'dikerjakan',
  dikerjakan: 'menunggu_verifikasi',
  menunggu_verifikasi: 'done'
};
const TYPE_LABEL = { P: 'PSB', M: 'Maintenance', T: 'Troubleshoot', D: 'Dismantle', B: 'Bangun Jaringan', S: 'Survey' };

const State = { mode: 'demo', items: [], tab: 'masuk', type: 'all', q: '', timer: null };

function escapeHTML(s) {
  return String(s ?? '').replace(/[&<>"']/g,
    c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
}

async function fetchJSON(url, opts) {
  const res = await fetch(url, opts);
  let body = null;
  try { body = await res.json(); } catch (_) { /* non-JSON body */ }
  if (!res.ok) {
    const detail = body && body.detail ? body.detail : `HTTP ${res.status}`;
    const err = new Error(detail);
    err.detail = detail;
    throw err;
  }
  return body;
}

const API = {
  async health() { return fetchJSON('/api/health'); },
  async list(params = {}) {
    const qs = new URLSearchParams(
      Object.entries(params).filter(([, v]) => v !== '' && v != null));
    const body = await fetchJSON(`/api/wo?${qs}`);
    return Array.isArray(body.items) ? body.items : [];
  },
  async transition(id, status) {
    return fetchJSON(`/api/wo/${id}/status`, {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ status })
    });
  },
  async raw(text) {
    return fetchJSON('/api/wo/raw', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text })
    });
  }
};

async function detectMode() {
  const ctrl = new AbortController();
  const t = setTimeout(() => ctrl.abort(), 500);
  try { await API.health(); return 'live'; }
  catch (_) { return 'demo'; }
  finally { clearTimeout(t); }
}
```

- [ ] **Step 2: Add mock store to `app.js` (items 1-5)**

```js
function iso(offsetH) { // ISO timestamp, offsetH hours ago
  return new Date(Date.now() - offsetH * 3600e3).toISOString();
}

const MOCK_ITEMS = [
  { id: 1, wo_code: 'WO/260812/M02/FZ/BL0277', wo_date: '2026-08-12', wo_type: 'M', wo_seq: 2,
    identitas: 'FZ/BL0277', customer_name: 'SITI SAKDEYA',
    address: 'JL.PULAU GALANG, GG. NILAWARSIKI, NO.10, PEMOGAN, DENPASAR SELATAN, KOTA DENPASAR, BALI',
    phone: '0857 0848 6239', package: null, action: 'FO CUT', description: null, segment: null,
    sn_ont: null, username: null, password: null, sharelocation: null,
    assignees: ['@IYOOO00', '@Kyy_YYY'], infra: [], flags: [],
    status: 'masuk', report: null, report_raw: null,
    raw_text: 'WO/260812/M02/FZ/BL0277\nSITI SAKDEYA\nJL.PULAU GALANG, GG. NILAWARSIKI, NO.10, PEMOGAN, DENPASAR SELATAN, KOTA DENPASAR, BALI\n0857 0848 6239\n\nFO CUT\n@IYOOO00 @Kyy_YYY',
    created_at: iso(1), started_at: null, verification_at: null, done_at: null },
  { id: 2, wo_code: 'WO/260812/P02/FZ-ABP-2957_01', wo_date: '2026-08-12', wo_type: 'P', wo_seq: 2,
    identitas: 'FZ-ABP-2957_01', customer_name: 'LILIK KHOLIDA',
    address: 'JL.PULAU GALANG, GG. NILAWARSIKI, NO.154, PEMOGAN, DENPASAR SELATAN, KOTA DENPASAR, BALI',
    phone: '0877 6864 6388', package: 'PSB BASIC 50Mbps', action: null, description: null, segment: null,
    sn_ont: 'ALCLB4436C21', username: 'TBA', password: 'TBA',
    sharelocation: 'https://www.google.com/maps/place/Denpasar',
    assignees: [], infra: ['@IYOOO00', '@bgs_dka'], flags: ['TARIK', 'AKTIVASI'],
    status: 'dikerjakan', report: null, report_raw: null,
    raw_text: 'WO/260812/P02/FZ-ABP-2957_01\nLILIK KHOLIDA\nJL.PULAU GALANG, GG. NILAWARSIKI, NO.154, PEMOGAN, DENPASAR SELATAN, KOTA DENPASAR, BALI\n0877 6864 6388\n\nPSB BASIC 50Mbps\nTARIK\nAKTIVASI\nSN ONT: ALCLB4436C21\nUsername: TBA\nPassword: TBA\nInfra: @IYOOO00 @bgs_dka',
    created_at: iso(5), started_at: iso(4), verification_at: null, done_at: null },
  { id: 3, wo_code: 'WO/260811/M01/FZ-ABQ-2212_01', wo_date: '2026-08-11', wo_type: 'M', wo_seq: 1,
    identitas: 'FZ-ABQ-2212_01', customer_name: 'RUDOLF KASENDA OKI',
    address: 'JL. SUBAK SARI, TIBUBENENG, KEC. KUTA UTARA, KABUPATEN BADUNG, BALI 80361',
    phone: '0813 1539 7698', package: null, action: 'Sambung ulang core di box panel', description: null, segment: null,
    sn_ont: null, username: null, password: null, sharelocation: null,
    assignees: ['@yohanesharlan'], infra: [], flags: [],
    status: 'menunggu_verifikasi', report: null, report_raw: null,
    raw_text: 'WO/260811/M01/FZ-ABQ-2212_01\nRUDOLF KASENDA OKI\nJL. SUBAK SARI, TIBUBENENG, KEC. KUTA UTARA, KABUPATEN BADUNG, BALI 80361\n0813 1539 7698',
    created_at: iso(26), started_at: iso(24), verification_at: iso(2), done_at: null },
  { id: 4, wo_code: 'WO/260803/T01/V-DPS-FDT21-FAT3', wo_date: '2026-08-03', wo_type: 'T', wo_seq: 1,
    identitas: 'V-DPS-FDT21-FAT3', customer_name: 'V-DPS-FDT21-FAT3',
    address: 'JL. NAKULA, GG. JATAYU', phone: null,
    package: null, action: null, description: 'Pengecekan FAT V-DPS-FDT21-FAT3', segment: 'V-DPS-FDT21-FAT3',
    sn_ont: null, username: null, password: null, sharelocation: null,
    assignees: ['@yohanesharlan'], infra: [], flags: [],
    status: 'done', report: {
      status_report: 'Cleared',
      case: ['Cek redaman input dan output'],
      action: ['Cek redaman input dan output'], solution: [],
      report_date: '3 Agustus 2026', pic_teknisi: null, start: null, finish: null,
      pic_pendamping: null, tarik: null, aktivasi: null, meteran: null,
      splitter: null, alat_terpasang: [], splicer: null,
      sn_ont: null, username: null, password: null
    },
    report_raw: 'Report troubleshoot\n\nWO/260803/T01/V-DPS-FDT21-FAT3\nV-DPS-FDT21-FAT3\nJL. NAKULA, GG. JATAYU\n\nPengecekan FAT V-DPS-FDT21-FAT3\n\nCek redaman input dan output\n\nStatus: Cleared',
    raw_text: 'WO/260803/T01/V-DPS-FDT21-FAT3\nV-DPS-FDT21-FAT3\nJL. NAKULA, GG. JATAYU\n\nPengecekan FAT V-DPS-FDT21-FAT3\n\n@yohanesharlan PKL',
    created_at: iso(220), started_at: iso(200), verification_at: iso(30), done_at: iso(29) },
  { id: 5, wo_code: 'WO/260810/P01/FZ-ABP-2957_01', wo_date: '2026-08-10', wo_type: 'P', wo_seq: 1,
    identitas: 'FZ-ABP-2957_01', customer_name: 'LILIK KHOLIDA',
    address: 'JL.PULAU GALANG, GG. NILAWARSIKI, NO.154, PEMOGAN, DENPASAR SELATAN, KOTA DENPASAR, BALI',
    phone: '0877 6864 6388', package: 'PSB BASIC 50Mbps', action: null, description: null, segment: null,
    sn_ont: 'ALCLB4436C21', username: 'TBA', password: 'TBA',
    sharelocation: 'https://www.google.com/maps/place/Denpasar',
    assignees: [], infra: ['@IYOOO00', '@bgs_dka'], flags: ['TARIK', 'AKTIVASI'],
    status: 'done', report: {
      status_report: 'Cleared', case: [], action: [],
      solution: ['Tarik kabel FO 1 Core dari Splitter terdekat Mengarah ke client sepanjang meter',
        'Splicing kabel sisi FAT dan Client'],
      report_date: '11 Agustus 2026', pic_teknisi: 'rifky dan iyo', start: '', finish: '',
      , tarik: 'ok', aktivasi: 'ok',
      meteran: 'Tarikan awal - meter\nMeteran akhir: 0\nTotal tarikan',
      splitter: 'FADPS-FDT10-FAT0\nDPS-FDT10-FAT03\nport 3 1:4',
      alat_terpasang: ['Patchcore Biru 1 Pcs', 'Pigtail Hijau 1 pcs', 'ONT Nokia 1 Pcs',
        'Kabel ties secukupnya', 'Klem kabel secukupnya'],
      splicer: 'Said : Likkho\nPas : Fifiye2170',
      sn_ont: 'ALCLB4436C21', username: 'TBA', password: 'TBA'
    },
    report_raw: 'Repot pasang baru\n\nWO/260810/P01/FZ-ABP-2957_01\nLILIK KHOLIDA\nJL.PULAU GALANG, GG. NILAWARSIKI, NO.154, PEMOGAN, DENPASAR SELATAN, KOTA DENPASAR, BALI\n0877 6864 6388\n\nPSB BASIC 50Mbps\n\nDetail laporan:\nHARI / TANGGAL : 11 Agustus 2026\nPic teknisi : rifky dan iyo\n...\nSolution\nTarik kabel FO 1 Core dari Splitter terdekat Mengarah ke client sepanjang meter\n- Splicing kabel sisi FAT dan Client\n...\nSaid : Likkho\nPas : Fifiye2170\nSN ONT: ALCLB4436C21\nUsername: TBA\nPassword: TBA',
    raw_text: 'WO/260810/P01/FZ-ABP-2957_01\nLILIK KHOLIDA\nJL.PULAU GALANG, GG. NILAWARSIKI, NO.154, PEMOGAN, DENPASAR SELATAN, KOTA DENPASAR, BALI\n0877 6864 6388\n\nPSB BASIC 50Mbps\nTARIK\nAKTIVASI\nSN ONT: ALCLB4436C21\nUsername: TBA\nPassword: TBA\nInfra: @IYOOO00 @bgs_dka\nSharelocation: https://www.google.com/maps/place/Denpasar',
    created_at: iso(50), started_at: iso(48), verification_at: iso(40), done_at: iso(39) },
  { id: 6, wo_code: 'WO/260812/S01/FZ-SRV-001', wo_date: '2026-08-12', wo_type: 'S', wo_seq: 1,
    identitas: 'FZ-SRV-001', customer_name: 'NI LUH PUTU AYU',
    address: 'JL. RAYA KUTA, NO.88, KUTA, BADUNG, BALI', phone: '0812 3456 7890',
    package: null, action: null, description: 'Survey lokasi pemasangan baru', segment: null,
    sn_ont: null, username: null, password: null, sharelocation: null,
    assignees: ['@bgs_dka'], infra: [], flags: [],
    status: 'masuk', report: null, report_raw: null,
    raw_text: 'WO/260812/S01/FZ-SRV-001\nNI LUH PUTU AYU\nJL. RAYA KUTA, NO.88, KUTA, BADUNG, BALI\n0812 3456 7890\n\nSurvey lokasi pemasangan baru\n@bgs_dka',
    created_at: iso(2), started_at: null, verification_at: null, done_at: null },
  { id: 7, wo_code: 'WO/260811/D01/FZ-DMT-012', wo_date: '2026-08-11', wo_type: 'D', wo_seq: 1,
    identitas: 'FZ-DMT-012', customer_name: 'I MADE WIRAWAN',
    address: 'JL. TUKAD BATAN HARI NO.12, DENPASAR', phone: '0819 9999 1111',
    package: null, action: null, description: 'Dismantle perangkat', segment: null,
    sn_ont: 'ALCLB0000001', username: null, password: null, sharelocation: null,
    assignees: ['@IYOOO00'], infra: [], flags: [],
    status: 'dikerjakan', report: null, report_raw: null,
    raw_text: 'WO/260811/D01/FZ-DMT-012\nI MADE WIRAWAN\nJL. TUKAD BATAN HARI NO.12, DENPASAR\n0819 9999 1111\n\nDismantle perangkat\n@IYOOO00',
    created_at: iso(20), started_at: iso(18), verification_at: null, done_at: null },
  { id: 8, wo_code: 'WO/260810/B01/FZ-BGN-009', wo_date: '2026-08-10', wo_type: 'B', wo_seq: 1,
    identitas: 'FZ-BGN-009', customer_name: 'KOMPLEK PERUM GRIYA PERMAI',
    address: 'JL. PULAU SERANGAN GG.5, DENPASAR SELATAN', phone: null,
    package: null, action: null, description: 'Bangun jaringan ODP baru', segment: null,
    sn_ont: null, username: null, password: null, sharelocation: null,
    assignees: ['@bgs_dka', '@IYOOO00'], infra: [], flags: [],
    status: 'menunggu_verifikasi', report: null, report_raw: null,
    raw_text: 'WO/260810/B01/FZ-BGN-009\nKOMPLEK PERUM GRIYA PERMAI\nJL. PULAU SERANGAN GG.5, DENPASAR SELATAN\n\nBangun jaringan ODP baru\n@bgs_dka @IYOOO00',
    created_at: iso(30), started_at: iso(28), verification_at: iso(3), done_at: null },
  { id: 9, wo_code: 'WO/260809/M03/FZ/BL0277', wo_date: '2026-08-09', wo_type: 'M', wo_seq: 3,
    identitas: 'FZ/BL0277', customer_name: 'KADEK SUMERTA',
    address: 'JL. PULAU GALANG GG. NILAWARSIKI NO.22, PEMOGAN, DENPASAR SELATAN', phone: '0838 7777 2222',
    package: null, action: 'Cek FO CUT', description: null, segment: null,
    sn_ont: null, username: null, password: null, sharelocation: null,
    assignees: ['@Kyy_YYY'], infra: [], flags: [],
    status: 'done', report: {
      status_report: 'Cleared', case: ['FO cut di kabel drop'], action: ['Splicing ulang konektor'],
      solution: ['Splicing ulang di sisi client', 'Test speed 50 Mbps OK'],
      report_date: '9 Agustus 2026', pic_teknisi: 'iyo', start: '09:00', finish: '11:30',
      pic_pendamping: null, tarik: null, aktivasi: null, meteran: null,
      splitter: null, alat_terpasang: [], splicer: null, sn_ont: null, username: null, password: null
    },
    report_raw: 'Report Maintenance\n\nWO/260809/M03/FZ/BL0277\nKADEK SUMERTA\nJL. PULAU GALANG GG. NILAWARSIKI NO.22, PEMOGAN, DENPASAR SELATAN\n0838 7777 2222\n\nCase :\n- FO cut di kabel drop\n\nAction :\n- Splicing ulang konektor\n\nStatus : Cleared',
    raw_text: 'WO/260809/M03/FZ/BL0277\nKADEK SUMERTA\nJL. PULAU GALANG GG. NILAWARSIKI NO.22, PEMOGAN, DENPASAR SELATAN\n0838 7777 2222\n\nCek FO CUT\n@Kyy_YYY',
    created_at: iso(76), started_at: iso(74), verification_at: iso(50), done_at: iso(49) },
  { id: 10, wo_code: 'WO/260812/M03/FZ/BL0301', wo_date: '2026-08-12', wo_type: 'M', wo_seq: 3,
    identitas: 'FZ/BL0301', customer_name: 'GEDE ARTAWA',
    address: 'JL. PULAU GALANG GG. NILAWARSIKI NO.45, PEMOGAN, DENPASAR SELATAN', phone: '0857 1111 4444',
    package: null, action: 'FO CUT', description: null, segment: null,
    sn_ont: null, username: null, password: null, sharelocation: null,
    assignees: ['@IYOOO00'], infra: [], flags: [],
    status: 'masuk', report: null, report_raw: null,
    raw_text: 'WO/260812/M03/FZ/BL0301\nGEDE ARTAWA\nJL. PULAU GALANG GG. NILAWARSIKI NO.45, PEMOGAN, DENPASAR SELATAN\n0857 1111 4444\n\nFO CUT\n@IYOOO00',
    created_at: iso(0.5), started_at: null, verification_at: null, done_at: null }
];

function mockTransition(id, status) {
  const wo = MOCK_ITEMS.find(w => w.id === id);
  if (!wo) throw Object.assign(new Error('WO tidak ditemukan'), { detail: 'WO tidak ditemukan' });
  const valid = STATUS_ORDER.indexOf(wo.status) < STATUS_ORDER.indexOf(status);
  if (!valid) {
    throw Object.assign(new Error(`transisi tidak valid: ${wo.status} -> ${status}`), { detail: `transisi tidak valid: ${wo.status} -> ${status}` });
  }
  wo.status = status;
  const now = new Date().toISOString();
  if (status === 'dikerjakan') wo.started_at = now;
  if (status === 'menunggu_verifikasi') wo.verification_at = now;
  if (status === 'done') wo.done_at = now;
  return wo;
}

function mockAdd(parsed) {
  const nextId = Math.max(...MOCK_ITEMS.map(w => w.id)) + 1;
  const wo = { id: nextId, wo_code: parsed.wo_code, wo_date: parsed.wo_date || null,
    wo_type: parsed.wo_type, wo_seq: parsed.wo_seq || null, identitas: parsed.identitas || null,
    customer_name: parsed.customer_name, address: parsed.address, phone: parsed.phone,
    package: parsed.package || null, action: parsed.action || null, description: parsed.description || null,
    segment: parsed.segment || null, sn_ont: null, username: null, password: null, sharelocation: null,
    assignees: parsed.assignees || [], infra: [], flags: [],
    status: 'masuk', report: null, report_raw: null, raw_text: parsed.raw_text || null,
    created_at: new Date().toISOString(), started_at: null, verification_at: null, done_at: null };
  MOCK_ITEMS.unshift(wo);
  return wo;
}

function parseRawDemo(text) {
  const lines = text.split(/\r?\n/).map(l => l.trim()).filter(Boolean);
  const m = lines[0] && lines[0].match(/^WO\/(\d{2})(\d{2})(\d{2})\/([A-Z])(\d+)\/(.+)$/);
  if (!m) return { recognized: false, reason: 'Baris pertama bukan format WO/YYMMDD/TYPE...' };
  return { recognized: true, wo_code: lines[0],
    wo_date: `20${m[1]}-${m[2]}-${m[3]}`, wo_type: m[4], wo_seq: parseInt(m[5], 10), identitas: m[6],
    customer_name: lines[1] || null, address: lines[2] || null, phone: lines[3] || null,
    description: lines.slice(4).filter(l => !l.startsWith('@')).join('\n') || null,
    assignees: lines.flatMap(l => l.match(/@\S+/g) || []), raw_text: text };
}
```

- [ ] **Step 3: Wire boot-level data functions**

```js
async function fetchList() {
  if (State.mode === 'live') return API.list({ limit: 500 });
  return [...MOCK_ITEMS];
}

async function transition(id, status) {
  if (State.mode === 'live') return API.transition(id, status);
  return mockTransition(id, status);
}

async function submitRaw(text) {
  if (State.mode === 'live') return API.raw(text);
  const parsed = parseRawDemo(text);
  if (!parsed.recognized) return parsed;
  const wo = mockAdd(parsed);
  return { recognized: true, wo_code: wo.wo_code, wo };
}
```

- [ ] **Step 4: Verify in console**

Reload page. In devtools console run: `State.mode`, `fetchList().then(x => console.log(x.length))`, `mockTransition(1, 'dikerjakan')`. Expected: `mode === 'demo'` (no backend), `fetchList()` resolves 10 items, transition sets item 1 status `dikerjakan` + `started_at` set. No console errors.

- [ ] **Step 5: Commit**

```bash
git add app/static/app.js
git commit -m "feat(frontend): data layer with demo mode + mock store"
```

---

### Task 4: Render — chips, tabs, cards (`app.js` part 2)

**Files:**
- Modify: `app/static/app.js`

**Interfaces:**
- Consumes: `State`, `escapeHTML`, `fetchList`, `TYPE_LABEL` from Task 3; DOM ids from Task 1.
- Produces: `renderAll()`, `renderCounts(items)`, `renderCards(items)`, `cardHTML(wo)`, `timestampLabel(iso)`, `fieldRow(label, value, mono)`, `listChips(arr, cls)`, `actionButton(wo)`, `boot()`.

- [ ] **Step 1: Add render helpers + card builder**

```js
const $ = id => document.getElementById(id);
const MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'Mei', 'Jun', 'Jul', 'Agu', 'Sep', 'Okt', 'Nov', 'Des'];

function timestampLabel(iso) {
  if (!iso) return null;
  const d = new Date(iso);
  if (isNaN(d)) return null;
  return `${d.getDate()} ${MONTHS[d.getMonth()]} ${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`;
}

function fieldRow(label, value, mono = false) {
  if (value == null || value === '') return '';
  const cls = mono ? ' class="mono"' : '';
  return `<div class="kw"><span>${escapeHTML(label)}</span><span${cls}>${escapeHTML(value)}</span></div>`;
}

function listChips(arr, cls = 'chip') {
  return (arr || []).map(x => `<span class="${cls}">${escapeHTML(x)}</span>`).join('');
}

function actionButton(wo) {
  if (wo.status === 'done') {
    return `<button class="btn ghost" data-action="report" data-id="${wo.id}">Lihat Report</button>`;
  }
  const next = NEXT_STATUS[wo.status];
  const label = { dikerjakan: 'Mulai', menunggu_verifikasi: 'Minta Verifikasi', done: 'Selesai' }[next] || 'Lanjut';
  return `<button class="btn primary" data-action="transition" data-id="${wo.id}" data-status="${next}">${label}</button>`;
}

function cardHTML(wo) {
  const type = TYPE_LABEL[wo.wo_type] || wo.wo_type;
  const ts = (lbl, s) => {
    const l = timestampLabel(s);
    return l ? `<div class="kw"><span>${lbl}</span><span>${l}</span></div>` : '';
  };
  const info = listChips(wo.assignees) + (wo.infra.length ? listChips(wo.infra, 'chip infra') : '');
  return `<article class="card" data-id="${wo.id}">
    <div class="card-head">
      <span class="badge type-${escapeHTML(wo.wo_type)}">${escapeHTML(type)}</span>
      <span class="card-title mono">${escapeHTML(wo.wo_code)}</span>
    </div>
    <div class="field"><strong>${escapeHTML(wo.customer_name || '—')}</strong></div>
    ${fieldRow('Alamat', wo.address)}
    ${fieldRow('Telepon', wo.phone, true)}
    ${fieldRow('Paket', wo.package)}
    ${fieldRow('Aksi', wo.action)}
    ${fieldRow('Segmen', wo.segment)}
    ${fieldRow('Deskripsi', wo.description)}
    ${fieldRow('SN ONT', wo.sn_ont, true)}
    ${fieldRow('Username', wo.username, true)}
    ${fieldRow('Password', wo.password, true)}
    ${wo.sharelocation ? `<div class="kw"><span>Lokasi</span><a href="${escapeHTML(wo.sharelocation)}" target="_blank" rel="noopener">${escapeHTML(wo.sharelocation)}</a></div>` : ''}
    ${info ? `<div class="chips">${info}</div>` : ''}
    <div class="timestamps">${ts('Mulai', wo.started_at)}${ts('Verifikasi', wo.verification_at)}${ts('Selesai', wo.done_at)}</div>
    <div class="actions">${actionButton(wo)}</div>
  </article>`;
}
```

- [ ] **Step 2: Add counts, cards render, empty state**

```js
function renderCounts(items) {
  const counts = { masuk: 0, dikerjakan: 0, menunggu_verifikasi: 0, done: 0 };
  for (const w of items) if (counts[w.status] !== undefined) counts[w.status]++;
  const labels = { masuk: 'Masuk', dikerjakan: 'Dikerjakan', menunggu_verifikasi: 'Menunggu Verifikasi', done: 'Done' };
  $('stats-chips').innerHTML = STATUS_ORDER.map(s =>
    `<span class="chip">${labels[s]}: <strong>${counts[s]}</strong></span>`).join('');
  document.querySelectorAll('#tabs .tab-count').forEach(el => {
    const st = el.closest('.tab').dataset.status;
    el.textContent = `(${counts[st] ?? 0})`;
  });
}

function filteredItems(items) {
  const q = State.q.trim().toLowerCase();
  return items.filter(w => {
    if (w.status !== State.tab) return false;
    if (State.type !== 'all' && w.wo_type !== State.type) return false;
    if (!q) return true;
    return [w.wo_code, w.customer_name, w.address, w.phone]
      .some(v => v && String(v).toLowerCase().includes(q));
  });
}

function renderCards(items) {
  const list = filteredItems(items);
  const cards = $('cards');
  cards.innerHTML = list.length
    ? list.map(cardHTML).join('')
    : `<div class="empty">Belum ada WO di tab ini.</div>`;
}
```

- [ ] **Step 3: Add `renderAll` and boot**

```js
async function renderAll() {
  try {
    State.items = await fetchList();
    renderCounts(State.items);
    renderCards(State.items);
    const err = $('error-banner');
    if (!err.classList.contains('hidden')) err.classList.add('hidden');
  } catch (err) {
    const banner = $('error-banner');
    banner.textContent = `Gagal ambil data: ${err.detail || err.message}`;
    banner.classList.remove('hidden');
  }
}

async function boot() {
  State.mode = await detectMode();
  if (State.mode === 'demo') $('demo-banner').classList.remove('hidden');
  await renderAll();
  if (State.mode === 'live') State.timer = setInterval(renderAll, 30000);
}

boot();
```

- [ ] **Step 4: Verify in browser**

Reload. Expected: demo banner visible; chips `Masuk: 3 Dikerjakan: 2 Menunggu Verifikasi: 2 Done: 3`; tab counts match; tab Masuk shows 3 cards (SITI SAKDEYA, NI LUH PUTU AYU, GEDE ARTAWA) with badges M/S/M, monospace codes, addresses, phones, "Mulai" buttons. No console errors.

- [ ] **Step 5: Commit**

```bash
git add app/static/app.js
git commit -m "feat(frontend): render stats, tabs, cards"
```

---

### Task 5: Interactions — tabs, search, filter, transitions, toast (`app.js` part 3)

**Files:**
- Modify: `app/static/app.js`, `app/static/style.css` (toast transition)

**Interfaces:**
- Consumes: `renderAll`, `renderCounts`, `renderCards`, `transition`, `submitRaw`, `State` from Tasks 3-4; DOM ids from Task 1.
- Produces: `showToast(msg, type)`, `switchTab(status)`, `bindEvents()`.

- [ ] **Step 1: Add toast + event binding**

```js
function showToast(msg, type = 'success') {
  const el = document.createElement('div');
  el.className = `toast ${type}`;
  el.textContent = msg;
  $('toast-container').appendChild(el);
  setTimeout(() => el.classList.add('show'), 10);
  setTimeout(() => {
    el.classList.remove('show');
    setTimeout(() => el.remove(), 300);
  }, 3000);
}

function switchTab(status) {
  State.tab = status;
  document.querySelectorAll('#tabs .tab').forEach(t =>
    t.classList.toggle('active', t.dataset.status === status));
  renderCards(State.items);
}

function bindEvents() {
  document.querySelectorAll('#tabs .tab').forEach(t =>
    t.addEventListener('click', () => switchTab(t.dataset.status)));
  $('search-input').addEventListener('input', () => {
    State.q = $('search-input').value;
    renderCards(State.items);
  });
  $('type-select').addEventListener('change', () => {
    State.type = $('type-select').value;
    renderCards(State.items);
  });
  $('cards').addEventListener('click', async (e) => {
    const btn = e.target.closest('button[data-action]');
    if (!btn) return;
    const id = Number(btn.dataset.id);
    if (btn.dataset.action === 'transition') {
      try {
        await transition(id, btn.dataset.status);
        showToast(`WO ${id} → ${btn.dataset.status}`);
        await renderAll();
      } catch (err) {
        showToast(err.detail || err.message, 'error');
      }
    }
  });
  $('modal-close').addEventListener('click', () => $('modal-overlay').classList.add('hidden'));
  $('modal-overlay').addEventListener('click', (e) => {
    if (e.target === $('modal-overlay')) $('modal-overlay').classList.add('hidden');
  });
  $('add-modal-overlay').addEventListener('click', (e) => {
    if (e.target === $('add-modal-overlay')) $('add-modal-overlay').classList.add('hidden');
  });
  $('btn-add').addEventListener('click', () => $('add-modal-overlay').classList.remove('hidden'));
  $('add-cancel').addEventListener('click', () => $('add-modal-overlay').classList.add('hidden'));
  $('add-submit').addEventListener('click', async () => {
    const text = $('add-text').value.trim();
    if (!text) { showToast('Teks kosong', 'error'); return; }
    try {
      const res = await submitRaw(text);
      if (!res.recognized) { showToast(`Tidak dikenali: ${res.reason || ''}`, 'error'); return; }
      showToast(`WO ${res.wo_code} tersimpan`);
      $('add-text').value = '';
      $('add-modal-overlay').classList.add('hidden');
      switchTab('masuk');
      await renderAll();
    } catch (err) {
      showToast(err.detail || err.message, 'error');
    }
  });
}
```

- [ ] **Step 2: Wire `bindEvents()` into boot + toast CSS transition**

In `app.js` `boot()`: add `bindEvents();` before `await renderAll();`. Append to `style.css` (`.toast` already has `transition` from Task 2 — verify; add `.show` rule if missing):

```css
.toast.show { opacity: 1; transform: translateY(0); }
```

- [ ] **Step 3: Verify interactions in browser**

Reload. Expected:
- Click tab "Dikerjakan" → 2 cards (LILIK KHOLIDA P, I MADE WIRAWAN D) with button "Minta Verifikasi".
- Search "siti" on Masuk tab → only SITI SAKDEYA card.
- Type filter P on Dikerjakan → only LILIK KHOLIDA.
- Click "Mulai" on SITI SAKDEYA → toast success, card disappears from Masuk, Dikerjakan count becomes 3, `started_at` set (verify by switching to Dikerjakan tab — card shows "Mulai" timestamp).
- Clear search + type=all; tab Done → 3 cards; click "Lihat Report" → nothing yet (Task 6 wires it), no console errors.
- "+ Tambah WO" → modal opens; paste `WO/260812/M99/FZ/TEST-1\nBUDI SANTOSO\nJL. MERPATI NO.1, DENPASAR\n0812 0000 0000\n\nCek kabel\n@IYOOO00` → Simpan → toast, modal closes, Masuk tab shows BUDI SANTOSO (4 cards).

- [ ] **Step 4: Commit**

```bash
git add app/static/app.js app/static/style.css
git commit -m "feat(frontend): tabs, search, filter, transitions, toast"
```

---

### Task 6: Modals — detail & report (`app.js` part 4)

**Files:**
- Modify: `app/static/app.js`

**Interfaces:**
- Consumes: `State`, `escapeHTML`, `fieldRow`, `listChips`, `timestampLabel`, `$`, `TYPE_LABEL` from Tasks 3-4.
- Produces: `modalHTML(wo, showRaw)`, `reportHTML(wo)`, `openDetail(id)`, `openReport(id)`.

- [ ] **Step 1: Add modal render functions**

```js
function modalHTML(wo, showRaw) {
  const rows = [
    ['No. WO', wo.wo_code], ['Tanggal', wo.wo_date], ['Tipe', TYPE_LABEL[wo.wo_type] || wo.wo_type],
    ['Identitas', wo.identitas], ['Nama', wo.customer_name], ['Alamat', wo.address],
    ['Telepon', wo.phone], ['Paket', wo.package], ['Aksi', wo.action], ['Deskripsi', wo.description],
    ['Segmen', wo.segment], ['SN ONT', wo.sn_ont], ['Username', wo.username], ['Password', wo.password]
  ];
  const mono = ['No. WO', 'Telepon', 'SN ONT', 'Username', 'Password'];
  const body = rows.map(([l, v]) => fieldRow(l, v, mono.includes(l))).join('');
  const chips = listChips(wo.assignees) + (wo.infra.length ? listChips(wo.infra, 'chip infra') : '');
  const loc = wo.sharelocation
    ? `<div class="kw"><span>Lokasi</span><a href="${escapeHTML(wo.sharelocation)}" target="_blank" rel="noopener">${escapeHTML(wo.sharelocation)}</a></div>` : '';
  const ts = ['created_at', 'started_at', 'verification_at', 'done_at']
    .map(k => fieldRow(k.replace('_at', ''), timestampLabel(wo[k])))
    .join('');
  const raw = showRaw && wo.raw_text ? `<div class="section-title">Teks asli</div><pre class="raw-pre">${escapeHTML(wo.raw_text)}</pre>` : '';
  return body + chips + loc + `<div class="timestamps">${ts}</div>` + raw;
}

function reportHTML(wo) {
  const r = wo.report || {};
  const list = (label, arr) => (arr && arr.length
    ? `<div class="section-title">${label}</div><ul class="report-list">${arr.map(x => `<li>${escapeHTML(x)}</li>`).join('')}</ul>` : '');
  const kv = (label, v) => fieldRow(label, v);
  return `<div class="kw"><span>Status Report</span><span><span class="badge type-M">${escapeHTML(r.status_report || '—')}</span></span></div>`
    + kv('Tanggal Laporan', r.report_date)
    + list('Case', r.case)
    + list('Action', r.action)
    + list('Solution', r.solution)
    + kv('PIC Teknisi', r.pic_teknisi)
    + kv('Start', r.start) + kv('Finish', r.finish)
    + kv('PIC Pendamping', r.pic_pendamping)
    + kv('Tarik', r.tarik) + kv('Aktivasi', r.aktivasi)
    + kv('Meteran', r.meteran)
    + kv('Splitter', r.splitter)
    + list('Alat Terpasang', r.alat_terpasang)
    + kv('Splicer', r.splicer)
    + kv('SN ONT', r.sn_ont) + kv('Username', r.username) + kv('Password', r.password)
    + (wo.report_raw ? `<div class="section-title">Report mentah</div><pre class="raw-pre">${escapeHTML(wo.report_raw)}</pre>` : '');
}

function openDetail(id) {
  const wo = State.items.find(w => w.id === id);
  if (!wo) return;
  $('modal-title').textContent = `Detail WO — ${wo.wo_code}`;
  $('modal-body').innerHTML = modalHTML(wo, true);
  $('modal-overlay').classList.remove('hidden');
}

function openReport(id) {
  const wo = State.items.find(w => w.id === id);
  if (!wo) return;
  $('modal-title').textContent = `Report — ${wo.wo_code}`;
  $('modal-body').innerHTML = reportHTML(wo);
  $('modal-overlay').classList.remove('hidden');
}
```

- [ ] **Step 2: Wire report/detail into the cards click handler**

In `bindEvents()`, replace the `$('cards')` click listener with:

```js
  $('cards').addEventListener('click', async (e) => {
    const btn = e.target.closest('button[data-action]');
    if (btn) {
      const id = Number(btn.dataset.id);
      if (btn.dataset.action === 'transition') {
        try {
          await transition(id, btn.dataset.status);
          showToast(`WO ${id} → ${btn.dataset.status}`);
          await renderAll();
        } catch (err) {
          showToast(err.detail || err.message, 'error');
        }
        return;
      }
      if (btn.dataset.action === 'report') { openReport(id); return; }
    }
    const card = e.target.closest('.card');
    if (card && !e.target.closest('a')) openDetail(Number(card.dataset.id));
  });
```

- [ ] **Step 3: Verify in browser**

Reload. Expected:
- Tab Done → click "Lihat Report" on KADEK SUMERTA (M) → modal title "Report — WO/260809/M03/FZ/BL0277", body shows Status Report Cleared, Case/Action/Solution lists, report mentah `<pre>` at bottom.
- Click "Lihat Report" on LILIK KHOLIDA (P) → Alat Terpasang list, Splitter, Splicer, PIC shown.
- Close via &times; and via backdrop click.
- Click card body (not button/link) on Masuk tab → Detail WO modal with all fields + "Teks asli" pre.
- Click Sharelocation link opens in new tab (no modal).
- No console errors.

- [ ] **Step 4: Commit**

```bash
git add app/static/app.js
git commit -m "feat(frontend): detail & report modals"
```

---

### Task 7: Final verification (spec §8 checklist)

**Files:**
- Verify: `app/static/index.html`, `app/static/style.css`, `app/static/app.js`

- [ ] **Step 1: Serve fresh and run full checklist in browser**

Run: `python3 -m http.server 8600` (repo root, background). Open `http://127.0.0.1:8600/app/static/` and verify ALL of:
1. Demo banner visible; chips Masuk: 3, Dikerjakan: 2, Menunggu Verifikasi: 2, Done: 3; tab counts match.
2. Tab Masuk → 3 cards; search "siti" → 1 card; clear; filter tipe M → 2 cards (SITI SAKDEYA, GEDE ARTAWA); type all.
3. Transitions: Masuk→Mulai on GEDE ARTAWA → toast + moves to Dikerjakan; Dikerjakan→Minta Verifikasi → moves; Menunggu Verifikasi→Selesai → moves to Done; each shows timestamp.
4. Tab Done → "Lihat Report" opens report modal with Case/Action/Solution/alat/splitter/raw; close via &times; and backdrop.
5. "+ Tambah WO" → paste text from PRD §6.2 (with `WO/260812/...` first line) → toast + appears in Masuk; paste garbage text → error toast "Tidak dikenali".
6. Responsive: devtools 360 px width — toolbar wraps, cards full width, no horizontal scroll.
7. Console: zero errors; `State.mode === 'demo'`.

- [ ] **Step 2: Update project tracking docs**

Update `BACKLOG.md`: mark T-019–T-027 status "Frontend selesai (mode demo + live); menunggu backend untuk integrasi" — keep rows, change Status column to ✅ Done. Update `ROADMAP.md` Phase 2 progress summary (frontend tasks complete, integration pending). Update `DEVLOG.md` with a "Fase 2 — Frontend" entry listing files and commits.

- [ ] **Step 3: Commit**

```bash
git add BACKLOG.md ROADMAP.md DEVLOG.md
git commit -m "docs: update roadmap/backlog/devlog — frontend phase complete"
```

---

## Self-Review Notes (from writing-plans skill)

- **Spec coverage:** §5 header/chips ✅ Task 4; tabs ✅ Task 4; toolbar search/filter ✅ Task 5; kartu field kontekstual ✅ Task 4; modal detail/report ✅ Task 6; toast ✅ Task 5; polling 30s ✅ Task 4 boot; demo mode ✅ Task 3; modal tambah WO ✅ Task 5; responsive + verifikasi ✅ Task 7. §4 contract dipakai verbatim di Task 3 `API` adapter.
- **Placeholder scan:** no TBD/TODO; every code step has full code; verification steps concrete.
- **Type consistency:** `State`, `renderAll`, `renderCards(State.items)`, `fetchList`, `transition(id, status)`, `submitRaw(text)`, `openDetail/openReport(id)` signatures consistent across tasks; mock items use same field names as spec §4 (snake_case).

