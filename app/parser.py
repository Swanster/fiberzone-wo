"""Parser pesan WO & report Fiberzone (PRD §6, §7, §9.3)."""

from __future__ import annotations

import re
from datetime import datetime

REPORT_KEYWORDS = (
    "report maintenance", "repot maintenance", "repot pasang baru",
    "report pasang baru", "report troubleshoot", "repot troubleshoot",
    "report dismantle", "repot dismantle",
    "report bangun jaringan", "repot bangun jaringan",
    "report survey", "repot survey", "report surfey", "repot surfey",
    "report pemeliharaan", "repot pemeliharaan",
    "laporan selesai",
)
WO_CODE_RE = re.compile(r"^WO/(\d{6})/([A-Z])(\d+)(?:/(.*))?$")
INVISIBLE_RE = re.compile(r"[\u200e\u200f\u200b\ufeff]")
BULLET_RE = re.compile(r"^[-–•‣]\s*(.*)$")
KEYVALUE_RE = re.compile(r"^([A-Za-z\s/\.]+?)\s*:\s*(.*)$")

TYPE_LABEL = {"P": "PSB", "M": "Maintenance", "T": "Troubleshoot",
              "D": "Dismantle", "B": "Bangun Jaringan", "S": "Survey"}


def _clean_lines(text: str) -> list[str]:
    return [INVISIBLE_RE.sub("", ln).strip() for ln in text.splitlines()]


def parse_wo_code(wo_code: str) -> dict | None:
    m = WO_CODE_RE.match(wo_code.strip())
    if not m:
        return None
    try:
        date = datetime(2000 + int(m.group(1)[:2]), int(m.group(1)[2:4]), int(m.group(1)[4:6]))
    except ValueError:
        return None
    return {"wo_date": date.strftime("%Y-%m-%d"),
            "wo_type": m.group(2), "wo_seq": int(m.group(3)), "identitas": (m.group(4) or "").strip() or None}


def _is_report(text_lines: list[str]) -> bool:
    first = next((ln.lower() for ln in text_lines if ln), "")
    return any(kw in first for kw in REPORT_KEYWORDS)


def parse_raw(text: str) -> dict:
    """Entry point: teks mentah → dict {recognized, kind, ...} tanpa crash."""
    lines = [ln for ln in _clean_lines(text) if ln]
    if not lines:
        return {"recognized": False, "reason": "Teks kosong"}
    if _is_report(lines):
        return parse_report(text)
    if lines[0].startswith("WO/"):
        return parse_wo(text)
    return {"recognized": False, "reason": "Format tidak dikenal"}


def parse_wo(text: str) -> dict:
    lines = [ln for ln in _clean_lines(text) if ln]
    head = parse_wo_code(lines[0])
    if not head:
        return {"recognized": False, "reason": "Baris pertama bukan format WO/YYMMDD/TYPE..."}

    customer_name = lines[1] if len(lines) > 1 else None
    address = lines[2] if len(lines) > 2 else None
    phone = lines[3] if len(lines) > 3 and re.match(r"^[0-9+\s\-()]{6,}$", lines[3]) else None
    start = 4 if phone else (3 if len(lines) > 3 else 2)
    body = lines[start:]

    assignees = [w for ln in body for w in re.findall(r"@\S+", ln)
                 if not re.match(r"@[-\d.,]", w)]
    infra, sharelocation, content = [], None, []
    for ln in body:
        low = ln.lower()
        if low.startswith("infra"):
            infra = re.findall(r"@\S+", ln)
        elif low.startswith("sharelocation"):
            sharelocation = ln.split(":", 1)[1].strip() if ":" in ln else None
        else:
            content.append(ln)

    wo = {"wo_code": lines[0], **head, "customer_name": customer_name, "address": address,
          "phone": phone, "assignees": assignees, "infra": infra,
          "sharelocation": sharelocation, "raw_text": text}

    t = head["wo_type"]
    if t == "P":
        wo["flags"] = [ln.split()[0].upper() for ln in content
                       if ln.upper().startswith(("TARIK", "AKTIVASI"))]
        for ln in content:
            low = ln.lower()
            if low.startswith("sn ont"):
                wo["sn_ont"] = ln.split(":", 1)[1].strip()
            elif low.startswith("username"):
                wo["username"] = ln.split(":", 1)[1].strip()
            elif low.startswith("password"):
                wo["password"] = ln.split(":", 1)[1].strip()
        wo["package"] = next((ln for ln in content
                              if not ln.startswith("@")
                              and not ln.upper().startswith(("TARIK", "AKTIVASI"))
                              and not low_key(ln)), None)
    elif t == "M":
        wo["action"] = next((ln for ln in content if not ln.startswith("@")), None)
    elif t == "T":
        wo["segment"] = lines[1] if len(lines) > 1 else None
        wo["description"] = next((ln for ln in content if not ln.startswith("@")), None)
    else:  # D, B, S — field generik
        wo["description"] = next((ln for ln in content if not ln.startswith("@")), None)
    return {"recognized": True, "kind": "wo", "wo": wo}


