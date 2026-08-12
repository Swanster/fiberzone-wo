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
      pic_pendamping: 'ybs', tarik: 'ok', aktivasi: 'ok',
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

/* ---------- render ---------- */

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

/* ---------- interactions ---------- */

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

/* ---------- modals ---------- */

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

/* ---------- boot ---------- */

async function boot() {
  State.mode = await detectMode();
  if (State.mode === 'demo') $('demo-banner').classList.remove('hidden');
  bindEvents();
  await renderAll();
  if (State.mode === 'live') State.timer = setInterval(renderAll, 30000);
}

boot();
