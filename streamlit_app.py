import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import time
import random
import re
import io

st.set_page_config(
    page_title="Snowflake × Faegre Drinker | AI-Powered Legal Intelligence",
    page_icon="❄️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Session state init ────────────────────────────────────────────────────────
for key, default in {
    "chat_messages": [],
    "contract_selected": None,
    "contract_scanning": False,
    "contract_done": {},
    "acknowledged_flags": set(),
    "matter_filter": "All Practices",
    "client_view": False,
    "share_step": 0,
    "compliance_role": "PARALEGAL",
    "screened_attorney": None,
    "classification_done": False,
    "roi_animated": False,
    "kpi_animated": False,
    "analyst_query": "",
    "analyst_result": None,
    "analyst_running": False,
    "uploaded_file_name": None,
    "uploaded_contract": None,
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

# ── Color palette ─────────────────────────────────────────────────────────────
SB = "#29B5E8"   # Snowflake Blue
SN = "#0D1B2A"   # Snowflake Navy
GR = "#00C49F"   # Green
OR = "#FF8C42"   # Orange
RD = "#FF4B4B"   # Red
LG = "#F7F9FC"   # Light Gray
GD = "#C9A84C"   # Gold

# ── Global CSS ────────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
  .main {{ background-color:{LG}; }}
  .stApp {{ background-color:{LG}; }}

  /* Hero banner */
  .hero {{
    background: linear-gradient(135deg,{SN} 0%,#1a3a5c 55%,{SB}44 100%);
    padding:2rem 2.5rem; border-radius:16px; margin-bottom:1.5rem;
    border:1px solid {SB}33;
  }}
  .hero-title  {{ color:white; font-size:2.2rem; font-weight:800; margin:0; line-height:1.2; }}
  .hero-sub    {{ color:{SB}; font-size:1.05rem; font-weight:500; margin-top:.4rem; }}
  .hero-meta   {{ color:#8BA3B8; font-size:.82rem; margin-top:.2rem; }}

  /* KPI cards */
  .kpi {{ background:white; border-radius:12px; padding:1.2rem 1.5rem;
          border-left:4px solid {SB}; box-shadow:0 2px 12px rgba(0,0,0,.06); }}
  .kpi-gold {{ background:white; border-radius:12px; padding:1.2rem 1.5rem;
               border-left:4px solid {GD}; box-shadow:0 2px 12px rgba(0,0,0,.06); }}
  .kpi-label {{ color:#5A6A7A; font-size:.78rem; text-transform:uppercase;
                letter-spacing:.06em; font-weight:600; }}
  .kpi-value {{ color:{SN}; font-size:2rem; font-weight:800; line-height:1.2; }}
  .kpi-delta {{ color:{GR}; font-size:.83rem; font-weight:600; }}
  .kpi-warn  {{ color:{OR}; font-size:.83rem; font-weight:600; }}

  /* Section header */
  .sh {{ color:{SN}; font-size:1.25rem; font-weight:700;
         border-bottom:2px solid {SB}; padding-bottom:.4rem; margin-bottom:1rem; }}

  /* Doc card */
  .dc {{ background:white; border-radius:10px; padding:1.1rem 1.3rem;
         border:1px solid #E2EBF5; box-shadow:0 2px 8px rgba(0,0,0,.04); margin-bottom:.7rem; }}

  /* Insight box */
  .ib {{ background:linear-gradient(135deg,#EFF8FF,#F0FFF9);
         border:1px solid {SB}44; border-radius:10px; padding:.9rem 1.1rem; margin:.4rem 0; }}

  /* AI response box */
  .air {{ background:linear-gradient(135deg,{SN}F5,#0f2d4a);
          border-left:4px solid {SB}; border-radius:10px; padding:1.1rem 1.4rem;
          color:#E8F4FD; font-size:.9rem; line-height:1.7; margin:.6rem 0; }}

  /* Badges */
  .b-ok   {{ background:{GR}22; color:#00956F; padding:2px 10px; border-radius:20px;
             font-size:.74rem; font-weight:700; }}
  .b-warn {{ background:{OR}22; color:{OR}; padding:2px 10px; border-radius:20px;
             font-size:.74rem; font-weight:700; }}
  .b-err  {{ background:{RD}22; color:{RD}; padding:2px 10px; border-radius:20px;
             font-size:.74rem; font-weight:700; }}
  .b-blue {{ background:{SB}22; color:#0073A8; padding:2px 10px; border-radius:20px;
             font-size:.74rem; font-weight:700; }}

  /* Use-case card */
  .uc {{ background:white; border-radius:12px; padding:1.2rem 1.4rem;
         border:1px solid #E2EBF5; border-top:3px solid {SB};
         box-shadow:0 2px 8px rgba(0,0,0,.04); height:100%; margin-bottom:.8rem; }}
  .uc-icon  {{ font-size:1.7rem; margin-bottom:.4rem; }}
  .uc-title {{ color:{SN}; font-weight:700; font-size:.98rem; margin-bottom:.3rem; }}
  .uc-desc  {{ color:#5A6A7A; font-size:.84rem; line-height:1.5; }}

  /* Alert pulse */
  @keyframes pulse-red {{
    0%,100% {{ box-shadow:0 0 0 0 {RD}55; }}
    50%      {{ box-shadow:0 0 0 8px {RD}00; }}
  }}
  .alert-pulse {{
    animation: pulse-red 2s infinite;
    border:1px solid {RD}44;
    background:{RD}08;
    border-radius:10px;
    padding:1rem 1.2rem;
    margin-bottom:.7rem;
  }}

  /* Fade-in */
  @keyframes fadeIn {{
    from {{ opacity:0; transform:translateY(8px); }}
    to   {{ opacity:1; transform:translateY(0); }}
  }}
  .fade-in {{ animation:fadeIn .5s ease forwards; }}

  /* Extraction field row */
  .ef {{ display:flex; align-items:flex-start; gap:.8rem; padding:.6rem 0;
         border-bottom:1px solid #E2EBF5; animation:fadeIn .4s ease forwards; }}
  .ef-label {{ color:#888; font-size:.78rem; text-transform:uppercase;
               letter-spacing:.05em; width:160px; flex-shrink:0; padding-top:2px; }}
  .ef-value {{ color:{SN}; font-size:.9rem; font-weight:600; flex:1; }}

  /* Step card */
  .step-card {{
    background:white; border-radius:12px; padding:1.3rem 1.5rem;
    border:1px solid #E2EBF5; box-shadow:0 2px 8px rgba(0,0,0,.04);
    border-left:4px solid {SB}; margin-bottom:.8rem;
  }}
  .step-inactive {{
    background:#F8FAFC; border-radius:12px; padding:1.3rem 1.5rem;
    border:1px dashed #CBD5E0; margin-bottom:.8rem; opacity:.45;
  }}

  /* Activity feed item */
  .af {{ padding:.5rem .8rem; border-radius:8px; margin-bottom:.4rem;
         background:{SB}12; border-left:3px solid {SB}; font-size:.78rem; }}
  .af-user  {{ color:white; font-weight:600; }}
  .af-action{{ color:#8BA3B8; }}
  .af-time  {{ color:{SB}; float:right; font-weight:600; }}

  /* Blocked flash */
  @keyframes blocked-flash {{
    0%,100% {{ background:{RD}10; }}
    25%,75% {{ background:{RD}30; }}
  }}
  .blocked-card {{
    animation:blocked-flash 1.5s ease 1;
    background:{RD}10; border:2px solid {RD}55; border-radius:12px;
    padding:1.2rem 1.5rem; text-align:center;
  }}

  /* Blur transition */
  .pii-blurred {{ filter:blur(5px); transition:filter .5s ease; }}
  .pii-clear   {{ filter:blur(0); transition:filter .5s ease; }}

  /* Sidebar */
  div[data-testid="stSidebarContent"] {{ background:{SN}; }}
  .stTabs [data-baseweb="tab-list"] {{
    gap:6px; background:white; padding:5px; border-radius:10px; border:1px solid #E2EBF5;
  }}
  .stTabs [data-baseweb="tab"] {{
    border-radius:7px; font-weight:600; padding:7px 14px;
  }}
</style>
""", unsafe_allow_html=True)

# ── Sidebar ────────────────────────────────────────────────────────────────────
ACTIVITY_FEED = [
    ("Sarah Chen", "queried Matter M-2026-0041 billing detail", "just now"),
    ("AI Cortex", "extracted 8 clauses from MSA-2024-0142", "12s ago"),
    ("global_pharma_corp", "accessed client matter portal", "38s ago"),
    ("James Holloway", "ran research query on FTC merger guidelines", "1m ago"),
    ("AI Cortex", "flagged risk in VEN-2025-1105 — expiring May 31", "2m ago"),
    ("Michelle Park", "filtered matters by Healthcare practice", "3m ago"),
    ("AI Cortex", "completed classification scan: 847 PII columns tagged", "5m ago"),
    ("David Reyes", "access to M-2026-0042 blocked — ethical wall", "6m ago"),
]

with st.sidebar:
    st.markdown(f"""
    <div style="padding:.5rem 0 1.5rem 0;">
      <div style="color:white;font-size:1.4rem;font-weight:800;letter-spacing:-.5px;">❄️ Snowflake</div>
      <div style="color:{SB};font-size:.78rem;font-weight:600;letter-spacing:.1em;text-transform:uppercase;">AI Data Cloud Demo</div>
    </div>""", unsafe_allow_html=True)

    st.markdown(f'<div style="color:#8BA3B8;font-size:.73rem;text-transform:uppercase;letter-spacing:.08em;font-weight:600;margin-bottom:.4rem;">Demo Modules</div>', unsafe_allow_html=True)

    page = st.radio("Navigate", [
        "🏠 Overview",
        "📄 Contract Intelligence",
        "🔍 Legal Research AI",
        "📊 Matter Analytics",
        "🤝 Client Collaboration",
        "🔒 Compliance & Governance",
        "💰 ROI Calculator",
    ], label_visibility="collapsed")

    st.markdown("---")
    st.markdown(f'<div style="color:#8BA3B8;font-size:.73rem;text-transform:uppercase;letter-spacing:.08em;font-weight:600;margin-bottom:.5rem;">Live Activity</div>', unsafe_allow_html=True)
    for user, action, t in ACTIVITY_FEED[:5]:
        st.markdown(f"""
        <div class="af">
          <span class="af-time">{t}</span>
          <span class="af-user">{user}</span>
          <span class="af-action"> {action}</span>
        </div>""", unsafe_allow_html=True)

    st.markdown(f"""
    <div style="margin-top:1rem;padding:.7rem;background:{SB}15;border-radius:8px;border:1px solid {SB}33;">
      <div style="color:white;font-weight:700;font-size:.8rem;">Faegre Drinker Biddle & Reath LLP</div>
      <div style="color:#8BA3B8;font-size:.72rem;line-height:1.6;margin-top:.2rem;">
        Am Law 100 · $500M+ Revenue · 750+ Attorneys<br>
        <span style="color:{SB};">Chief Technology & Innovation Officer</span>
      </div>
    </div>
    <div style="margin-top:.8rem;padding:.6rem;background:{RD}12;border-radius:8px;border:1px solid {RD}22;">
      <div style="color:{OR};font-size:.7rem;font-weight:700;">SIMULATED DEMO</div>
      <div style="color:#8BA3B8;font-size:.69rem;margin-top:.2rem;">Illustrative data only. No real client information used.</div>
    </div>""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# Data
# ═══════════════════════════════════════════════════════════════════════════════
# ── Contract upload helpers ───────────────────────────────────────────────────

def _extract_text_from_file(uploaded_file) -> tuple[str, int]:
    """Return (text, page_count) from an uploaded PDF, DOCX, or TXT file."""
    name = uploaded_file.name.lower()
    raw = uploaded_file.read()
    if name.endswith(".pdf"):
        try:
            from pypdf import PdfReader
            reader = PdfReader(io.BytesIO(raw))
            pages = len(reader.pages)
            text = "\n".join(p.extract_text() or "" for p in reader.pages)
            return text, pages
        except Exception:
            return "", 0
    elif name.endswith(".docx"):
        try:
            import docx
            doc = docx.Document(io.BytesIO(raw))
            text = "\n".join(p.text for p in doc.paragraphs)
            pages = max(1, len(text) // 3000)
            return text, pages
        except Exception:
            return "", 1
    else:
        text = raw.decode("utf-8", errors="replace")
        pages = max(1, len(text) // 3000)
        return text, pages


def _find(pattern, text, default="Not identified"):
    m = re.search(pattern, text, re.IGNORECASE)
    return m.group(1).strip() if m else default


def analyze_uploaded_contract(uploaded_file) -> dict:
    """Extract text and run clause/risk analysis on a user-uploaded contract."""
    text, pages = _extract_text_from_file(uploaded_file)
    filename = uploaded_file.name
    base_id = re.sub(r"[^A-Z0-9]", "-", filename.upper().replace(".PDF", "").replace(".DOCX", "").replace(".TXT", ""))[:20]
    contract_id = f"UPL-{base_id[:15]}"

    # ── Clause extraction ────────────────────────────────────────────────────
    gov_law = _find(r"governed by (?:the laws? of )?(?:the (?:State|Commonwealth) of )?([A-Z][a-zA-Z ]{2,30})", text)
    if gov_law == "Not identified":
        gov_law = _find(r"laws? of (?:the (?:State|Commonwealth) of )?([A-Z][a-zA-Z]{3,20})", text)

    term_notice = _find(r"(\d+)[- ]days?['\s]+(?:written |prior )?notice", text)
    if term_notice != "Not identified":
        term_notice = f"{term_notice} days written notice"

    liab_cap_raw = _find(r"(?:shall not exceed|limited to|cap(?:ped)? at)\s+(\$[\d,]+(?:\.\d+)?(?:\s*(?:million|thousand))?)", text)
    liab_cap = liab_cap_raw if liab_cap_raw != "Not identified" else "Not specified — review required"

    auto_renew_match = re.search(r"auto(?:matically)?[\s-]renew|automatic(?:ally)? renew|evergreen", text, re.IGNORECASE)
    auto_renew = "Yes — check for opt-out window" if auto_renew_match else "No"

    conf_period = _find(r"(\d+)[- ]years? (?:following|after|from|post)[- ](?:termination|expiration|expiry)", text)
    conf_period = f"{conf_period} years post-termination" if conf_period != "Not identified" else _find(r"confidentiality.*?(?:period|term)[^.]{0,40}(\d+ year[s]?)", text)

    eff_date = _find(r"(?:effective|commencing|as of)[:\s]+([A-Z][a-z]+ \d{1,2},? \d{4}|\d{1,2}/\d{1,2}/\d{4})", text)
    exp_date = _find(r"(?:expires?|expiration|terminates?|end date)[:\s]+([A-Z][a-z]+ \d{1,2},? \d{4}|\d{1,2}/\d{1,2}/\d{4})", text)
    dollar_vals = re.findall(r"\$[\d,]+(?:\.\d+)?(?:\s*(?:million|thousand))?", text, re.IGNORECASE)
    contract_value = max(dollar_vals, key=lambda x: len(x), default="Not specified") if dollar_vals else "Not specified"

    extracted = [
        ("Governing Law", gov_law),
        ("Termination Notice", term_notice),
        ("Liability Cap", liab_cap),
        ("Auto-Renewal", auto_renew),
        ("Confidentiality Period", conf_period),
        ("Effective Date", eff_date),
        ("Expiry Date", exp_date),
        ("Contract Value", contract_value),
    ]

    # ── Obligation sentences ─────────────────────────────────────────────────
    sentences = re.split(r"(?<=[.;])\s+", text)
    obligation_keywords = re.compile(
        r"\b(shall|must|required to|agrees? to|obligated to|will provide|will deliver)\b",
        re.IGNORECASE,
    )
    deadline_keywords = re.compile(r"\b(by |within \d|no later than|prior to|before )\b", re.IGNORECASE)
    obligations = []
    for s in sentences:
        s = s.strip()
        if 20 < len(s) < 220 and obligation_keywords.search(s):
            label = "⚠️ DEADLINE" if deadline_keywords.search(s) else ""
            obligations.append(f"{label} {s}".strip() if label else s)
        if len(obligations) >= 6:
            break
    if not obligations:
        obligations = ["Review document manually — obligation clauses not clearly structured"]

    # ── Risk scoring ─────────────────────────────────────────────────────────
    score = 20
    flags = []

    if liab_cap_raw == "Not identified":
        score += 20
        flags.append(("No liability cap found — significant exposure risk", False))

    if gov_law == "Not identified":
        score += 15
        flags.append(("Governing law not identified — jurisdiction risk", False))

    if auto_renew_match:
        score += 12
        flags.append(("Auto-renewal clause detected — verify opt-out window and deadline", False))

    if re.search(r"\bindemnif", text, re.IGNORECASE):
        score += 10
        flags.append(("Indemnification clause present — review scope and carve-outs", False))

    if re.search(r"\bAI\b|artificial intelligence|machine learning|generative", text, re.IGNORECASE):
        score += 8
        flags.append(("AI/ML references detected — review IP ownership and data usage clauses", False))

    if re.search(r"perpetual|indefinite|no expir", text, re.IGNORECASE):
        score += 8
        flags.append(("Perpetual or indefinite term detected — confirm intent", False))

    if re.search(r"arbitrat|dispute resolution|mediat", text, re.IGNORECASE):
        score += 5
        flags.append(("Dispute resolution / arbitration clause present", False))

    large_dollar = any(
        float(re.sub(r"[,$]", "", v.split()[0])) >= 1_000_000
        for v in dollar_vals
        if re.sub(r"[,$]", "", v.split()[0]).replace(".", "").isdigit()
    ) if dollar_vals else False
    if large_dollar:
        score += 8
        flags.append(("High-value contract — enhanced review recommended", False))

    if not flags:
        flags.append(("No major risk flags detected — document appears standard", False))

    score = min(score, 98)
    risk_label = "High" if score >= 70 else ("Medium" if score >= 40 else "Low")

    contract_type = "Unknown"
    if re.search(r"\bnon.?disclosure\b|\bNDA\b|\bconfidentiality agreement\b", text, re.IGNORECASE):
        contract_type = "Non-Disclosure Agreement"
    elif re.search(r"\bmaster services\b|\bMSA\b", text, re.IGNORECASE):
        contract_type = "Master Services Agreement"
    elif re.search(r"\bengagement letter\b|\bretainer\b", text, re.IGNORECASE):
        contract_type = "Engagement Letter"
    elif re.search(r"\bvendor\b|\bservices agreement\b|\bstatement of work\b|\bSOW\b", text, re.IGNORECASE):
        contract_type = "Services / Vendor Agreement"
    elif re.search(r"\blicense\b|\blicensing\b", text, re.IGNORECASE):
        contract_type = "License Agreement"
    elif re.search(r"\blease\b|\btenancy\b|\bpremises\b", text, re.IGNORECASE):
        contract_type = "Lease Agreement"

    client_match = re.search(
        r"(?:between|party|client|customer)[:\s]+([A-Z][A-Za-z\s,\.]{4,50}(?:LLC|Inc\.|Corp\.|LLP|Ltd\.)?)",
        text,
    )
    client = client_match.group(1).strip()[:50] if client_match else "Unknown Party"

    return {
        "id": contract_id,
        "label": f"📎 {filename}",
        "client": client,
        "type": contract_type,
        "pages": pages,
        "effective": eff_date,
        "expires": exp_date,
        "value": contract_value,
        "status": "Uploaded",
        "risk": score,
        "risk_label": risk_label,
        "extracted": extracted,
        "obligations": obligations,
        "risk_flags": flags,
        "_uploaded": True,
    }


CONTRACTS = [
    {
        "id": "MSA-2024-0142", "label": "Global Pharma Corp — Master Services Agreement",
        "client": "Global Pharma Corp", "type": "Master Services Agreement",
        "pages": 47, "effective": "March 1, 2024", "expires": "February 28, 2027",
        "value": "$4,200,000", "status": "Active", "risk": 62, "risk_label": "Medium",
        "extracted": [
            ("Governing Law", "Delaware"),
            ("Termination Notice", "90 days written notice"),
            ("Liability Cap", "$5,000,000 or 12 months fees — whichever is greater"),
            ("Auto-Renewal", "Yes — 1-year terms, 60-day opt-out window"),
            ("Confidentiality Period", "3 years post-termination"),
            ("Billing Rate Lock", "Preferred rates locked through Dec 31, 2026"),
        ],
        "obligations": [
            "Quarterly business reviews required with Partner-level attendance",
            "Annual SOC 2 Type II certification required",
            "Dedicated partner lead assigned to account",
        ],
        "risk_flags": [
            ("Auto-renewal window opens Dec 31, 2026 — action required within 60 days", False),
            ("Liability cap below Am Law 100 benchmark for this contract value", False),
            ("IP ownership clause ambiguous for AI-generated work product", False),
        ],
    },
    {
        "id": "ENG-2026-0023", "label": "Midwest Manufacturing — Litigation Engagement",
        "client": "Midwest Manufacturing Inc.", "type": "Engagement Letter — Litigation",
        "pages": 12, "effective": "January 8, 2026", "expires": "Matter-based",
        "value": "Hourly — Est. $890,000", "status": "Active", "risk": 88, "risk_label": "High",
        "extracted": [
            ("Governing Law", "Indiana"),
            ("Termination Notice", "Client: anytime · Firm: 30 days"),
            ("Liability Cap", "Not addressed — exposure risk"),
            ("Auto-Renewal", "N/A — matter-based"),
            ("Confidentiality Period", "Indefinite (A/C privilege)"),
            ("Billing Requirement", "Monthly with detailed narrative"),
        ],
        "obligations": [
            "Motion to dismiss due April 30, 2026 — IMMINENT",
            "Expert witness designation by June 15, 2026",
            "Privilege log due within 30 days of discovery requests",
        ],
        "risk_flags": [
            ("IMMINENT: Motion to dismiss deadline April 30, 2026", False),
            ("No liability cap — unusual for complex litigation", False),
            ("Client has prior billing dispute history — document all time carefully", False),
            ("Third-party funding clause may require court disclosure", False),
        ],
    },
    {
        "id": "VEN-2025-1105", "label": "LegalTech Solutions — Vendor Agreement",
        "client": "LegalTech Solutions Inc.", "type": "Vendor Services Agreement",
        "pages": 31, "effective": "June 1, 2025", "expires": "May 31, 2026",
        "value": "$240,000/year", "status": "Expiring Soon", "risk": 54, "risk_label": "Medium",
        "extracted": [
            ("Governing Law", "Minnesota"),
            ("Termination Notice", "60 days written notice"),
            ("Liability Cap", "$240,000 (1 year fees)"),
            ("Auto-Renewal", "Yes — 1-year, 60-day opt-out"),
            ("SLA Uptime", "99.9% with 2× credit for breaches"),
            ("Data Portability", "Standard formats upon termination"),
        ],
        "obligations": [
            "Renewal or replacement decision needed by March 31, 2026",
            "Security incident notification required within 24 hours",
            "Annual pricing review — 5% increase cap",
        ],
        "risk_flags": [
            ("Contract expiring May 31, 2026 — renewal decision overdue", False),
            ("Vendor data residency clause may conflict with new state privacy laws", False),
            ("No AI/ML use restriction — review for client data exposure risk", False),
        ],
    },
    {
        "id": "NDA-2025-0891", "label": "TechStart Ventures — Non-Disclosure Agreement",
        "client": "TechStart Ventures LLC", "type": "Non-Disclosure Agreement",
        "pages": 8, "effective": "January 15, 2025", "expires": "January 14, 2028",
        "value": "N/A", "status": "Active", "risk": 22, "risk_label": "Low",
        "extracted": [
            ("Governing Law", "New York"),
            ("Termination Notice", "30 days written notice"),
            ("Liability Cap", "Not specified"),
            ("Auto-Renewal", "No"),
            ("Confidentiality Period", "5 years post-termination"),
            ("Scope", "Mutual — both parties' confidential information"),
        ],
        "obligations": [
            "Return or destroy materials upon termination",
            "Permitted disclosures limited to need-to-know employees only",
        ],
        "risk_flags": [
            ("No liability cap specified — unusual even for mutual NDAs", False),
            ("Definition of 'Confidential Information' broader than firm standard", False),
        ],
    },
]

MATTERS = [
    {"id": "M-2026-0041", "client": "Global Pharma Corp",   "type": "Regulatory", "partner": "Sarah Chen",     "hrs": 412, "fees": 618000,  "budget": 700000,  "status": "On Track",    "practice": "Life Sciences"},
    {"id": "M-2026-0042", "client": "Midwest Manufacturing", "type": "Litigation", "partner": "James Holloway", "hrs": 589, "fees": 883500,  "budget": 890000,  "status": "At Risk",     "practice": "Labor & Employment"},
    {"id": "M-2025-1847", "client": "HealthSystem Partners", "type": "M&A",        "partner": "Michelle Park",  "hrs":1204, "fees":1806000,  "budget":1800000,  "status": "Over Budget", "practice": "Healthcare"},
    {"id": "M-2026-0078", "client": "TechStart Ventures",    "type": "Corporate",  "partner": "David Reyes",    "hrs":  88, "fees": 132000,  "budget": 200000,  "status": "On Track",    "practice": "Private Equity"},
    {"id": "M-2026-0089", "client": "National Retail Group", "type": "IP/Patent",  "partner": "Lisa Tran",      "hrs": 256, "fees": 384000,  "budget": 350000,  "status": "Over Budget", "practice": "Intellectual Property"},
    {"id": "M-2026-0112", "client": "Financial Services Co.","type": "Regulatory", "partner": "Michael Torres",  "hrs": 177, "fees": 265500,  "budget": 400000,  "status": "On Track",    "practice": "Financial Services"},
    {"id": "M-2026-0134", "client": "Energy Holdings LLC",   "type": "Litigation", "partner": "Amanda Foster",  "hrs": 334, "fees": 501000,  "budget": 600000,  "status": "On Track",    "practice": "Energy"},
    {"id": "M-2026-0156", "client": "State University",      "type": "Employment", "partner": "Robert Kim",     "hrs": 145, "fees": 145000,  "budget": 180000,  "status": "On Track",    "practice": "Labor & Employment"},
]

RESEARCH_QA = {
    "Tortious interference elements in Delaware": {
        "answer": "Under Delaware law, a **tortious interference** claim requires four elements:\n\n1. **Valid business relationship or expectancy** — not merely a hope, but a reasonable probability of future economic benefit\n2. **Knowledge** of the relationship by the defendant\n3. **Intentional interference** that induces a breach or termination\n4. **Resulting damages** to the plaintiff\n\nCourts emphasize the interference must be *improper* — competition alone is insufficient. Relevant cases include *WaveDivision Holdings v. Highland Capital Mgmt.* (Del. Ch. 2007) and *Lipson v. Anesthesia Services* (Del. Super. 1991).",
        "sources": ["WaveDivision Holdings v. Highland Capital Mgmt., 2007 Del. Ch. LEXIS 88", "Lipson v. Anesthesia Services, 1991 WL 280264 (Del. Super.)", "Restatement (Second) of Torts §766B"],
        "confidence": 97,
    },
    "FTC pharmaceutical merger review trends 2024–2026": {
        "answer": "FTC pharmaceutical merger review has **intensified significantly** from 2024–2026:\n\n- **Pipeline drug overlaps** — Commission now challenges deals where acquirer holds competing pipeline assets, even pre-approval\n- **Structural divestitures preferred** — behavioral remedies rejected in 8 of 11 challenged deals\n- **'Killer acquisition' scrutiny** — heightened review of large pharma acquiring early-stage competitors\n- **Data concentration theory** — novel harm theory where merger consolidates patient health data\n- **Second Request rate up 34% YoY** — broader investigation scope\n\nNew merger guidelines specific to life sciences emphasize *innovation competition* alongside traditional HHI concentration analysis.",
        "sources": ["FTC v. AbbVie Inc., No. 1:19-cv-02408 (D.D.C. 2024)", "FTC Pharmaceutical Merger Guidelines Update (2025)", "FTC Annual Competition Report 2025"],
        "confidence": 94,
    },
    "Attorney-client privilege in internal investigations": {
        "answer": "Internal investigation privilege is governed by ***Upjohn Co. v. United States*** (449 U.S. 383, 1981), extending privilege beyond the 'control group' test. For privilege to apply:\n\n1. Communication made by an **employee to corporate counsel**\n2. Made at the **direction of corporate superiors**\n3. For the **purpose of obtaining legal advice**\n4. Employee must be **aware** the communication is for legal advice\n5. Must remain **confidential**\n\n**2024–2026 developments:** Several circuits have narrowed privilege for mixed business/legal purpose investigations. The DOJ's updated guidelines require privilege logs within 30 days. The 9th Circuit's *In re: Grand Jury* 'primary purpose' test has been adopted by additional circuits, creating new circuit splits.",
        "sources": ["Upjohn Co. v. United States, 449 U.S. 383 (1981)", "In re: Grand Jury, 23 F.4th 1088 (9th Cir. 2023)", "DOJ Internal Investigation Guidelines (2025 Update)"],
        "confidence": 96,
    },
    "WARN Act requirements for 200+ employee reduction": {
        "answer": "The **WARN Act (29 U.S.C. § 2101)** requires **60 days' advance written notice** for covered plant closings and mass layoffs. For a workforce reduction of 200+ employees:\n\n- **Covered employer threshold:** 100+ full-time employees (or 100+ who work 4,000+ hours/week combined)\n- **Mass layoff trigger:** 500 employees, OR 50–499 employees if they constitute ≥33% of the workforce\n- **Notice recipients:** Affected employees, state dislocated worker unit, and local government\n- **Key exceptions:** Faltering company, unforeseeable business circumstances, natural disaster\n\n**2025 state law note:** Several states (CA, NY, NJ, IL) have enacted mini-WARN statutes with *stricter* thresholds and longer notice periods. California requires 60 days regardless of percentage threshold for 50+ employees.",
        "sources": ["29 U.S.C. § 2101-2109 (WARN Act)", "20 C.F.R. Part 639 (DOL Implementing Regulations)", "Cal. Lab. Code § 1400 et seq. (Cal-WARN)"],
        "confidence": 98,
    },
}

ANALYST_QUERIES = {
    "Which matters are over budget?": {
        "cols": ["Matter ID", "Client", "Fees Billed", "Budget", "Over By", "% of Budget"],
        "rows": [
            ["M-2025-1847", "HealthSystem Partners", "$1,806,000", "$1,800,000", "$6,000", "100.3%"],
            ["M-2026-0089", "National Retail Group", "$384,000", "$350,000", "$34,000", "109.7%"],
        ],
    },
    "Who are the top 3 partners by fees billed this year?": {
        "cols": ["Partner", "Practice", "Active Matters", "Total Fees Billed"],
        "rows": [
            ["Michelle Park", "Healthcare", "1", "$1,806,000"],
            ["James Holloway", "Labor & Employment", "1", "$883,500"],
            ["Amanda Foster", "Energy", "1", "$501,000"],
        ],
    },
    "Show me all litigation matters and their budget status": {
        "cols": ["Matter ID", "Client", "Partner", "Fees Billed", "Budget", "Status"],
        "rows": [
            ["M-2026-0042", "Midwest Manufacturing", "James Holloway", "$883,500", "$890,000", "At Risk"],
            ["M-2026-0134", "Energy Holdings LLC", "Amanda Foster", "$501,000", "$600,000", "On Track"],
        ],
    },
}

# ═══════════════════════════════════════════════════════════════════════════════
# Page: Overview
# ═══════════════════════════════════════════════════════════════════════════════
if page == "🏠 Overview":
    st.markdown(f"""
    <div class="hero">
      <div class="hero-title">❄️ Snowflake × Faegre Drinker</div>
      <div class="hero-sub">AI-Powered Legal Intelligence — Transforming How Law Gets Done</div>
      <div class="hero-meta">Confidential Demo · Prepared by Snowflake Sales Engineering · April 2026</div>
    </div>""", unsafe_allow_html=True)

    # Animated KPI counters
    kpis = [
        ("kpi1", "Attorney Hours Saved / Year", 28400, "", "↑ Via AI automation across contract, research & admin workflows", "kpi"),
        ("kpi2", "Contract Review Speedup", 82, "%", "↑ AI extraction vs. manual attorney review", "kpi"),
        ("kpi3", "Additional Revenue Unlocked", 12, "M+", "↑ From attorney capacity freed by AI", "kpi-gold"),
        ("kpi4", "Contract Risk Exposure Surfaced", 47, "M", "↑ Flags identified across active portfolio", "kpi-gold"),
    ]

    if not st.session_state.kpi_animated:
        c1, c2, c3, c4 = st.columns(4)
        cols_list = [c1, c2, c3, c4]
        placeholders = [c.empty() for c in cols_list]

        steps = 40
        for step in range(steps + 1):
            t = step / steps
            ease = t * t * (3 - 2 * t)
            for i, (kid, label, target, suffix, delta, cls) in enumerate(kpis):
                if suffix == "%":
                    val = f"{int(target * ease)}{suffix}"
                elif suffix in ("M+", "M"):
                    val = f"${int(target * ease)}{suffix}"
                else:
                    val = f"{int(target * ease):,}"
                placeholders[i].markdown(f"""<div class="{cls}">
                  <div class="kpi-label">{label}</div>
                  <div class="kpi-value">{val}</div>
                  <div class="kpi-delta">{delta}</div>
                </div>""", unsafe_allow_html=True)
            time.sleep(0.025)
        st.session_state.kpi_animated = True
    else:
        c1, c2, c3, c4 = st.columns(4)
        for col, (kid, label, target, suffix, delta, cls) in zip([c1, c2, c3, c4], kpis):
            if suffix == "%":
                val = f"{target}{suffix}"
            elif suffix in ("M+", "M"):
                val = f"${target}{suffix}"
            else:
                val = f"{target:,}"
            col.markdown(f"""<div class="{cls}">
              <div class="kpi-label">{label}</div>
              <div class="kpi-value">{val}</div>
              <div class="kpi-delta">{delta}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Use case cards
    st.markdown('<div class="sh">The Snowflake Platform for Legal — Six Core Capabilities</div>', unsafe_allow_html=True)
    use_cases = [
        ("📄", "Contract Intelligence", "AI_EXTRACT processes thousands of contracts in minutes — surfacing risk flags, key dates, and obligations automatically with no manual review required.", SB),
        ("🔍", "Legal Research AI", "Cortex Search + RAG lets attorneys ask natural language questions across 2.4M+ documents — case law, memos, client files — in under 2 seconds.", GR),
        ("📊", "Matter Analytics", "Real-time billing, utilization, and matter health dashboards consolidated from iManage, Aderant, and Elite — always current, no manual exports.", GD),
        ("🤝", "Client Collaboration", "Secure Data Sharing gives clients live, governed access to their matter data. No portals to build, no exports, no stale PDFs.", SB),
        ("🔒", "Compliance & Governance", "Column masking, ethical walls, and audit logs protect client PII while enabling firm-wide analytics — enforced at the storage layer.", GR),
        ("🤖", "Cortex Analyst", "Ask any business question in plain English and get a SQL-backed answer instantly — democratizing data access for every timekeeper at the firm.", GD),
    ]
    r1, r2 = st.columns(3), st.columns(3)
    for i, (icon, title, desc, color) in enumerate(use_cases):
        col = (r1 if i < 3 else r2)[i % 3]
        col.markdown(f"""<div class="uc">
          <div class="uc-icon">{icon}</div>
          <div class="uc-title" style="color:{color};">{title}</div>
          <div class="uc-desc">{desc}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    col_chart, col_why = st.columns([2, 3])
    with col_chart:
        st.markdown('<div class="sh">Active matters by practice group</div>', unsafe_allow_html=True)
        practice_df = pd.DataFrame({
            "Practice": ["Litigation", "Labor & Employment", "Life Sciences", "Healthcare", "Intellectual Property", "Private Equity", "Financial Services", "Energy"],
            "Matters": [94, 61, 38, 42, 33, 29, 27, 18]
        }).sort_values("Matters")
        fig = px.bar(practice_df, x="Matters", y="Practice", orientation="h",
                     color_discrete_sequence=[SB])
        fig.update_layout(plot_bgcolor="white", paper_bgcolor="white", height=310,
                          margin=dict(l=0, r=0, t=10, b=0),
                          xaxis=dict(showgrid=True, gridcolor="#F0F0F0"),
                          font=dict(family="sans-serif", size=12))
        st.plotly_chart(fig, use_container_width=True)

    with col_why:
        st.markdown('<div class="sh">Why Faegre Drinker + Snowflake</div>', unsafe_allow_html=True)
        reasons = [
            ("🏆", "Am Law 100 Proven", f"3 of the 5 largest US law firms run on Snowflake. Built for the security, scale, and governance demands of elite legal practice."),
            ("🔐", "Ironclad Security", f"FedRAMP, SOC 2 Type II, HIPAA, ISO 27001. The compliance posture required for client data of this sensitivity."),
            ("⚡", "Zero Data Movement", f"iManage, Aderant, Intapp, and Elite integrate natively — no ETL, no stale copies, no brittle pipelines."),
            ("🧠", "AI Built In — Not Bolted On", f"Cortex AI, Cortex Search, and Cortex Analyst are first-class Snowflake features, not third-party bolt-ons."),
            ("🤝", "Client-Ready Sharing", f"Give clients live, governed access to their matter data in days — without building a portal or writing a line of code."),
        ]
        for icon, title, desc in reasons:
            st.markdown(f"""<div class="ib">
              <b style="color:{SN};">{icon} {title}</b><br>
              <span style="color:#5A6A7A;font-size:.86rem;">{desc}</span>
            </div>""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# Page: Contract Intelligence
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "📄 Contract Intelligence":
    st.markdown(f"""
    <div class="hero">
      <div class="hero-title">📄 Contract Intelligence</div>
      <div class="hero-sub">Drop in any contract — AI extracts every key term, surfaces every risk, tracks every deadline. Automatically.</div>
      <div class="hero-meta">Snowflake Cortex AI · AI_EXTRACT · AI_FILTER · AI_SUMMARIZE</div>
    </div>""", unsafe_allow_html=True)

    # Step 1 — Upload or select a sample contract
    st.markdown('<div class="sh">Step 1 — Upload a contract or choose a sample</div>', unsafe_allow_html=True)

    uploaded_file = st.file_uploader(
        "Drag & drop a contract file here",
        type=["pdf", "docx", "txt"],
        help="Your file is processed in-memory and never stored on any server",
        label_visibility="collapsed",
    )

    if uploaded_file is not None:
        if st.session_state.uploaded_file_name != uploaded_file.name:
            st.session_state.uploaded_file_name = uploaded_file.name
            st.session_state.contract_done = {}
            with st.spinner("Extracting text from document..."):
                uploaded_file.seek(0)
                st.session_state.uploaded_contract = analyze_uploaded_contract(uploaded_file)
        contract = st.session_state.uploaded_contract
        st.markdown(f'<div style="background:#F0FBF8;border:1px solid {GR};border-radius:10px;padding:.7rem 1.1rem;font-size:.88rem;color:{SN};margin-bottom:.5rem;">📎 <b>{uploaded_file.name}</b> &nbsp;·&nbsp; {contract["pages"]} pages detected &nbsp;·&nbsp; <span style="color:{GR};font-weight:700;">Ready to analyze</span></div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div style="color:#888;font-size:.83rem;margin:.4rem 0 .5rem 0;">— or choose a sample contract below —</div>', unsafe_allow_html=True)
        contract_labels = [c["label"] for c in CONTRACTS]
        selected_label = st.radio("Sample contracts:", contract_labels, label_visibility="collapsed",
                                  horizontal=False)
        contract = next(c for c in CONTRACTS if c["label"] == selected_label)

    if st.session_state.contract_selected != contract["id"]:
        st.session_state.contract_selected = contract["id"]
        st.session_state.contract_done = {}

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="sh">Step 2 — Run AI analysis</div>', unsafe_allow_html=True)

    risk_color = RD if contract["risk"] >= 75 else (OR if contract["risk"] >= 45 else GR)
    c_meta, c_scan = st.columns([1, 2])

    with c_meta:
        st.markdown(f"""<div class="dc">
          <div style="font-weight:700;color:{SN};font-size:1rem;">{contract['id']}</div>
          <div style="color:#888;font-size:.82rem;margin:.3rem 0 .8rem 0;">{contract['type']}</div>
          <table style="width:100%;font-size:.82rem;border-collapse:collapse;">
            <tr><td style="color:#888;padding:3px 0;">Client</td><td style="font-weight:600;">{contract['client']}</td></tr>
            <tr><td style="color:#888;padding:3px 0;">Pages</td><td style="font-weight:600;">{contract['pages']}</td></tr>
            <tr><td style="color:#888;padding:3px 0;">Effective</td><td style="font-weight:600;">{contract['effective']}</td></tr>
            <tr><td style="color:#888;padding:3px 0;">Expires</td><td style="font-weight:600;">{contract['expires']}</td></tr>
            <tr><td style="color:#888;padding:3px 0;">Value</td><td style="font-weight:600;">{contract['value']}</td></tr>
            <tr><td style="color:#888;padding:3px 0;">Status</td><td><span class="{'b-ok' if contract['status']=='Active' else 'b-warn'}">{contract['status']}</span></td></tr>
          </table>
        </div>""", unsafe_allow_html=True)

        run_btn = st.button("🧠 Analyze with Cortex AI", use_container_width=True, type="primary")

    with c_scan:
        scan_placeholder = st.empty()

        if run_btn or contract["id"] in st.session_state.contract_done:
            if run_btn and contract["id"] not in st.session_state.contract_done:
                # Animated scan
                stages = [
                    (0.15, "Loading document..."),
                    (0.35, "OCR & text extraction..."),
                    (0.55, "Identifying clauses & sections..."),
                    (0.75, "Running AI_EXTRACT..."),
                    (0.90, "Scoring risk flags..."),
                    (1.00, "Complete ✓"),
                ]
                for prog, msg in stages:
                    scan_placeholder.markdown(f"""<div class="dc">
                      <div style="font-weight:700;color:{SN};margin-bottom:.8rem;">
                        🔄 Cortex AI Processing — {contract['pages']} pages
                      </div>
                      <div style="color:#888;font-size:.85rem;margin-bottom:.6rem;">{msg}</div>
                    </div>""", unsafe_allow_html=True)
                    with scan_placeholder.container():
                        st.progress(prog, text=msg)
                    time.sleep(0.45)
                st.session_state.contract_done[contract["id"]] = True

            scan_placeholder.empty()

            # Results tabs
            tab_terms, tab_oblig, tab_risk = st.tabs(["📋 Extracted Terms", "✅ Key Obligations", "⚠️ Risk Flags"])

            with tab_terms:
                # Gauge chart
                g_col, f_col = st.columns([1, 2])
                with g_col:
                    fig_gauge = go.Figure(go.Indicator(
                        mode="gauge+number",
                        value=contract["risk"],
                        title={"text": "Risk Score", "font": {"size": 14}},
                        gauge={
                            "axis": {"range": [0, 100]},
                            "bar": {"color": risk_color},
                            "steps": [
                                {"range": [0, 40], "color": "rgba(0,196,159,0.2)"},
                                {"range": [40, 70], "color": "rgba(255,140,66,0.2)"},
                                {"range": [70, 100], "color": "rgba(255,75,75,0.2)"},
                            ],
                            "threshold": {"line": {"color": risk_color, "width": 3}, "value": contract["risk"]},
                        }
                    ))
                    fig_gauge.update_layout(height=200, margin=dict(l=10, r=10, t=30, b=10),
                                            paper_bgcolor="white", font=dict(family="sans-serif"))
                    st.plotly_chart(fig_gauge, use_container_width=True)
                    st.markdown(f'<span style="background:{risk_color}22;color:{risk_color};padding:3px 12px;border-radius:20px;font-size:.8rem;font-weight:700;">⚠ {contract["risk_label"]} Risk</span>', unsafe_allow_html=True)

                with f_col:
                    if run_btn or True:
                        field_placeholder = st.empty()
                        shown = []
                        for label, val in contract["extracted"]:
                            shown.append((label, val))
                            rows_html = "".join(f"""<div class="ef fade-in">
                              <div class="ef-label">{l}</div>
                              <div class="ef-value">{v}</div>
                            </div>""" for l, v in shown)
                            field_placeholder.markdown(f'<div style="background:white;border-radius:10px;padding:.8rem 1rem;border:1px solid #E2EBF5;">{rows_html}</div>', unsafe_allow_html=True)
                            time.sleep(0.18)

            with tab_oblig:
                for ob in contract["obligations"]:
                    is_urgent = "IMMINENT" in ob
                    st.markdown(f"""<div style="background:{'#FFF0F0' if is_urgent else f'{GR}10'};
                      border-left:3px solid {RD if is_urgent else GR};
                      padding:.7rem 1rem;border-radius:7px;margin-bottom:.5rem;
                      font-size:.88rem;color:{SN};">
                      {'🚨' if is_urgent else '✅'} {ob}
                    </div>""", unsafe_allow_html=True)

            with tab_risk:
                flags = st.session_state.acknowledged_flags
                cid = contract["id"]
                for i, (flag, _) in enumerate(contract["risk_flags"]):
                    flag_key = f"{cid}_{i}"
                    is_urgent = "IMMINENT" in flag
                    is_acked = flag_key in flags
                    col_flag, col_btn = st.columns([6, 1])
                    with col_flag:
                        if is_acked:
                            st.markdown(f'<div style="background:#F8F8F8;border-left:3px solid #CCC;padding:.6rem 1rem;border-radius:7px;margin-bottom:.5rem;color:#888;font-size:.86rem;text-decoration:line-through;">✓ {flag}</div>', unsafe_allow_html=True)
                        else:
                            color = RD if is_urgent else OR
                            st.markdown(f'<div style="background:{color}10;border-left:3px solid {color};padding:.7rem 1rem;border-radius:7px;margin-bottom:.5rem;font-size:.88rem;color:{SN};">{"🚨" if is_urgent else "⚠️"} {flag}</div>', unsafe_allow_html=True)
                    with col_btn:
                        if not is_acked:
                            if st.button("Ack", key=f"ack_{flag_key}"):
                                st.session_state.acknowledged_flags.add(flag_key)
                                st.rerun()
        else:
            scan_placeholder.markdown(f"""<div class="dc" style="text-align:center;padding:2.5rem;color:#888;">
              <div style="font-size:2rem;margin-bottom:.5rem;">🧠</div>
              <div style="font-weight:600;color:{SN};">Ready to analyze</div>
              <div style="font-size:.84rem;margin-top:.3rem;">Click "Analyze with Cortex AI" to extract all terms</div>
            </div>""", unsafe_allow_html=True)

    # Portfolio summary
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="sh">Full contract portfolio — AI risk scores</div>', unsafe_allow_html=True)
    df_portfolio = pd.DataFrame([{
        "Contract ID": c["id"], "Client": c["client"], "Type": c["type"],
        "Value": c["value"], "Expires": c["expires"], "Risk Score": c["risk"],
        "Risk Level": c["risk_label"], "Status": c["status"], "Flags": len(c["risk_flags"])
    } for c in CONTRACTS])
    st.dataframe(df_portfolio, hide_index=True, use_container_width=True)


# ═══════════════════════════════════════════════════════════════════════════════
# Page: Legal Research AI
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "🔍 Legal Research AI":
    st.markdown(f"""
    <div class="hero">
      <div class="hero-title">🔍 Legal Research AI</div>
      <div class="hero-sub">Ask any legal question — get an answer grounded in 2.4M+ indexed documents in under 2 seconds</div>
      <div class="hero-meta">Snowflake Cortex Search · Retrieval-Augmented Generation · 96% accuracy on legal eval set</div>
    </div>""", unsafe_allow_html=True)

    m1, m2, m3, m4 = st.columns(4)
    for col, (label, val, delta) in zip([m1, m2, m3, m4], [
        ("Documents Indexed", "2.4M", "iManage + PACER + Research DBs"),
        ("Avg. Response Time", "1.3s", "End-to-end including LLM"),
        ("Accuracy (Eval Set)", "96%", "Attorney-graded Q&A benchmarks"),
        ("Source Attribution", "100%", "Every answer cites sources"),
    ]):
        col.markdown(f"""<div class="kpi">
          <div class="kpi-label">{label}</div>
          <div class="kpi-value">{val}</div>
          <div class="kpi-delta">{delta}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Chat interface
    chat_container = st.container()

    # Suggestion pills (only if no messages)
    if not st.session_state.chat_messages:
        st.markdown('<div style="color:#888;font-size:.84rem;margin-bottom:.4rem;">Try a sample question:</div>', unsafe_allow_html=True)
        suggestion = st.pills(
            "Suggestions",
            list(RESEARCH_QA.keys()),
            label_visibility="collapsed",
        )
        if suggestion:
            st.session_state.chat_messages.append({"role": "user", "content": suggestion})
            st.rerun()

    # Render chat history
    with chat_container:
        for msg in st.session_state.chat_messages:
            with st.chat_message(msg["role"], avatar="⚖️" if msg["role"] == "user" else "❄️"):
                if msg["role"] == "assistant":
                    st.markdown(msg["content"])
                    if "sources" in msg:
                        with st.expander("📚 Sources & citations", expanded=False):
                            for src in msg["sources"]:
                                st.markdown(f"- {src}")
                        col_c, col_t = st.columns(2)
                        col_c.metric("Confidence", f"{msg.get('confidence', 95)}%")
                        col_t.metric("Response time", "1.3s")
                else:
                    st.write(msg["content"])

    # Handle new input
    if prompt := st.chat_input("Ask a legal research question..."):
        st.session_state.chat_messages.append({"role": "user", "content": prompt})

        qa = RESEARCH_QA.get(prompt)

        with chat_container:
            with st.chat_message("user", avatar="⚖️"):
                st.write(prompt)

            with st.chat_message("assistant", avatar="❄️"):
                if qa:
                    def stream_response(text):
                        for word in text.split(" "):
                            yield word + " "
                            time.sleep(0.025)

                    full = st.write_stream(stream_response(qa["answer"]))
                    with st.expander("📚 Sources & citations", expanded=False):
                        for src in qa["sources"]:
                            st.markdown(f"- {src}")
                    col_c, col_t = st.columns(2)
                    col_c.metric("Confidence", f"{qa['confidence']}%")
                    col_t.metric("Response time", "1.3s")
                    st.session_state.chat_messages.append({
                        "role": "assistant", "content": full,
                        "sources": qa["sources"], "confidence": qa["confidence"]
                    })
                else:
                    def stream_generic():
                        response = (
                            "Based on Faegre Drinker's indexed document corpus — including iManage files, PACER docket data, "
                            "Westlaw integration, and internal precedent library — here is a synthesized analysis for your query. "
                            "In production, this response draws from your firm's actual privileged documents with full source attribution "
                            "and confidence scoring. Every answer is grounded in retrieved passages so attorneys can verify the basis immediately. "
                            "Response time from a 2.4M-document corpus: 1.3 seconds."
                        )
                        for word in response.split(" "):
                            yield word + " "
                            time.sleep(0.025)

                    full = st.write_stream(stream_generic())
                    st.session_state.chat_messages.append({"role": "assistant", "content": full})

    if st.session_state.chat_messages:
        if st.button("Clear conversation", type="secondary"):
            st.session_state.chat_messages = []
            st.rerun()


# ═══════════════════════════════════════════════════════════════════════════════
# Page: Matter Analytics
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "📊 Matter Analytics":
    st.markdown(f"""
    <div class="hero">
      <div class="hero-title">📊 Matter Analytics</div>
      <div class="hero-sub">Real-time visibility into billing, utilization, budget health, and profitability across every matter at the firm</div>
      <div class="hero-meta">Powered by Snowflake Cortex Analyst — ask questions in plain English, get instant answers</div>
    </div>""", unsafe_allow_html=True)

    df = pd.DataFrame(MATTERS)

    # Practice filter
    practices = ["All Practices"] + sorted(df["practice"].unique().tolist())
    practice_filter = st.pills("Filter by practice:", practices, default="All Practices")
    if practice_filter and practice_filter != "All Practices":
        df_filtered = df[df["practice"] == practice_filter]
    else:
        df_filtered = df

    # KPIs
    kc1, kc2, kc3, kc4 = st.columns(4)
    with kc1:
        st.markdown(f"""<div class="kpi">
          <div class="kpi-label">Total fees billed</div>
          <div class="kpi-value">${df_filtered['fees'].sum()/1e6:.1f}M</div>
          <div class="kpi-delta">↑ YTD 2026 (filtered)</div>
        </div>""", unsafe_allow_html=True)
    with kc2:
        st.markdown(f"""<div class="kpi">
          <div class="kpi-label">Active matters shown</div>
          <div class="kpi-value">{len(df_filtered)}</div>
          <div class="kpi-delta">↑ of 342 firm-wide</div>
        </div>""", unsafe_allow_html=True)
    with kc3:
        over = len(df_filtered[df_filtered["status"] == "Over Budget"])
        st.markdown(f"""<div class="kpi" style="border-left-color:{RD};">
          <div class="kpi-label">Over budget</div>
          <div class="kpi-value" style="color:{RD};">{over}</div>
          <div class="kpi-warn">↑ Requires attention</div>
        </div>""", unsafe_allow_html=True)
    with kc4:
        at_risk = len(df_filtered[df_filtered["status"] == "At Risk"])
        st.markdown(f"""<div class="kpi" style="border-left-color:{OR};">
          <div class="kpi-label">At risk</div>
          <div class="kpi-value" style="color:{OR};">{at_risk}</div>
          <div class="kpi-warn">↑ Monitor closely</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Alert cards for problem matters
    problem_matters = df_filtered[df_filtered["status"].isin(["Over Budget", "At Risk"])]
    if len(problem_matters) > 0:
        st.markdown(f'<div style="color:{RD};font-weight:700;font-size:.9rem;margin-bottom:.5rem;">⚡ Matters requiring attention ({len(problem_matters)})</div>', unsafe_allow_html=True)
        for _, m in problem_matters.iterrows():
            pct = m["fees"] / m["budget"] * 100
            st.markdown(f"""<div class="alert-pulse">
              <div style="display:flex;justify-content:space-between;align-items:center;">
                <div>
                  <span style="font-weight:700;color:{SN};">{m['id']}</span>
                  <span style="color:#888;font-size:.82rem;margin-left:.6rem;">{m['client']} · {m['practice']}</span>
                </div>
                <span class="{'b-err' if m['status']=='Over Budget' else 'b-warn'}">{m['status']}</span>
              </div>
              <div style="display:flex;gap:2rem;margin-top:.6rem;font-size:.85rem;">
                <span><b style="color:{SN};">${m['fees']:,.0f}</b> <span style="color:#888;">billed</span></span>
                <span><b style="color:{SN};">${m['budget']:,.0f}</b> <span style="color:#888;">budget</span></span>
                <span><b style="color:{RD if pct>100 else OR};">{pct:.0f}%</b> <span style="color:#888;">of budget used</span></span>
                <span><b style="color:{SN};">{m['partner']}</b></span>
              </div>
            </div>""", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

    col_tbl, col_pie = st.columns([3, 2])

    with col_tbl:
        st.markdown('<div class="sh">Matter portfolio</div>', unsafe_allow_html=True)
        display = df_filtered[["id", "client", "practice", "partner", "hrs", "fees", "budget", "status"]].copy()
        display.columns = ["Matter ID", "Client", "Practice", "Partner", "Hours", "Fees Billed", "Budget", "Status"]
        display["Fees Billed"] = display["Fees Billed"].apply(lambda x: f"${x:,.0f}")
        display["Budget"] = display["Budget"].apply(lambda x: f"${x:,.0f}")
        st.dataframe(display, hide_index=True, use_container_width=True, height=300)

    with col_pie:
        st.markdown('<div class="sh">Fees by practice group</div>', unsafe_allow_html=True)
        pie_df = df_filtered.groupby("practice")["fees"].sum().reset_index()
        fig_pie = px.pie(pie_df, names="practice", values="fees", hole=0.45,
                         color_discrete_sequence=[SB, GR, GD, OR, "#9B59B6", RD, "#1ABC9C", "#E74C3C"])
        fig_pie.update_layout(plot_bgcolor="white", paper_bgcolor="white", height=300,
                               margin=dict(l=0, r=0, t=10, b=0), legend=dict(font=dict(size=10)))
        st.plotly_chart(fig_pie, use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)

    col_bar, col_analyst = st.columns([3, 2])

    with col_bar:
        st.markdown('<div class="sh">Budget vs. fees billed</div>', unsafe_allow_html=True)
        fig_bar = go.Figure()
        fig_bar.add_trace(go.Bar(name="Fees Billed", x=df_filtered["id"], y=df_filtered["fees"],
                                 marker_color=SB, opacity=.85))
        fig_bar.add_trace(go.Scatter(name="Budget", x=df_filtered["id"], y=df_filtered["budget"],
                                     mode="markers", marker=dict(symbol="diamond", size=10, color=RD)))
        fig_bar.update_layout(plot_bgcolor="white", paper_bgcolor="white", height=280,
                               margin=dict(l=0, r=0, t=10, b=0), barmode="group",
                               legend=dict(orientation="h", y=1.1),
                               yaxis_tickprefix="$", yaxis_tickformat=",.0f",
                               xaxis=dict(tickangle=-30))
        st.plotly_chart(fig_bar, use_container_width=True)

    with col_analyst:
        st.markdown('<div class="sh">Ask Cortex Analyst</div>', unsafe_allow_html=True)
        st.caption("Ask any question about your matters in plain English")

        preset_qs = list(ANALYST_QUERIES.keys())
        analyst_q = st.selectbox("Choose a question:", preset_qs, label_visibility="collapsed")

        if st.button("Ask Cortex Analyst →", type="primary", use_container_width=True):
            st.session_state.analyst_query = analyst_q
            st.session_state.analyst_result = None
            with st.spinner("Cortex Analyst translating to SQL and running..."):
                time.sleep(1.4)
            st.session_state.analyst_result = ANALYST_QUERIES[analyst_q]

        if st.session_state.analyst_result:
            result = st.session_state.analyst_result
            st.markdown(f'<div style="background:{GR}12;border-left:3px solid {GR};padding:.6rem .9rem;border-radius:7px;margin:.5rem 0;font-size:.82rem;color:{SN};font-weight:600;">✅ {st.session_state.analyst_query}</div>', unsafe_allow_html=True)
            res_df = pd.DataFrame(result["rows"], columns=result["cols"])
            st.dataframe(res_df, hide_index=True, use_container_width=True)


# ═══════════════════════════════════════════════════════════════════════════════
# Page: Client Collaboration
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "🤝 Client Collaboration":
    st.markdown(f"""
    <div class="hero">
      <div class="hero-title">🤝 Client Data Collaboration</div>
      <div class="hero-sub">Give clients live, governed access to their matter data — no portals, no exports, no stale PDFs, ever</div>
      <div class="hero-meta">Snowflake Secure Data Sharing · Zero-Copy Architecture · Row-Level Security</div>
    </div>""", unsafe_allow_html=True)

    toggle_col, _ = st.columns([2, 3])
    with toggle_col:
        view_toggle = st.toggle("👤 Simulate Client Login — Global Pharma Corp", value=st.session_state.client_view)
        if view_toggle != st.session_state.client_view:
            st.session_state.client_view = view_toggle
            st.rerun()

    if st.session_state.client_view:
        # Client portal simulation
        st.markdown(f"""
        <div style="background:linear-gradient(135deg,{SN},#1a3a5c);padding:1.2rem 1.8rem;border-radius:14px;margin-bottom:1rem;border:2px solid {SB}55;">
          <div style="color:{SB};font-size:.75rem;font-weight:700;text-transform:uppercase;letter-spacing:.08em;">Snowflake Secure Share — Live Matter Portal</div>
          <div style="color:white;font-size:1.3rem;font-weight:800;margin-top:.3rem;">Global Pharma Corp · Client View</div>
          <div style="color:#8BA3B8;font-size:.8rem;margin-top:.2rem;">You are viewing data shared by Faegre Drinker Biddle & Reath LLP · Real-time · Zero copies</div>
        </div>""", unsafe_allow_html=True)

        client_matters = [m for m in MATTERS if m["client"] == "Global Pharma Corp"]

        # Query counter animation
        qcount_ph = st.empty()
        for q in range(0, 285, 12):
            qcount_ph.markdown(f'<div style="text-align:right;color:#888;font-size:.78rem;margin-bottom:.5rem;">⚡ {q} queries run against this share this month</div>', unsafe_allow_html=True)
            time.sleep(0.01)
        qcount_ph.markdown(f'<div style="text-align:right;color:{SB};font-size:.78rem;margin-bottom:.5rem;font-weight:600;">⚡ 284 queries run against this share this month</div>', unsafe_allow_html=True)

        for m in client_matters:
            pct = m["fees"] / m["budget"] * 100
            color = GR if pct < 85 else (OR if pct < 100 else RD)
            st.markdown(f"""<div class="dc">
              <div style="display:flex;justify-content:space-between;">
                <div>
                  <span style="font-weight:700;color:{SN};">{m['id']} — {m['type']}</span>
                  <span style="color:#888;font-size:.8rem;margin-left:.6rem;">Partner: {m['partner']}</span>
                </div>
                <span class="{'b-ok' if m['status']=='On Track' else 'b-warn'}">{m['status']}</span>
              </div>
              <div style="display:flex;gap:2.5rem;margin-top:.9rem;">
                <div><div style="color:#888;font-size:.74rem;">FEES BILLED</div><div style="font-weight:700;font-size:1.2rem;color:{SN};">${m['fees']:,.0f}</div></div>
                <div><div style="color:#888;font-size:.74rem;">BUDGET</div><div style="font-weight:700;font-size:1.2rem;color:{SN};">${m['budget']:,.0f}</div></div>
                <div><div style="color:#888;font-size:.74rem;">HOURS</div><div style="font-weight:700;font-size:1.2rem;color:{SN};">{m['hrs']:,}</div></div>
                <div><div style="color:#888;font-size:.74rem;">BUDGET USED</div><div style="font-weight:700;font-size:1.2rem;color:{color};">{pct:.0f}%</div></div>
              </div>
              <div style="background:#F8FAFC;border-radius:6px;height:8px;margin-top:.8rem;">
                <div style="background:{color};width:{min(pct,100):.0f}%;height:8px;border-radius:6px;transition:width .5s;"></div>
              </div>
            </div>""", unsafe_allow_html=True)

        st.markdown(f"""<div class="ib">
          <b style="color:{SN};">🔒 How this works</b><br>
          <span style="color:#5A6A7A;font-size:.86rem;">Global Pharma Corp is querying Faegre Drinker's Snowflake account directly via a secure share — zero data was copied or exported. Row-level security ensures they see <em>only their matters</em>. Faegre Drinker can revoke access in a single click.</span>
        </div>""", unsafe_allow_html=True)

    else:
        # Step-by-step walkthrough
        steps = [
            ("1", "Create a Row-Level Security view", f"A single SQL view filters matter data by `CURRENT_USER()` — each client automatically sees only their matters when they query the share. No application logic required."),
            ("2", "Create the secure share", f"Snowflake creates a zero-copy pointer to your data. No data is duplicated, moved, or exported. The share references live production data in real time."),
            ("3", "Add the client's Snowflake account", f"Specify the client's Snowflake account identifier. They instantly gain access. You control exactly which objects, tables, and columns they can see."),
            ("4", "Client queries live — always current", f"The client connects their own BI tools (Tableau, Power BI, Sigma, or SQL) to the share. Every query hits live data. No refresh cycles, no stale PDFs, no billing disputes."),
        ]

        total_steps = len(steps)
        current = st.session_state.share_step

        step_cols = st.columns(total_steps)
        for i, (num, title, _) in enumerate(steps):
            is_active = i <= current
            step_cols[i].markdown(f"""<div style="text-align:center;padding:.5rem;">
              <div style="width:36px;height:36px;border-radius:50%;background:{'linear-gradient(135deg,'+SB+','+GR+')' if is_active else '#E2EBF5'};
                color:{'white' if is_active else '#888'};font-weight:800;font-size:1rem;display:flex;align-items:center;justify-content:center;margin:0 auto .5rem auto;">{num}</div>
              <div style="font-size:.78rem;font-weight:{700 if is_active else 400};color:{SN if is_active else '#999'};">{title}</div>
            </div>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        for i, (num, title, desc) in enumerate(steps):
            if i <= current:
                st.markdown(f"""<div class="step-card fade-in">
                  <div style="display:flex;align-items:center;gap:.8rem;margin-bottom:.5rem;">
                    <div style="width:28px;height:28px;border-radius:50%;background:linear-gradient(135deg,{SB},{GR});
                      color:white;font-weight:800;font-size:.9rem;display:flex;align-items:center;justify-content:center;flex-shrink:0;">{num}</div>
                    <div style="font-weight:700;color:{SN};">{title}</div>
                  </div>
                  <div style="color:#5A6A7A;font-size:.88rem;line-height:1.6;margin-left:2.3rem;">{desc}</div>
                </div>""", unsafe_allow_html=True)
            else:
                st.markdown(f"""<div class="step-inactive">
                  <div style="font-weight:600;color:#888;">Step {num} — {title}</div>
                </div>""", unsafe_allow_html=True)

        btn_col_a, btn_col_b, _ = st.columns([1, 1, 3])
        with btn_col_a:
            if current < total_steps - 1:
                if st.button("Next step →", type="primary", use_container_width=True):
                    st.session_state.share_step += 1
                    st.rerun()
            else:
                st.button("✅ Setup complete!", disabled=True, use_container_width=True)
        with btn_col_b:
            if current > 0:
                if st.button("Reset", use_container_width=True):
                    st.session_state.share_step = 0
                    st.rerun()

        if current == total_steps - 1:
            st.success("Sharing is live — toggle 'Simulate Client Login' above to see the client experience!", icon="🎉")

        st.markdown("<br>", unsafe_allow_html=True)
        shares_df = pd.DataFrame([
            {"Client": "Global Pharma Corp",  "Share": "FD_GPCorp_MatterShare", "Matters": 3, "Last Query": "Today, 9:42 AM", "Queries (30d)": 284, "Status": "Active"},
            {"Client": "HealthSystem Partners","Share": "FD_HSP_MatterShare",   "Matters": 1, "Last Query": "Yesterday, 3:15 PM","Queries (30d)": 142, "Status": "Active"},
            {"Client": "National Retail Group","Share": "FD_NRG_MatterShare",   "Matters": 1, "Last Query": "Apr 28, 2026",     "Queries (30d)": 67,  "Status": "Active"},
            {"Client": "Financial Services Co.","Share": "FD_FSC_MatterShare",  "Matters": 1, "Last Query": "—",                "Queries (30d)": 0,   "Status": "Pending"},
        ])
        st.markdown('<div class="sh">Active client shares</div>', unsafe_allow_html=True)
        st.dataframe(shares_df, hide_index=True, use_container_width=True)


# ═══════════════════════════════════════════════════════════════════════════════
# Page: Compliance & Governance
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "🔒 Compliance & Governance":
    st.markdown(f"""
    <div class="hero">
      <div class="hero-title">🔒 Compliance & Data Governance</div>
      <div class="hero-sub">Protect every client record, enforce every ethical wall, and prove compliance — without slowing down analytics</div>
      <div class="hero-meta">Column Masking · Row Access Policies · Automated Classification · Immutable Audit Logs</div>
    </div>""", unsafe_allow_html=True)

    cc1, cc2, cc3, cc4 = st.columns(4)
    for col, (label, val, delta) in zip([cc1, cc2, cc3, cc4], [
        ("Protected PII Columns", "847", "Auto-classified across 214 tables"),
        ("Ethical Wall Policies", "124", "Active across active matter portfolio"),
        ("Audit Events / Day", "41K", "Immutable, queryable via SQL"),
        ("Compliance Posture", "98%", "SOC 2 · ISO 27001 · HIPAA"),
    ]):
        col.markdown(f"""<div class="kpi">
          <div class="kpi-label">{label}</div>
          <div class="kpi-value">{val}</div>
          <div class="kpi-delta">{delta}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    tab_mask, tab_walls, tab_audit, tab_class = st.tabs([
        "🎭 Data Masking", "🚧 Ethical Walls", "📋 Audit Trail", "🏷️ Auto-Classification"
    ])

    with tab_mask:
        st.markdown('<div class="sh">Role-based PII protection — live demo</div>', unsafe_allow_html=True)
        st.markdown(f"""<div class="ib" style="margin-bottom:1rem;">
          <b style="color:{SN};">How it works</b> — Snowflake's column-level masking policies evaluate the querying user's role at runtime. The exact same query returns full data to a Partner and masked data to a Paralegal. The policy is enforced at the storage layer — no application code required, no bypass possible.
        </div>""", unsafe_allow_html=True)

        role_col, _ = st.columns([2, 3])
        with role_col:
            new_role = st.segmented_control(
                "Simulated role:", ["PARALEGAL", "ASSOCIATE", "PARTNER", "COMPLIANCE"],
                default=st.session_state.compliance_role
            )
            if new_role and new_role != st.session_state.compliance_role:
                st.session_state.compliance_role = new_role
                st.rerun()

        role = st.session_state.compliance_role
        can_see_pii = role in ("PARTNER", "COMPLIANCE")

        demo_records = [
            {"Name": "Margaret Thompson", "SSN": "123-45-6789", "DOB": "1965-03-14", "Email": "m.thompson@email.com", "Matter IDs": "M-2026-0041"},
            {"Name": "James Richardson", "SSN": "987-65-4321", "DOB": "1978-09-22", "Email": "j.richardson@corp.com", "Matter IDs": "M-2026-0042"},
            {"Name": "Sandra O'Brien", "SSN": "456-78-9012", "DOB": "1982-07-05", "Email": "s.obrien@email.com", "Matter IDs": "M-2026-0078"},
        ]

        def mask(val, field, visible):
            if visible:
                return val
            if field == "SSN":
                return f"***-**-{val[-4:]}"
            if field == "DOB":
                return "****-**-**"
            if field == "Email":
                parts = val.split("@")
                return f"{parts[0][0]}***@***.***"
            return val

        col_style = "pii-clear" if can_see_pii else "pii-blurred"
        hdr_bg = SN if can_see_pii else "#F8FAFC"
        hdr_color = "white" if can_see_pii else "#888"
        badge_bg = "#00956F22" if can_see_pii else f"{OR}22"
        badge_color = "#00956F" if can_see_pii else OR
        badge_label = f"🔓 Full Access — {role}" if can_see_pii else f"🔒 PII Masked — {role}"
        pii_text_color = "#333" if can_see_pii else "#CCC"
        pii_blur = "" if can_see_pii else "filter:blur(4px);"
        headers_html = "".join(
            f'<th style="padding:8px 12px;text-align:left;color:#5A6A7A;font-size:.76rem;text-transform:uppercase;letter-spacing:.04em;border-bottom:1px solid #E2EBF5;">{h}</th>'
            for h in ["Name", "SSN", "Date of Birth", "Email", "Matter IDs"]
        )
        rows_html = "".join(
            f'<tr style="border-bottom:1px solid #F0F0F0;">'
            f'<td style="padding:8px 12px;font-weight:600;color:{SN};">{r["Name"]}</td>'
            f'<td style="padding:8px 12px;color:{pii_text_color};font-family:monospace;{pii_blur}">{mask(r["SSN"],"SSN",can_see_pii)}</td>'
            f'<td style="padding:8px 12px;color:{pii_text_color};{pii_blur}">{mask(r["DOB"],"DOB",can_see_pii)}</td>'
            f'<td style="padding:8px 12px;color:{pii_text_color};{pii_blur}">{mask(r["Email"],"Email",can_see_pii)}</td>'
            f'<td style="padding:8px 12px;color:#333;">{r["Matter IDs"]}</td>'
            f'</tr>'
            for r in demo_records
        )
        st.markdown(f"""
        <div style="background:white;border-radius:12px;border:1px solid #E2EBF5;overflow:hidden;margin-top:.5rem;">
          <div style="background:{hdr_bg};padding:.7rem 1rem;display:flex;justify-content:space-between;align-items:center;">
            <span style="color:{hdr_color};font-weight:700;font-size:.85rem;">fd_clients.intake.client_records</span>
            <span style="background:{badge_bg};color:{badge_color};padding:2px 10px;border-radius:20px;font-size:.74rem;font-weight:700;">{badge_label}</span>
          </div>
          <table style="width:100%;border-collapse:collapse;font-size:.85rem;">
            <tr style="background:#F8FAFC;">{headers_html}</tr>
            {rows_html}
          </table>
        </div>""", unsafe_allow_html=True)

        if not can_see_pii:
            st.markdown(f'<div style="margin-top:.5rem;"><span class="b-warn">⚠ PII columns masked — switch to PARTNER or COMPLIANCE role to view unmasked data</span></div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div style="margin-top:.5rem;"><span class="b-ok">✅ Full PII visible — {role} role has access</span></div>', unsafe_allow_html=True)

    with tab_walls:
        st.markdown('<div class="sh">Ethical wall enforcement — try accessing a screened matter</div>', unsafe_allow_html=True)
        st.markdown(f"""<div class="ib" style="margin-bottom:1rem;">
          Row Access Policies make screened matters <em>invisible</em> — the query returns zero rows with no error or hint that the matter exists. This is enforced at the storage layer, not the application layer, so there is no bypass path.
        </div>""", unsafe_allow_html=True)

        attorneys = ["James Holloway", "Sarah Chen", "David Reyes", "Michelle Park", "Lisa Tran"]
        screened_map = {
            "David Reyes": ("M-2026-0042", "Midwest Manufacturing Inc.", "Prior representation of opposing party"),
            "Lisa Tran": ("M-2026-0042", "Midwest Manufacturing Inc.", "Prior representation of opposing party"),
            "James Holloway": ("M-2025-1847", "HealthSystem Partners", "Spousal conflict of interest"),
        }

        atty = st.selectbox("Select an attorney to query matters as:", attorneys)
        matter_to_query = st.selectbox("Matter to query:", [m["id"] for m in MATTERS])

        if st.button("Run Query", type="primary"):
            st.session_state.screened_attorney = atty
            with st.spinner("Checking row access policy..."):
                time.sleep(0.8)

            if atty in screened_map:
                screened_matter, screened_client, reason = screened_map[atty]
                if matter_to_query == screened_matter or atty in ["David Reyes", "Lisa Tran"]:
                    st.markdown(f"""<div class="blocked-card">
                      <div style="font-size:2rem;margin-bottom:.5rem;">🚫</div>
                      <div style="color:{RD};font-weight:800;font-size:1.1rem;">ACCESS BLOCKED</div>
                      <div style="color:#888;font-size:.85rem;margin-top:.5rem;">
                        Attorney <b style="color:{SN};">{atty}</b> is screened from <b style="color:{SN};">{screened_matter}</b>
                      </div>
                      <div style="color:#888;font-size:.82rem;margin-top:.3rem;">Reason: {reason}</div>
                      <div style="margin-top:.8rem;padding:.5rem 1rem;background:{RD}15;border-radius:8px;display:inline-block;">
                        <span style="color:{RD};font-size:.78rem;font-weight:700;">Query returned 0 rows · Policy enforced at storage layer · Event logged to audit trail</span>
                      </div>
                    </div>""", unsafe_allow_html=True)
                    st.toast(f"Ethical wall triggered — {atty} blocked from {screened_matter}", icon="🚫")
                else:
                    st.success(f"✅ {atty} has access to {matter_to_query} — {len([m for m in MATTERS if m['id'] == matter_to_query])} record(s) returned")
            else:
                st.success(f"✅ {atty} has access to {matter_to_query} — {len([m for m in MATTERS if m['id'] == matter_to_query])} record(s) returned")

        walls_df = pd.DataFrame([
            {"Attorney": "David Reyes", "Screened From": "M-2026-0042", "Client": "Midwest Manufacturing Inc.", "Reason": "Prior representation", "Since": "2026-01-09"},
            {"Attorney": "Lisa Tran", "Screened From": "M-2026-0042", "Client": "Midwest Manufacturing Inc.", "Reason": "Prior representation", "Since": "2026-01-09"},
            {"Attorney": "James Holloway", "Screened From": "M-2025-1847", "Client": "HealthSystem Partners", "Reason": "Spousal conflict", "Since": "2025-11-15"},
            {"Attorney": "Michael Torres", "Screened From": "M-2026-0078", "Client": "TechStart Ventures", "Reason": "Prior client conflict", "Since": "2026-02-14"},
        ])
        st.markdown('<div class="sh" style="margin-top:1.5rem;">Active ethical walls</div>', unsafe_allow_html=True)
        st.dataframe(walls_df, hide_index=True, use_container_width=True)

    with tab_audit:
        st.markdown('<div class="sh">Immutable audit trail — every query, every user</div>', unsafe_allow_html=True)
        st.markdown(f"""<div class="ib" style="margin-bottom:1rem;">
          Snowflake's ACCESS_HISTORY view logs every query with full context — object accessed, rows returned, execution time, and role used. Logs are tamper-proof, retained for 7 years, and searchable in seconds via SQL. No SIEM required for basic compliance reporting.
        </div>""", unsafe_allow_html=True)
        audit_df = pd.DataFrame([
            {"Timestamp": "2026-04-30 09:42:11", "User": "sarah.chen@fd.com", "Role": "PARTNER", "Object": "client_matter_view", "Rows": 47, "Status": "SUCCESS"},
            {"Timestamp": "2026-04-30 09:38:04", "User": "system@globalpharmacorp.com", "Role": "SHARE_CONSUMER", "Object": "billing_detail (share)", "Rows": 312, "Status": "SUCCESS"},
            {"Timestamp": "2026-04-30 09:22:55", "User": "david.reyes@fd.com", "Role": "ASSOCIATE", "Object": "all_matters", "Rows": 0, "Status": "BLOCKED (Ethical Wall)"},
            {"Timestamp": "2026-04-30 09:15:30", "User": "james.holloway@fd.com", "Role": "PARTNER", "Object": "active_contracts", "Rows": 8, "Status": "SUCCESS"},
            {"Timestamp": "2026-04-30 08:55:12", "User": "michelle.park@fd.com", "Role": "PARTNER", "Object": "client_records", "Rows": 23, "Status": "SUCCESS"},
            {"Timestamp": "2026-04-29 17:44:09", "User": "unknown@external.net", "Role": "N/A", "Object": "all_matters", "Rows": 0, "Status": "BLOCKED (Auth Failure)"},
        ])
        st.dataframe(audit_df, hide_index=True, use_container_width=True)

    with tab_class:
        st.markdown('<div class="sh">Automated PII classification — scan your entire data estate</div>', unsafe_allow_html=True)
        st.markdown(f"""<div class="ib" style="margin-bottom:1rem;">
          Snowflake's <b>SYSTEM$CLASSIFY</b> automatically scans every column in a table, assigns semantic categories (EMAIL, SSN, DATE_OF_BIRTH, etc.) and privacy tiers (SENSITIVE, QUASI_IDENTIFIER), and can auto-apply masking tags — all without writing any application code.
        </div>""", unsafe_allow_html=True)

        if not st.session_state.classification_done:
            if st.button("🔍 Run Classification Scan on client_records", type="primary"):
                scan_ph = st.empty()
                columns_to_scan = [
                    ("client_ssn", "IDENTIFIER", "SENSITIVE", "ssn_mask"),
                    ("date_of_birth", "DATE_OF_BIRTH", "SENSITIVE", "dob_mask"),
                    ("email_address", "EMAIL", "QUASI_IDENTIFIER", "email_mask"),
                    ("home_address", "ADDRESS", "SENSITIVE", "address_mask"),
                    ("phone_number", "PHONE_NUMBER", "QUASI_IDENTIFIER", "phone_mask"),
                    ("matter_description", "FREE_TEXT", "SENSITIVE", "Manual review"),
                ]
                found = []
                for col_name, semantic, privacy, policy in columns_to_scan:
                    with scan_ph.container():
                        st.progress(len(found) / len(columns_to_scan), text=f"Scanning column: {col_name}...")
                    time.sleep(0.4)
                    found.append({"Column": col_name, "Semantic Category": semantic,
                                  "Privacy Tier": privacy, "Suggested Policy": policy,
                                  "Auto-Tagged": "✅" if policy != "Manual review" else "⚠️ Partial"})
                    scan_ph.empty()
                    with scan_ph.container():
                        st.dataframe(pd.DataFrame(found), hide_index=True, use_container_width=True)

                st.session_state.classification_done = True
                st.success(f"Classification complete — {len(columns_to_scan)} columns scanned, {len(columns_to_scan)-1} auto-tagged with masking policies!", icon="✅")
        else:
            class_df = pd.DataFrame([
                {"Column": "client_ssn", "Semantic": "IDENTIFIER", "Privacy": "SENSITIVE", "Policy": "ssn_mask", "Tagged": "✅"},
                {"Column": "date_of_birth", "Semantic": "DATE_OF_BIRTH", "Privacy": "SENSITIVE", "Policy": "dob_mask", "Tagged": "✅"},
                {"Column": "email_address", "Semantic": "EMAIL", "Privacy": "QUASI_IDENTIFIER", "Policy": "email_mask", "Tagged": "✅"},
                {"Column": "home_address", "Semantic": "ADDRESS", "Privacy": "SENSITIVE", "Policy": "address_mask", "Tagged": "✅"},
                {"Column": "phone_number", "Semantic": "PHONE_NUMBER", "Privacy": "QUASI_IDENTIFIER", "Policy": "phone_mask", "Tagged": "✅"},
                {"Column": "matter_description", "Semantic": "FREE_TEXT", "Privacy": "SENSITIVE", "Policy": "Manual review", "Tagged": "⚠️ Partial"},
            ])
            st.dataframe(class_df, hide_index=True, use_container_width=True)
            if st.button("Re-run scan"):
                st.session_state.classification_done = False
                st.rerun()


# ═══════════════════════════════════════════════════════════════════════════════
# Page: ROI Calculator
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "💰 ROI Calculator":
    st.markdown(f"""
    <div class="hero">
      <div class="hero-title">💰 ROI Calculator</div>
      <div class="hero-sub">Quantify the Snowflake opportunity — customize to Faegre Drinker's actual profile</div>
      <div class="hero-meta">Based on Am Law 100 deployment benchmarks · Adjust sliders to model your firm</div>
    </div>""", unsafe_allow_html=True)

    st.markdown('<div class="sh">Firm inputs</div>', unsafe_allow_html=True)
    ci1, ci2, ci3 = st.columns(3)
    with ci1:
        num_attorneys = st.slider("Number of attorneys", 400, 1200, 750, 50)
        avg_rate = st.slider("Avg billable rate ($/hr)", 400, 1200, 750, 50)
    with ci2:
        contract_volume = st.slider("Contracts reviewed / year", 500, 10000, 3500, 250)
        research_hrs = st.slider("Attorney research hours / week", 5, 30, 12)
    with ci3:
        ai_speedup = st.slider("Contract review speedup (AI)", 2, 10, 5)
        research_speedup = st.slider("Research speedup (AI search)", 2, 8, 4)
        retention_pct = st.slider("Client retention improvement (%)", 1, 15, 5)

    contract_hrs_saved = (contract_volume * 3.5) * (1 - 1 / ai_speedup)
    research_hrs_saved = num_attorneys * research_hrs * 48 * (1 - 1 / research_speedup)
    admin_hrs_saved = 180 * 12 * 0.70
    total_hrs = contract_hrs_saved + research_hrs_saved + admin_hrs_saved
    rev_capacity = total_hrs * avg_rate * 0.65
    risk_reduction = contract_volume * 14000 * 0.03
    retention_val = num_attorneys * avg_rate * 1800 * 0.15 * (retention_pct / 100)
    platform_savings = 515000
    total_value = rev_capacity + risk_reduction + retention_val + platform_savings
    investment = max(180000, num_attorneys * 420)
    roi_pct = (total_value - investment) / investment * 100
    payback = investment / (total_value / 12)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="sh">Value summary</div>', unsafe_allow_html=True)

    # Animated KPI counters
    roi_ph1, roi_ph2, roi_ph3, roi_ph4 = [c.empty() for c in st.columns(4)]

    if not st.session_state.roi_animated:
        steps = 45
        for step in range(steps + 1):
            t = step / steps
            ease = t * t * (3 - 2 * t)
            roi_ph1.markdown(f"""<div class="kpi">
              <div class="kpi-label">Attorney hours saved / year</div>
              <div class="kpi-value">{int(total_hrs*ease):,}</div>
              <div class="kpi-delta">Contract + Research + Admin</div>
            </div>""", unsafe_allow_html=True)
            roi_ph2.markdown(f"""<div class="kpi">
              <div class="kpi-label">Revenue from freed capacity</div>
              <div class="kpi-value">${rev_capacity*ease/1e6:.1f}M</div>
              <div class="kpi-delta">At 65% realization rate</div>
            </div>""", unsafe_allow_html=True)
            roi_ph3.markdown(f"""<div class="kpi-gold">
              <div class="kpi-label">Total annual value</div>
              <div class="kpi-value">${total_value*ease/1e6:.1f}M</div>
              <div class="kpi-delta">Across all value drivers</div>
            </div>""", unsafe_allow_html=True)
            roi_ph4.markdown(f"""<div class="kpi-gold">
              <div class="kpi-label">ROI</div>
              <div class="kpi-value">{int(roi_pct*ease):.0f}%</div>
              <div class="kpi-delta">{payback:.1f} month payback</div>
            </div>""", unsafe_allow_html=True)
            time.sleep(0.018)
        st.session_state.roi_animated = True
        if roi_pct > 400:
            st.balloons()
    else:
        roi_ph1.markdown(f"""<div class="kpi">
          <div class="kpi-label">Attorney hours saved / year</div>
          <div class="kpi-value">{int(total_hrs):,}</div>
          <div class="kpi-delta">Contract + Research + Admin</div>
        </div>""", unsafe_allow_html=True)
        roi_ph2.markdown(f"""<div class="kpi">
          <div class="kpi-label">Revenue from freed capacity</div>
          <div class="kpi-value">${rev_capacity/1e6:.1f}M</div>
          <div class="kpi-delta">At 65% realization rate</div>
        </div>""", unsafe_allow_html=True)
        roi_ph3.markdown(f"""<div class="kpi-gold">
          <div class="kpi-label">Total annual value</div>
          <div class="kpi-value">${total_value/1e6:.1f}M</div>
          <div class="kpi-delta">Across all value drivers</div>
        </div>""", unsafe_allow_html=True)
        roi_ph4.markdown(f"""<div class="kpi-gold">
          <div class="kpi-label">ROI</div>
          <div class="kpi-value">{roi_pct:.0f}%</div>
          <div class="kpi-delta">{payback:.1f} month payback</div>
        </div>""", unsafe_allow_html=True)

    # Reset animation when sliders change
    if st.button("Recalculate & animate", type="secondary"):
        st.session_state.roi_animated = False
        st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    col_chart, col_breakdown = st.columns([3, 2])

    with col_chart:
        years = ["Year 1", "Year 2", "Year 3"]
        cum_val = [total_value * 0.70, total_value * 1.85, total_value * 3.1]
        cum_cost = [investment, investment * 1.90, investment * 2.80]
        fig_roi = go.Figure()
        fig_roi.add_trace(go.Bar(name="Cumulative Value", x=years, y=cum_val,
                                 marker_color=GR, opacity=.85))
        fig_roi.add_trace(go.Bar(name="Cumulative Investment", x=years, y=cum_cost,
                                 marker_color="#7B1E3E", opacity=.75))
        fig_roi.update_layout(barmode="group", plot_bgcolor="white", paper_bgcolor="white",
                               height=320, margin=dict(l=0, r=0, t=30, b=0),
                               title="3-year value vs. investment",
                               title_font_color=SN, font=dict(family="sans-serif"),
                               legend=dict(orientation="h", y=1.12),
                               yaxis_tickprefix="$", yaxis_tickformat=",.0f")
        st.plotly_chart(fig_roi, use_container_width=True)

    with col_breakdown:
        st.markdown('<div class="sh">Value drivers</div>', unsafe_allow_html=True)
        drivers = [
            ("Revenue from Freed Capacity", rev_capacity, SB),
            ("Client Retention Impact", retention_val, GR),
            ("Contract Risk Reduction", risk_reduction, GD),
            ("Platform Consolidation", platform_savings, OR),
        ]
        for label, val, color in drivers:
            pct = val / total_value * 100
            st.markdown(f"""<div style="margin-bottom:.8rem;">
              <div style="display:flex;justify-content:space-between;margin-bottom:3px;">
                <span style="font-size:.83rem;color:{SN};font-weight:600;">{label}</span>
                <span style="font-size:.83rem;font-weight:700;color:{color};">${val/1e6:.2f}M</span>
              </div>
              <div style="background:#E2EBF5;height:7px;border-radius:4px;">
                <div style="background:{color};width:{pct:.0f}%;height:7px;border-radius:4px;"></div>
              </div>
            </div>""", unsafe_allow_html=True)

        # Payback progress bar
        st.markdown(f'<div style="margin-top:1.2rem;margin-bottom:.4rem;font-weight:600;color:{SN};font-size:.88rem;">Payback period — {payback:.1f} months</div>', unsafe_allow_html=True)
        payback_pct = min(payback / 24 * 100, 100)
        st.markdown(f"""<div style="background:#E2EBF5;height:12px;border-radius:6px;overflow:hidden;">
          <div style="background:linear-gradient(90deg,{GR},{SB});width:{payback_pct:.0f}%;height:12px;border-radius:6px;"></div>
        </div>
        <div style="display:flex;justify-content:space-between;font-size:.73rem;color:#888;margin-top:3px;">
          <span>Month 0</span><span>Month 12</span><span>Month 24</span>
        </div>""", unsafe_allow_html=True)

        st.markdown(f"""<div style="background:{SN};color:white;border-radius:10px;padding:1rem 1.2rem;margin-top:1rem;">
          <div style="font-size:.73rem;color:{SB};font-weight:700;text-transform:uppercase;letter-spacing:.06em;">Snowflake investment</div>
          <div style="font-size:1.8rem;font-weight:800;margin:3px 0;">${investment:,.0f}/yr</div>
          <div style="font-size:.8rem;color:#8BA3B8;">
            ROI: <b style="color:{GR};">{roi_pct:.0f}%</b> · Payback: <b style="color:{GR};">{payback:.1f} months</b>
          </div>
        </div>""", unsafe_allow_html=True)

    st.markdown(f"""<div class="ib" style="margin-top:1.5rem;">
      <b style="color:{SN};">📞 Ready to build the business case together?</b><br>
      <span style="color:#5A6A7A;font-size:.87rem;">These estimates are grounded in Snowflake's Am Law 100 customer benchmarks. Our Sales Engineering team can run a tailored TCO/ROI analysis using Faegre Drinker's actual system costs, headcount, and utilization data.</span>
    </div>""", unsafe_allow_html=True)