def low_key(ln: str) -> bool:
    low = ln.lower()
    return low.startswith(("sn ont", "username", "password", "sharelocation", "infra"))


def _report_section(line: str) -> str | None:
    l = line.lower()
    if re.match(r"^case\s*:", l):
        return "case"
    if re.match(r"^action\s*:", l):
        return "action"
    if re.match(r"^(solusi|solution)\s*:?\s*$", l) or re.match(r"^(solusi|solution)\s*:", l):
        return "solution"
    if re.match(r"^(alat yang terpasang|perangkat yang di ?ambil)\s*:?", l):
        return "alat"
    if re.match(r"^soliter\s*/?", l) or l.startswith("splitter"):
        return "splitter"
    if re.match(r"^(said|pas)\s*:", l):
        return "splicer"
    return None


def parse_report(text: str) -> dict:
    lines = [ln for ln in _clean_lines(text) if ln]
    wo_code = next((ln for ln in lines if WO_CODE_RE.match(ln)), None)
    if not wo_code:
        return {"recognized": False, "reason": "Tidak ada baris WO/... di teks"}

    r = {"status_report": None, "case": [], "action": [], "solution": [],
         "alat_terpasang": [], "pic_teknisi": None, "report_date": None,
         "start": None, "finish": None, "pic_pendamping": None, "tarik": None,
         "aktivasi": None, "meteran": None, "splitter": None, "splicer": None,
         "segmen": None, "description": None, "sn_ont": None, "username": None,
         "password": None, "extra": {}}
    section = None

    for raw in lines:
        if raw.startswith("WO/"):
            continue
        m = KEYVALUE_RE.match(raw)
        if m:
            k = m.group(1).strip().lower()
            v = m.group(2).strip()
            if re.match(r"^status", k):
                r["status_report"] = v or None; continue
            if re.match(r"^hari|tanggal", k):
                r["report_date"] = v or None; continue
            if re.match(r"^pic teknisi", k):
                r["pic_teknisi"] = v or None; continue
            if "damping" in k:
                r["pic_pendamping"] = v or None; continue
            if k == "start":
                r["start"] = v or None; continue
            if k == "finish":
                r["finish"] = v or None; continue
            if k == "tarik":
                r["tarik"] = v or None; continue
            if k == "aktivasi":
                r["aktivasi"] = v or None; continue
            if re.match(r"^meteran akhir|^total tarikan", k):
                r["meteran"] = ((r["meteran"] or "") + "\n" + m.group(1).strip()
                                + (": " + v if v else " :")).strip()
                continue
            if re.match(r"^sn ont", k):
                r["sn_ont"] = v or None; continue
            if re.match(r"^segmen", k):
                r["segmen"] = v or None; continue
            if re.match(r"^description", k):
                r["description"] = v or None; continue
            if k == "username":
                r["username"] = v or None; continue
            if k == "password":
                r["password"] = v or None; continue
            if re.match(r"^(said|pas)$", k):
                r["splicer"] = ((r["splicer"] or "") + "\n" + m.group(1).strip()
                                + " : " + v).strip()
                continue
            r["extra"][m.group(1).strip()] = v
            # fall-through: "Case :" dll tetap jadi header section
        sec = _report_section(raw)
        if sec:
            section = sec
            if sec in ("splicer", "splitter"):
                r[sec] = ((r[sec] or "") + "\n" + raw).strip()
            continue
        bm = BULLET_RE.match(raw)
        if bm:
            item = bm.group(1).strip()
            if section == "case":
                r["case"].append(item)
            elif section == "action":
                r["action"].append(item)
            elif section == "solution":
                r["solution"].append(item)
            elif section == "alat":
                r["alat_terpasang"].append(item)
            elif section == "splitter":
                r["splitter"] = ((r["splitter"] or "") + "\n" + item).strip()
            elif section == "splicer":
                r["splicer"] = ((r["splicer"] or "") + "\n" + item).strip()
            continue
        if section == "splitter":
            r["splitter"] = ((r["splitter"] or "") + "\n" + raw).strip()
        elif section == "splicer":
            r["splicer"] = ((r["splicer"] or "") + "\n" + raw).strip()
        elif section == "solution":
            r["solution"].append(raw)
        elif re.search(r"tarikan|meter", raw, re.I):
            r["meteran"] = ((r["meteran"] or "") + "\n" + raw).strip()

    return {"recognized": True, "kind": "report", "wo_code": wo_code,
            "report": r, "report_raw": text}



