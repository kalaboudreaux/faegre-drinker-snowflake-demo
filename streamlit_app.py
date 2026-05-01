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
    "research_topic": "All",
    "simulated_client": "Global Pharma Corp",
    "share_revoked": False,
    "ai_func_result": None,
    "ai_func_running": False,
    "playground_response": None,
    "playground_model": "snowflake-arctic-instruct",
    "prediction_result": None,
    "doc_intel_result": None,
    "anomaly_matter": "All Matters — Portfolio View",
    "anomaly_explained": {},
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
  div[data-testid="stSidebarContent"] label,
  div[data-testid="stSidebarContent"] .stRadio label,
  div[data-testid="stSidebarContent"] p,
  div[data-testid="stSidebarContent"] span,
  div[data-testid="stSidebarContent"] div[role="radiogroup"] label span p {{
    color: white !important;
  }}
  div[data-testid="stSidebarContent"] div[role="radiogroup"] label {{
    color: white !important;
  }}
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
        "🤖 Legal AI Lab",
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
        "topic": "Litigation",
        "answer": "Under Delaware law, a **tortious interference** claim requires four elements:\n\n1. **Valid business relationship or expectancy** — not merely a hope, but a reasonable probability of future economic benefit\n2. **Knowledge** of the relationship by the defendant\n3. **Intentional interference** that induces a breach or termination\n4. **Resulting damages** to the plaintiff\n\nCourts emphasize the interference must be *improper* — competition alone is insufficient. Relevant cases include *WaveDivision Holdings v. Highland Capital Mgmt.* (Del. Ch. 2007) and *Lipson v. Anesthesia Services* (Del. Super. 1991).",
        "sources": ["WaveDivision Holdings v. Highland Capital Mgmt., 2007 Del. Ch. LEXIS 88", "Lipson v. Anesthesia Services, 1991 WL 280264 (Del. Super.)", "Restatement (Second) of Torts §766B"],
        "confidence": 97,
        "followups": ["What damages are recoverable for tortious interference?", "How does Delaware compare to New York on this claim?"],
    },
    "FTC pharmaceutical merger review trends 2024–2026": {
        "topic": "Regulatory",
        "answer": "FTC pharmaceutical merger review has **intensified significantly** from 2024–2026:\n\n- **Pipeline drug overlaps** — Commission now challenges deals where acquirer holds competing pipeline assets, even pre-approval\n- **Structural divestitures preferred** — behavioral remedies rejected in 8 of 11 challenged deals\n- **'Killer acquisition' scrutiny** — heightened review of large pharma acquiring early-stage competitors\n- **Data concentration theory** — novel harm theory where merger consolidates patient health data\n- **Second Request rate up 34% YoY** — broader investigation scope\n\nNew merger guidelines specific to life sciences emphasize *innovation competition* alongside traditional HHI concentration analysis.",
        "sources": ["FTC v. AbbVie Inc., No. 1:19-cv-02408 (D.D.C. 2024)", "FTC Pharmaceutical Merger Guidelines Update (2025)", "FTC Annual Competition Report 2025"],
        "confidence": 94,
        "followups": ["What divestitures has FTC required in recent pharma deals?", "How long do Second Requests typically take in life sciences M&A?"],
    },
    "Attorney-client privilege in internal investigations": {
        "topic": "Litigation",
        "answer": "Internal investigation privilege is governed by ***Upjohn Co. v. United States*** (449 U.S. 383, 1981), extending privilege beyond the 'control group' test. For privilege to apply:\n\n1. Communication made by an **employee to corporate counsel**\n2. Made at the **direction of corporate superiors**\n3. For the **purpose of obtaining legal advice**\n4. Employee must be **aware** the communication is for legal advice\n5. Must remain **confidential**\n\n**2024–2026 developments:** Several circuits have narrowed privilege for mixed business/legal purpose investigations. The DOJ's updated guidelines require privilege logs within 30 days. The 9th Circuit's *In re: Grand Jury* 'primary purpose' test has been adopted by additional circuits, creating new circuit splits.",
        "sources": ["Upjohn Co. v. United States, 449 U.S. 383 (1981)", "In re: Grand Jury, 23 F.4th 1088 (9th Cir. 2023)", "DOJ Internal Investigation Guidelines (2025 Update)"],
        "confidence": 96,
        "followups": ["Does privilege survive disclosure to outside auditors?", "How does work-product doctrine interact with internal investigation privilege?"],
    },
    "WARN Act requirements for 200+ employee reduction": {
        "topic": "Employment",
        "answer": "The **WARN Act (29 U.S.C. § 2101)** requires **60 days' advance written notice** for covered plant closings and mass layoffs. For a workforce reduction of 200+ employees:\n\n- **Covered employer threshold:** 100+ full-time employees (or 100+ who work 4,000+ hours/week combined)\n- **Mass layoff trigger:** 500 employees, OR 50–499 employees if they constitute ≥33% of the workforce\n- **Notice recipients:** Affected employees, state dislocated worker unit, and local government\n- **Key exceptions:** Faltering company, unforeseeable business circumstances, natural disaster\n\n**2025 state law note:** Several states (CA, NY, NJ, IL) have enacted mini-WARN statutes with *stricter* thresholds and longer notice periods. California requires 60 days regardless of percentage threshold for 50+ employees.",
        "sources": ["29 U.S.C. § 2101-2109 (WARN Act)", "20 C.F.R. Part 639 (DOL Implementing Regulations)", "Cal. Lab. Code § 1400 et seq. (Cal-WARN)"],
        "confidence": 98,
        "followups": ["What penalties apply for WARN Act violations?", "How do state mini-WARN statutes differ from federal requirements?"],
    },
    "Non-compete enforceability after FTC 2024 rule": {
        "topic": "Employment",
        "answer": "The **FTC's Non-Compete Clause Rule** (April 2024) sought to ban most non-competes nationwide, but its enforcement has been enjoined by federal courts:\n\n- **Ryan LLC v. FTC** (N.D. Tex. 2024) — nationwide injunction blocking the rule\n- The 5th Circuit is reviewing; Supreme Court involvement anticipated in 2026\n- **Current state:** Pre-rule state law controls enforceability\n\n**State-by-state snapshot:**\n- **California, Minnesota, Oklahoma, North Dakota** — near-total ban regardless of FTC rule status\n- **Illinois** (2022): Must be $75K+ salary; 14-day advance notice required\n- **New York** (2024): Pending legislation would ban for most employees\n- **Indiana** (Faegre Drinker home state): Enforced with reasonableness test on scope, duration, geography\n\nBest practice: assume non-competes are *unenforceable* in blue-collar/low-wage roles and document legitimate business interest for any executive-level restriction.",
        "sources": ["Ryan LLC v. FTC, No. 3:24-cv-00986-E (N.D. Tex. 2024)", "FTC Non-Compete Clause Rule, 89 Fed. Reg. 38342 (2024)", "Ind. Code § 24-2-3 (Indiana Trade Secrets Act)"],
        "confidence": 93,
        "followups": ["What makes a non-compete 'reasonable' under Indiana law?", "Can trade secret protections substitute for unenforceable non-competes?"],
    },
    "HSR filing thresholds and waiting periods 2026": {
        "topic": "M&A",
        "answer": "**HSR Act filing thresholds** (revised annually by FTC, effective February 2026):\n\n| Test | Threshold |\n|---|---|\n| Size of transaction | **$119.5M** (up from $111.4M in 2025) |\n| Size of person (larger) | **$239.0M** |\n| Size of person (smaller) | **$23.9M** |\n\n**Waiting periods:**\n- Standard: **30 calendar days** from filing\n- Cash tender offers / bankruptcy: **15 days**\n- Early termination: Suspended since 2021; FTC restarting on case-by-case basis in 2026\n\n**2025–2026 changes:** New HSR rules effective February 2025 require extensive *deal rationale narratives*, labor market analysis, and draft agreements — significantly increasing filing preparation time (average now 6–8 weeks for complex deals vs. 2–3 weeks previously).",
        "sources": ["16 C.F.R. Part 801 (HSR Rules)", "FTC HSR Threshold Adjustments (Jan. 2026)", "FTC Final Rule: Revised HSR Form, 89 Fed. Reg. 89216 (2025)"],
        "confidence": 96,
        "followups": ["What's included in the new HSR deal rationale narrative requirement?", "Which transactions are exempt from HSR filing?"],
    },
    "Patent claim construction — means-plus-function claims": {
        "topic": "IP",
        "answer": "**Means-plus-function (MPF) claims** under **35 U.S.C. § 112(f)** allow claiming a function without structural limitation, but are construed narrowly:\n\n**Construction standard:**\n1. Claim must use 'means for' language (or functional language without structure)\n2. Scope limited to **corresponding structure** disclosed in the specification + **equivalents**\n3. If no corresponding structure → claim is **indefinite** and invalid\n\n**Key Federal Circuit trends 2024–2026:**\n- *Dyfan v. Target Corp.* (Fed. Cir. 2022) — software MPF claims require algorithm disclosure\n- Heightened definiteness scrutiny for AI/ML patent claims where 'neural network' without architectural detail may be insufficient structure\n- **Prosecution strategy:** Avoid MPF language; disclose multiple structural embodiments; include pseudocode for software-implemented functions\n\n**Litigation risk:** MPF claims are frequently invalidated on § 112 indefiniteness grounds — assess exposure in any Freedom to Operate analysis.",
        "sources": ["35 U.S.C. § 112(f)", "Dyfan, LLC v. Target Corp., 28 F.4th 1360 (Fed. Cir. 2022)", "Williamson v. Citrix Online LLC, 792 F.3d 1339 (Fed. Cir. 2015)"],
        "confidence": 95,
        "followups": ["How should we disclose algorithms in patent specifications?", "What's the risk of MPF invalidity in an existing portfolio?"],
    },
    "HIPAA minimum necessary standard for litigation holds": {
        "topic": "Regulatory",
        "answer": "The **HIPAA Minimum Necessary Standard (45 C.F.R. § 164.502(b))** requires covered entities to make reasonable efforts to limit PHI use/disclosure to the **minimum necessary** to accomplish the intended purpose.\n\n**Litigation hold intersection:**\n- A litigation hold does *not* automatically satisfy the minimum necessary standard\n- **Permitted disclosures for litigation:** Healthcare operations, required by law, judicial/administrative proceeding\n- For production in litigation: subpoena + satisfactory assurance OR HIPAA-compliant court order required\n\n**2025 OCR guidance:** OCR has clarified that law firms acting as Business Associates must flow down minimum necessary obligations. Litigation counsel receiving PHI under a BAA must:\n1. Limit internal circulation to attorneys/staff with case-specific need\n2. Implement technical safeguards (encryption at rest/transit)\n3. Return or destroy PHI at matter conclusion\n4. Report breaches within **60 days** of discovery\n\n**Penalty exposure:** Tier 4 violations — up to **$1.9M per violation category per year** (2026 adjusted figure).",
        "sources": ["45 C.F.R. § 164.502(b) (HIPAA Minimum Necessary)", "45 C.F.R. § 164.512(e) (Disclosures for Judicial Proceedings)", "OCR Guidance on Business Associates in Litigation (2025)"],
        "confidence": 97,
        "followups": ["What must a BAA include when engaging outside litigation counsel?", "How do we handle HIPAA when responding to a subpoena for medical records?"],
    },
}

ANALYST_QUERIES = {
    "Which matters are over budget?": {
        "sql": "SELECT matter_id, client, fees_billed, budget,\n  fees_billed - budget AS over_by,\n  ROUND(fees_billed / budget * 100, 1) AS pct_budget\nFROM matter_portfolio\nWHERE fees_billed > budget\nORDER BY over_by DESC;",
        "cols": ["Matter ID", "Client", "Fees Billed", "Budget", "Over By", "% of Budget"],
        "rows": [
            ["M-2026-0089", "National Retail Group", "$384,000", "$350,000", "$34,000", "109.7%"],
            ["M-2025-1847", "HealthSystem Partners", "$1,806,000", "$1,800,000", "$6,000", "100.3%"],
        ],
    },
    "Who are the top 3 partners by fees billed?": {
        "sql": "SELECT partner, practice_group,\n  COUNT(*) AS active_matters,\n  SUM(fees_billed) AS total_fees\nFROM matter_portfolio\nGROUP BY partner, practice_group\nORDER BY total_fees DESC\nLIMIT 3;",
        "cols": ["Partner", "Practice", "Active Matters", "Total Fees Billed"],
        "rows": [
            ["Michelle Park", "Healthcare", "1", "$1,806,000"],
            ["James Holloway", "Labor & Employment", "1", "$883,500"],
            ["Amanda Foster", "Energy", "1", "$501,000"],
        ],
    },
    "Show me all litigation matters and budget status": {
        "sql": "SELECT matter_id, client, partner,\n  fees_billed, budget, status\nFROM matter_portfolio\nWHERE matter_type = 'Litigation'\nORDER BY fees_billed DESC;",
        "cols": ["Matter ID", "Client", "Partner", "Fees Billed", "Budget", "Status"],
        "rows": [
            ["M-2026-0042", "Midwest Manufacturing", "James Holloway", "$883,500", "$890,000", "At Risk"],
            ["M-2026-0134", "Energy Holdings LLC", "Amanda Foster", "$501,000", "$600,000", "On Track"],
        ],
    },
    "Which matters have billing velocity above budget pace?": {
        "sql": "SELECT matter_id, client, partner,\n  hours_billed,\n  ROUND(fees_billed / DATEDIFF('day', open_date, CURRENT_DATE) * 30, 0)\n    AS monthly_burn_rate,\n  budget,\n  status\nFROM matter_portfolio\nWHERE status IN ('At Risk', 'Over Budget')\nORDER BY monthly_burn_rate DESC;",
        "cols": ["Matter ID", "Client", "Partner", "Hours", "Monthly Burn Rate", "Budget", "Status"],
        "rows": [
            ["M-2025-1847", "HealthSystem Partners", "Michelle Park", "1,204", "$180,600/mo", "$1,800,000", "Over Budget"],
            ["M-2026-0042", "Midwest Manufacturing", "James Holloway", "589", "$88,350/mo", "$890,000", "At Risk"],
            ["M-2026-0089", "National Retail Group", "Lisa Tran", "256", "$48,000/mo", "$350,000", "Over Budget"],
        ],
    },
    "Break down fees by practice group": {
        "sql": "SELECT practice_group,\n  COUNT(*) AS matters,\n  SUM(hours_billed) AS total_hours,\n  SUM(fees_billed) AS total_fees,\n  ROUND(AVG(fees_billed / budget * 100), 1) AS avg_budget_pct\nFROM matter_portfolio\nGROUP BY practice_group\nORDER BY total_fees DESC;",
        "cols": ["Practice Group", "Matters", "Total Hours", "Total Fees", "Avg Budget %"],
        "rows": [
            ["Healthcare", "1", "1,204", "$1,806,000", "100.3%"],
            ["Labor & Employment", "2", "734", "$1,028,500", "93.6%"],
            ["Energy", "1", "334", "$501,000", "83.5%"],
            ["Intellectual Property", "1", "256", "$384,000", "109.7%"],
            ["Life Sciences", "1", "412", "$618,000", "88.3%"],
            ["Financial Services", "1", "177", "$265,500", "66.4%"],
            ["Private Equity", "1", "88", "$132,000", "66.0%"],
        ],
    },
}

# ── Cortex AI Lab data ────────────────────────────────────────────────────────

AI_FUNCTIONS = {
    "AI_SUMMARIZE": {
        "desc": "Summarize documents into concise executive briefs",
        "sql_tmpl": "SELECT AI_SUMMARIZE(document_text) AS summary\nFROM legal_documents\nWHERE doc_id = '{doc_id}';",
        "docs": {
            "Global Pharma MSA (47 pages)": {
                "input": "This Master Services Agreement ('Agreement') is entered into as of March 1, 2024, between Global Pharma Corp ('Client') and Faegre Drinker Biddle & Reath LLP ('Firm'). The Firm agrees to provide legal services including regulatory advisory, patent prosecution, and litigation support. Total engagement value: $4,200,000 over three years. Termination requires 90 days written notice. The liability cap is $5,000,000 or 12 months of fees, whichever is greater. Auto-renewal applies annually with a 60-day opt-out window. The agreement is governed by the laws of Delaware...",
                "output": "**Executive Summary — Global Pharma Corp MSA**\n\n- **Scope:** Full-service legal engagement covering regulatory, patent, and litigation\n- **Term:** March 2024 – February 2027 (3 years, auto-renewing)\n- **Value:** $4,200,000 total · $1.4M/year\n- **Key Protections:** $5M liability cap · 90-day termination notice · 3-year confidentiality post-term\n- **Risk Flags:** IP ownership clause ambiguous for AI-generated work product; liability cap below Am Law 100 peer benchmark for this contract size\n- **Action Required:** Renewal opt-out window opens December 31, 2026",
            },
            "Midwest Manufacturing Engagement Letter": {
                "input": "Engagement Letter for litigation representation in Midwest Manufacturing Inc. v. [Adverse Party]. Faegre Drinker Biddle & Reath LLP will represent Midwest Manufacturing Inc. in all aspects of the pending litigation in the U.S. District Court for the Southern District of Indiana. Billing is hourly at partner rates of $895–$1,150/hour. Estimated matter value: $890,000. A motion to dismiss is due April 30, 2026. No liability cap is specified...",
                "output": "**Executive Summary — Midwest Manufacturing Engagement Letter**\n\n- **Matter Type:** Active litigation · U.S. District Court, S.D. Indiana\n- **Billing:** Hourly · Partner rates $895–$1,150/hr · Est. $890,000\n- **Immediate Deadline:** Motion to dismiss due **April 30, 2026** ⚠️\n- **Risk Exposure:** No liability cap specified — unusual for complex litigation\n- **Privilege:** Indefinite attorney-client privilege applies\n- **Recommendation:** Formalize liability cap language; document all time entries with narrative detail given prior billing dispute history",
            },
        },
    },
    "AI_CLASSIFY": {
        "desc": "Automatically tag and categorize legal documents and matters",
        "sql_tmpl": "SELECT matter_id, matter_description,\n  AI_CLASSIFY(matter_description,\n    ['Litigation','M&A','Regulatory','Employment',\n     'IP/Patent','Corporate','High Priority','Standard']\n  ) AS classifications\nFROM matters\nWHERE status = 'Active';",
        "docs": {
            "Active Matter Portfolio": {
                "input": "M-2026-0041: Regulatory approval filing for new biologic drug, FDA interactions, global patent portfolio review\nM-2026-0042: Commercial litigation, breach of contract, jury trial scheduled\nM-2025-1847: Cross-border merger, $2.4B enterprise value, HSR filing, 12 jurisdictions\nM-2026-0089: Patent infringement action, inter partes review petition, PTAB proceedings\nM-2026-0156: Wrongful termination claim, class action risk, WARN Act analysis",
                "output": "| Matter | Classifications | Confidence |\n|--------|----------------|------------|\n| M-2026-0041 | `Regulatory` `Life Sciences` `Standard` | 96% |\n| M-2026-0042 | `Litigation` `Commercial` `High Priority` | 98% |\n| M-2025-1847 | `M&A` `Cross-Border` `High Priority` | 99% |\n| M-2026-0089 | `IP/Patent` `Litigation` `High Priority` | 97% |\n| M-2026-0156 | `Employment` `Class Action Risk` `High Priority` | 94% |\n\n**3 of 5 matters classified as High Priority** — review partner capacity allocation",
            },
            "Incoming Client Intake Forms": {
                "input": "Intake 1: Client needs help with non-compete agreement dispute, Indiana employee\nIntake 2: Client seeks advice on HIPAA violation notice received from OCR\nIntake 3: Startup company requesting term sheet review and Series A documentation\nIntake 4: Client received EEOC charge, needs response within 30 days",
                "output": "| Intake | Practice Area | Priority | Assigned Group |\n|--------|--------------|----------|----------------|\n| Intake 1 | `Employment` `Non-Compete` | Standard | Labor & Employment |\n| Intake 2 | `Regulatory` `Healthcare` `HIPAA` | **High** | Healthcare |\n| Intake 3 | `Corporate` `Venture/Startup` | Standard | Private Equity |\n| Intake 4 | `Employment` `EEOC` | **High — 30d deadline** | Labor & Employment |\n\n**2 high-priority intakes require immediate partner review**",
            },
        },
    },
    "AI_SENTIMENT": {
        "desc": "Analyze tone and sentiment in client communications and feedback",
        "sql_tmpl": "SELECT client_id, message_date,\n  AI_SENTIMENT(message_text) AS sentiment,\n  sentiment:score::FLOAT AS score,\n  sentiment:reasoning::STRING AS reasoning\nFROM client_communications\nORDER BY message_date DESC\nLIMIT 50;",
        "docs": {
            "Client Satisfaction Survey Responses": {
                "input": "Response 1 (Global Pharma): 'The team has been incredibly responsive. Sarah Chen's work on the FDA filing was exceptional — she anticipated every issue before it became a problem.'\nResponse 2 (Midwest Manufacturing): 'Billing is hard to follow. We keep getting invoices with vague descriptions like \"legal research\" for 8 hours. Need more detail.'\nResponse 3 (TechStart): 'Very happy overall. Quick turnaround on the term sheet. A few redlines were more aggressive than expected but nothing deal-breaking.'\nResponse 4 (HealthSystem): 'The M&A closing took 3 weeks longer than projected. Communication during the final stretch was poor. We had to chase updates.'",
                "output": "| Client | Sentiment | Score | Key Signal |\n|--------|-----------|-------|------------|\n| Global Pharma | 😊 **Very Positive** | 94/100 | Attorney performance praised by name — expansion opportunity |\n| Midwest Manufacturing | 😟 **Negative** | 31/100 | ⚠️ Billing transparency issue — churn risk if unresolved |\n| TechStart Ventures | 🙂 **Positive** | 72/100 | Minor concern on aggressiveness — monitor |\n| HealthSystem Partners | 😠 **Negative** | 28/100 | ⚠️ Timeline and communication failures — escalation warranted |\n\n**Action Required:** 2 clients flagged for immediate partner outreach",
            },
            "Post-Matter Close Feedback": {
                "input": "Matter M-2025-1847 close: 'The deal got done, which is what mattered. The team knew the healthcare regulatory angle cold. Would have liked more proactive status updates but the outcome was excellent.'\nMatter M-2026-0042 close: 'Still ongoing but very pleased with the motion strategy. James really understands the industrial manufacturing space.'",
                "output": "| Matter | Sentiment | Score | Insight |\n|--------|-----------|-------|--------|\n| M-2025-1847 | 🙂 **Positive** | 74/100 | Outcome praised · Communication gap noted — process improvement opportunity |\n| M-2026-0042 | 😊 **Very Positive** | 88/100 | Strong domain expertise recognition — reference client potential |\n\n**Overall portfolio NPS signal: 71** — above Am Law 100 median of 62",
            },
        },
    },
    "AI_EXTRACT": {
        "desc": "Pull structured data from unstructured contract text",
        "sql_tmpl": "SELECT doc_id, filename,\n  AI_EXTRACT(document_text, [\n    'parties', 'effective_date', 'governing_law',\n    'liability_cap', 'termination_notice',\n    'auto_renewal', 'confidentiality_period'\n  ]) AS extracted_fields\nFROM contracts\nWHERE status = 'Active';",
        "docs": {
            "NDA Clause Block": {
                "input": "This Non-Disclosure Agreement is entered into as of January 15, 2025, between TechStart Ventures LLC, a Delaware limited liability company ('Disclosing Party'), and Faegre Drinker Biddle & Reath LLP ('Receiving Party'). The Receiving Party agrees to maintain strict confidentiality for a period of five (5) years following termination of this Agreement. This Agreement shall be governed by the laws of the State of New York. Either party may terminate with thirty (30) days written notice...",
                "output": '```json\n{\n  "parties": [\n    "TechStart Ventures LLC (Disclosing Party)",\n    "Faegre Drinker Biddle & Reath LLP (Receiving Party)"\n  ],\n  "effective_date": "January 15, 2025",\n  "governing_law": "New York",\n  "liability_cap": null,\n  "termination_notice": "30 days written notice",\n  "auto_renewal": false,\n  "confidentiality_period": "5 years post-termination",\n  "_confidence": 0.97,\n  "_model": "snowflake-arctic-instruct",\n  "_latency_ms": 412\n}\n```',
            },
            "Vendor Services Agreement": {
                "input": "This Vendor Services Agreement ('Agreement'), effective June 1, 2025, is made between LegalTech Solutions Inc. ('Vendor') and Faegre Drinker Biddle & Reath LLP ('Client'). Services shall be provided for an annual fee of $240,000. The Agreement automatically renews for successive one-year terms unless either party provides sixty (60) days written notice of non-renewal. Vendor's total liability shall not exceed the fees paid in the preceding twelve (12) months. The Agreement shall be governed by the laws of the State of Minnesota...",
                "output": '```json\n{\n  "parties": [\n    "LegalTech Solutions Inc. (Vendor)",\n    "Faegre Drinker Biddle & Reath LLP (Client)"\n  ],\n  "effective_date": "June 1, 2025",\n  "governing_law": "Minnesota",\n  "liability_cap": "$240,000 (12 months fees)",\n  "termination_notice": "60 days written notice of non-renewal",\n  "auto_renewal": true,\n  "confidentiality_period": null,\n  "annual_fee": "$240,000",\n  "_confidence": 0.99,\n  "_model": "snowflake-arctic-instruct",\n  "_latency_ms": 388\n}\n```',
            },
        },
    },
    "AI_FILTER": {
        "desc": "Filter large document sets to find exactly what matches your criteria",
        "sql_tmpl": "SELECT doc_id, filename, practice_area,\n  AI_FILTER(\n    document_text,\n    'contains an indemnification clause that favors the client'\n  ) AS matches_filter\nFROM contract_corpus\nWHERE status = 'Active'\n  AND matches_filter = TRUE;",
        "docs": {
            "Contract Corpus — Indemnification Screen": {
                "input": "Screening 847 active contracts for: 'contains indemnification clause that creates unlimited or uncapped exposure for the firm'\n\nContracts scanned: MSA-2024-0142, ENG-2026-0023, VEN-2025-1105, NDA-2025-0891, MSA-2023-0088, ENG-2025-1204, VEN-2024-0934, NDA-2024-0776 [+ 839 more]...",
                "output": "**AI_FILTER Results — 847 contracts scanned in 2.1 seconds**\n\n✅ **Matches found: 23 contracts**\n\n| Contract | Client | Exposure Type | Risk |\n|----------|--------|--------------|------|\n| ENG-2026-0023 | Midwest Manufacturing | No liability cap — unlimited exposure | 🔴 High |\n| MSA-2023-0088 | Legacy Pharma Co. | Mutual indemnification, broad IP scope | 🟠 Medium |\n| ENG-2025-1204 | Industrial Corp | Third-party indemnification, broad | 🔴 High |\n| VEN-2024-0934 | Cloud Vendor Inc. | Data breach indemnification uncapped | 🔴 High |\n| [+19 more] | ... | ... | ... |\n\n**824 contracts passed filter** — no uncapped indemnification exposure\n**Estimated review time saved: 423 attorney hours** vs. manual review",
            },
            "Discovery Document Review — Privilege Screen": {
                "input": "Screening 12,847 documents produced in discovery for: 'contains attorney-client privileged communication or attorney work product'\n\nDocuments: email corpus, internal memos, draft agreements, board minutes from 2022–2026",
                "output": "**AI_FILTER Results — 12,847 documents screened in 8.3 seconds**\n\n🔐 **Privilege flags: 1,847 documents**\n- Attorney-client communications: 1,203\n- Work product doctrine: 512\n- Dual-purpose (business + legal): 132\n\n⚠️ **Inadvertent disclosure risk: 47 documents** already produced — immediate clawback recommended\n\n✅ **10,953 documents clear for production**\n\n**Attorney review time saved: ~2,140 hours** · **Cost savings: ~$1.9M** at partner review rates",
            },
        },
    },
}

PLAYGROUND_TEMPLATES = {
    "Draft a risk memo": {
        "model_hint": "snowflake-arctic-instruct",
        "prompt": "You are a senior partner at Faegre Drinker Biddle & Reath LLP. Draft a concise risk memorandum for the following situation:\n\nClient: Global Pharma Corp\nSituation: The client's Master Services Agreement with our firm auto-renews on January 31, 2027. The current liability cap of $5,000,000 is below the Am Law 100 benchmark for a $4.2M contract. Additionally, the IP ownership clause does not address AI-generated work product.\n\nFormat as a formal memo with: Summary, Key Risks (bullet points), Recommended Actions, and Timeline.",
        "response": "**MEMORANDUM**\n\n**TO:** File — Global Pharma Corp Matter Team  \n**FROM:** Senior Partner, Faegre Drinker Biddle & Reath LLP  \n**DATE:** May 1, 2026  \n**RE:** MSA Risk Assessment & Renewal Strategy — Global Pharma Corp\n\n---\n\n**SUMMARY**\n\nThe Global Pharma Corp Master Services Agreement (MSA-2024-0142) presents two material risk areas requiring action before the January 31, 2027 auto-renewal window closes on December 31, 2026.\n\n**KEY RISKS**\n\n- **Liability Cap Exposure:** Current cap of $5,000,000 represents approximately 119% of annual fees — the Am Law 100 benchmark for this contract size is 200–250% of annual fees ($2.8M–$3.5M). In a worst-case malpractice scenario, the firm's net exposure could exceed coverage.\n- **AI Work Product Gap:** The agreement predates the firm's AI-assisted drafting workflows. No clause allocates ownership of AI-generated deliverables, creating ambiguity if the client claims ownership of AI-assisted memoranda, research summaries, or contract drafts.\n- **Auto-Renewal Risk:** The 60-day opt-out window opens October 31, 2026. Missing this window locks the firm into 2027 terms without renegotiation leverage.\n\n**RECOMMENDED ACTIONS**\n\n1. Initiate renegotiation discussion with GPC in-house counsel no later than **September 1, 2026** — position as a 'standard annual review'\n2. Propose revised liability cap at **$8,400,000** (200% of annual fees) with mutual indemnification carve-outs\n3. Add AI work product clause: *'Deliverables produced with AI assistance remain Firm work product; Client receives a perpetual, non-exclusive license to use for the specific matter'*\n4. Review force majeure clause — current version predates 2024 cyber incident standards\n\n**TIMELINE**\n\n| Milestone | Date |\n|-----------|------|\n| Partner review of this memo | May 15, 2026 |\n| Draft renegotiation proposal | June 30, 2026 |\n| Open discussion with GPC | September 1, 2026 |\n| Opt-out / renegotiation deadline | **December 31, 2026** |\n| Auto-renewal effective | January 31, 2027 |",
    },
    "Summarize this clause": {
        "model_hint": "mistral-large2",
        "prompt": "Summarize the following contract clause in plain English for a non-lawyer client. Identify: (1) what it means, (2) what protections it provides, and (3) any risks or concerns.\n\nClause: 'In no event shall either party be liable to the other for any indirect, incidental, special, exemplary, punitive, or consequential damages, including lost profits, loss of data, loss of goodwill, service interruption, computer damage, or system failure, or the cost of substitute services arising out of or in connection with this Agreement or from the use of or inability to use the Services, whether based on warranty, contract, tort (including negligence), product liability, or any other legal theory, and whether or not the party has been advised of the possibility of such damages, even if a limited remedy set forth herein is found to have failed of its essential purpose.'",
        "response": "**Plain English Summary — Limitation of Liability Clause**\n\n**What It Means:**\nThis clause is a 'no consequential damages' provision. It says that if something goes wrong under this contract, neither side can sue the other for indirect losses — things like lost profits, lost business opportunities, or the cost of finding a replacement vendor.\n\n**What Protections It Provides:**\n- Caps the firm's exposure to direct, out-of-pocket losses only\n- Prevents a client from claiming they lost $10M in business because of a legal error, even if that were arguably true\n- Standard in most commercial contracts — courts generally enforce them\n\n**Risks & Concerns:**\n\n⚠️ **For the Client (you):** If the firm makes a serious error that costs your business significant revenue or opportunities, you can only recover the direct value of the services themselves — not your downstream losses.\n\n⚠️ **Carve-out gap:** This clause does not appear to carve out gross negligence, fraud, or willful misconduct. Best practice is to explicitly exclude these — our standard form does include such carve-outs. Recommend confirming this clause matches your executed agreement.\n\n✅ **Bottom line:** Standard and reasonable for a law firm engagement, but confirm the carve-outs are in place before signing.",
    },
    "Identify regulatory issues": {
        "model_hint": "llama3-70b",
        "prompt": "Review the following business situation and identify all potential regulatory, compliance, and legal issues. For each issue, rate severity (High/Medium/Low) and suggest the relevant legal framework.\n\nSituation: A healthcare system (HealthSystem Partners) is planning to:\n1. Acquire a regional hospital chain (12 hospitals, 3 states)\n2. Implement an AI diagnostic tool that analyzes patient medical records\n3. Share anonymized patient outcome data with a pharmaceutical research partner\n4. Reduce workforce by approximately 400 employees across the combined organization",
        "response": "**Regulatory Issue Analysis — HealthSystem Partners Expansion**\n\n---\n\n**Issue 1: HSR Antitrust Filing** 🔴 HIGH\n- *Framework:* Hart-Scott-Rodino Act · FTC/DOJ Merger Review\n- 12-hospital acquisition almost certainly exceeds HSR thresholds ($119.5M, 2026)\n- Healthcare mergers face heightened FTC scrutiny — Second Request rate elevated\n- FTC has challenged hospital mergers under 'any-to-any' competition theory\n- *Timeline risk:* 30-day waiting period minimum; potential 12–18 month investigation\n\n**Issue 2: State CON (Certificate of Need) Laws** 🔴 HIGH\n- *Framework:* State health planning statutes (varies by state)\n- 3-state footprint — all may require CON approval before acquisition closes\n- CON proceedings can take 6–18 months and involve public hearings\n- *Action:* Identify which states and begin pre-filing consultations immediately\n\n**Issue 3: AI Diagnostic Tool — FDA Regulation** 🔴 HIGH\n- *Framework:* FDA Software as a Medical Device (SaMD) · 21 CFR Part 820\n- AI tool analyzing medical records for diagnostic purposes likely qualifies as a Class II or III medical device\n- May require 510(k) clearance or De Novo authorization before deployment\n- *2025 update:* FDA's AI/ML Action Plan requires change control procedures for adaptive AI\n\n**Issue 4: HIPAA Data Sharing with Pharma Partner** 🟠 MEDIUM-HIGH\n- *Framework:* HIPAA Privacy Rule · 45 CFR § 164.514 (De-identification)\n- 'Anonymized' data must meet HIPAA's Safe Harbor or Expert Determination standard\n- Research sharing requires a Data Use Agreement (DUA) and IRB approval\n- State laws (e.g., California CMIA) may be stricter than HIPAA\n\n**Issue 5: WARN Act — 400-Employee Reduction** 🟠 MEDIUM\n- *Framework:* Federal WARN Act · State mini-WARN statutes\n- 400 employees across 3 states — federal WARN likely triggered\n- **60 days advance written notice required** to employees and state agencies\n- Check state mini-WARN laws — California, Illinois have stricter requirements\n- *Risk:* Failure = back pay + benefits for 60 days per affected employee\n\n**Issue 6: Medical Staff Credentialing Integration** 🟡 LOW-MEDIUM\n- *Framework:* Joint Commission Standards · State medical practice acts\n- Acquired hospital medical staff must be re-credentialed under acquiring entity's bylaws\n- Typically 6–12 month process; cannot be rushed without accreditation risk",
    },
    "Write a client update": {
        "model_hint": "snowflake-arctic-instruct",
        "prompt": "Write a professional client status update email for the following matter:\n\nClient: Midwest Manufacturing Inc.\nMatter: Commercial litigation, breach of contract\nPartner: James Holloway\nKey update: The court denied opposing counsel's motion to continue the April 30 deadline for our motion to dismiss. Our motion is on track. We've identified three strong grounds for dismissal. Discovery requests are due from opposing counsel by May 15.\n\nTone: Confident, professional, concise. The client has been anxious about this matter.",
        "response": "**Subject:** Matter Update — Motion to Dismiss Status · M-2026-0042\n\nDear [Client Contact],\n\nI'm writing with a positive update on your matter.\n\n**Motion to Dismiss — On Track**\n\nThe court denied opposing counsel's request to extend the briefing deadline, confirming our April 30 filing date stands. Our team has completed its analysis and identified **three strong independent grounds for dismissal** — any one of which would resolve this matter in your favor at the outset.\n\nWe are finalizing the brief this week and remain confident in our position.\n\n**What to Expect Next**\n\n- **April 30:** We file our motion to dismiss\n- **May 15:** Opposing counsel's discovery requests are due — we'll review and respond within the required timeframe\n- **~60 days post-filing:** Court typically rules on motions of this type\n\n**Our Assessment**\n\nThe case is proceeding well. The court's denial of the continuance request reflects favorably — courts are often skeptical when parties seek last-minute delays without cause.\n\nPlease don't hesitate to call me directly if you have questions. We'll send a comprehensive strategy memo by end of week.\n\nBest regards,\n\nJames Holloway\nPartner, Labor & Employment\nFaegre Drinker Biddle & Reath LLP",
    },
    "Compare two contracts": {
        "model_hint": "mistral-large2",
        "prompt": "Compare the following two termination clauses and identify: (1) key differences, (2) which is more favorable to the law firm, and (3) any negotiation recommendations.\n\nClause A (Current MSA): 'Either party may terminate this Agreement upon ninety (90) days prior written notice to the other party. Upon termination, Client shall pay all fees for services rendered through the termination date.'\n\nClause B (Proposed revision from client): 'Client may terminate this Agreement at any time upon fifteen (15) days written notice. Firm may terminate only for cause, with thirty (30) days written notice and opportunity to cure. Upon termination by Client, no further fees shall accrue after the notice date, regardless of work in progress.'",
        "response": "**Contract Comparison — Termination Clauses**\n\n---\n\n**Key Differences**\n\n| Factor | Clause A (Current) | Clause B (Proposed) |\n|--------|-------------------|---------------------|\n| Client notice period | 90 days | **15 days** |\n| Firm termination right | Yes — 90 days | **For cause only** |\n| Work-in-progress fees | Paid through termination | **Cut off at notice date** |\n| Balance of power | Symmetric | **Client-favored** |\n\n---\n\n**Analysis: Clause B is significantly less favorable to the firm**\n\n🔴 **Critical concern — 15-day client termination:** This gives the client a near-instant exit at any time. On a $4.2M engagement with ongoing work, the firm could have substantial unbilled WIP that becomes unrecoverable if the client terminates immediately before a billing cycle.\n\n🔴 **'No further fees after notice date':** This is highly unusual and potentially exposes the firm to significant losses. If we're mid-discovery, mid-brief, or mid-deal on a 15-day notice, partners may have invested hundreds of hours that cannot be billed.\n\n🟠 **Firm termination 'for cause only':** Removes the firm's right to exit a problematic client relationship — important safety valve for conflicts, non-payment, or reputational risk.\n\n---\n\n**Negotiation Recommendations**\n\n1. **Counter-propose 45 days** (client) / 60 days (firm) — a reasonable compromise\n2. **Reject the WIP cutoff:** Propose *'Client shall pay for all work performed through the date services are wound down, not to exceed 30 days post-notice'*\n3. **Preserve firm termination right:** Propose symmetric termination with 'for cause' triggering immediate termination rights for both parties (non-payment, conflict, material breach)\n4. **Add transition fee:** If client terminates within first 12 months, propose a transition assistance fee of 30 days of average monthly billing",
    },
}

PREDICTION_TABLE = {
    ("Litigation", "Low"): {"favorable_pct": 72, "budget_overrun_risk": 28, "timeline_months": "8–14", "factors": [("Opposing counsel tier", 38), ("Case complexity score", 25), ("Jurisdiction / judge assignment", 22), ("Prior similar matters won", 15)], "actions": ["File early dispositive motions to test theory", "Engage expert witnesses within 60 days of case opening", "Set client expectations: litigation timelines frequently extend 20–30%"]},
    ("Litigation", "High"): {"favorable_pct": 54, "budget_overrun_risk": 67, "timeline_months": "18–36", "factors": [("Case complexity score", 42), ("Opposing counsel tier", 31), ("Jurisdiction / judge assignment", 17), ("Client cooperation history", 10)], "actions": ["Schedule early settlement evaluation at 90 days", "Establish weekly budget checkpoints with client", "Consider mediation referral at 6-month mark"]},
    ("M&A", "Low"): {"favorable_pct": 91, "budget_overrun_risk": 15, "timeline_months": "3–5", "factors": [("Deal complexity / structure", 44), ("Regulatory footprint", 33), ("Target data room quality", 13), ("Counterparty counsel experience", 10)], "actions": ["Initiate HSR analysis immediately", "Assign dedicated data room coordinator", "Pre-schedule closing checklist review at week 6"]},
    ("M&A", "High"): {"favorable_pct": 78, "budget_overrun_risk": 52, "timeline_months": "8–18", "factors": [("Regulatory footprint", 48), ("Deal complexity / structure", 29), ("Cross-border jurisdictions", 15), ("Target data room quality", 8)], "actions": ["Engage antitrust counsel in parallel from day 1", "Flag CON requirements in all target states", "Build 20% budget contingency into engagement estimate"]},
    ("Regulatory", "Low"): {"favorable_pct": 83, "budget_overrun_risk": 22, "timeline_months": "4–9", "factors": [("Agency relationship quality", 40), ("Regulatory precedent clarity", 35), ("Filing completeness", 15), ("Political / policy environment", 10)], "actions": ["Request pre-submission meeting with agency", "Assign regulatory specialist with agency experience", "Prepare for standard 6-month review cycle"]},
    ("Regulatory", "High"): {"favorable_pct": 61, "budget_overrun_risk": 58, "timeline_months": "12–24", "factors": [("Regulatory precedent clarity", 45), ("Agency relationship quality", 28), ("Political / policy environment", 17), ("Filing completeness", 10)], "actions": ["Engage former agency counsel for regulatory intelligence", "Build parallel strategy: approval + litigation backup", "Set quarterly budget reviews with contingency triggers"]},
    ("Employment", "Low"): {"favorable_pct": 79, "budget_overrun_risk": 18, "timeline_months": "3–8", "factors": [("Documentation quality", 46), ("Jurisdiction / state law", 30), ("Claims scope", 14), ("HR process compliance", 10)], "actions": ["Audit personnel file documentation immediately", "Assess class action certification risk early", "Engage employment practices expert if needed"]},
    ("Employment", "High"): {"favorable_pct": 48, "budget_overrun_risk": 71, "timeline_months": "12–30", "factors": [("Claims scope", 39), ("Documentation quality", 28), ("Jurisdiction / state law", 21), ("Media / PR exposure", 12)], "actions": ["Evaluate early resolution vs. litigation economics", "Engage crisis communications if public exposure risk", "Build class action defense team immediately"]},
    ("IP/Patent", "Low"): {"favorable_pct": 68, "budget_overrun_risk": 31, "timeline_months": "12–18", "factors": [("Claim construction strength", 44), ("Prior art landscape", 32), ("Validity of asserted patents", 14), ("Damages theory", 10)], "actions": ["Conduct thorough prior art search within 30 days", "File IPR petition if validity is in question", "Establish claim construction strategy early"]},
    ("IP/Patent", "High"): {"favorable_pct": 52, "budget_overrun_risk": 63, "timeline_months": "24–48", "factors": [("Prior art landscape", 40), ("Claim construction strength", 30), ("PTAB / IPR exposure", 20), ("Damages theory", 10)], "actions": ["File inter partes review petition to challenge validity", "Engage technical expert with domain-specific credentials", "Budget for Markman hearing and potential PTAB proceedings"]},
}

DOC_INTEL_SAMPLES = {
    "NDA Confidentiality Clause": "The Receiving Party agrees to hold all Confidential Information in strict confidence and not to disclose any Confidential Information to third parties without the prior written consent of the Disclosing Party. The Receiving Party shall use the Confidential Information solely for the purpose of evaluating a potential business relationship between the parties. This obligation of confidentiality shall survive the termination of this Agreement for a period of five (5) years. The Receiving Party shall notify the Disclosing Party promptly, and in no event later than forty-eight (48) hours, upon discovery of any unauthorized use or disclosure of Confidential Information.",
    "Indemnification Clause": "Each party (the 'Indemnifying Party') shall indemnify, defend, and hold harmless the other party, its affiliates, officers, directors, employees, agents, successors, and assigns (collectively, 'Indemnified Parties') from and against any and all losses, damages, liabilities, costs, and expenses, including reasonable attorneys' fees, arising out of or relating to: (i) any breach by the Indemnifying Party of any representation, warranty, covenant, or obligation under this Agreement; (ii) the negligence or willful misconduct of the Indemnifying Party; or (iii) any third-party claim arising from the Indemnifying Party's products or services. The indemnified party shall provide prompt written notice of any claim and cooperate fully in the defense thereof.",
    "Governing Law & Dispute Resolution": "This Agreement shall be governed by and construed in accordance with the laws of the State of Delaware, without regard to its conflict of laws principles. Any dispute, controversy, or claim arising out of or relating to this Agreement, or the breach thereof, shall be resolved by binding arbitration administered by the American Arbitration Association in accordance with its Commercial Arbitration Rules. The arbitration shall be conducted in Chicago, Illinois before a panel of three arbitrators. The award rendered by the arbitrators shall be final and binding and may be entered as a judgment in any court of competent jurisdiction. Notwithstanding the foregoing, either party may seek injunctive or other equitable relief in any court of competent jurisdiction to prevent irreparable harm.",
    "Payment & Fee Terms": "Client shall pay all invoices within thirty (30) days of the invoice date. Invoices not paid within thirty (30) days shall accrue interest at the rate of one and one-half percent (1.5%) per month, or the maximum rate permitted by applicable law, whichever is less. In the event of a billing dispute, Client shall pay all undisputed amounts and provide written notice of disputed amounts within fifteen (15) days of the invoice date. Failure to dispute an invoice within fifteen (15) days constitutes acceptance. The Firm reserves the right to suspend services upon thirty (30) days written notice for any invoice outstanding more than sixty (60) days.",
    "Force Majeure": "Neither party shall be liable for any failure or delay in performance under this Agreement to the extent such failure or delay is caused by circumstances beyond such party's reasonable control, including but not limited to acts of God, natural disasters, pandemic, epidemic, acts of war or terrorism, government actions, civil unrest, strikes or labor disputes, power failures, or internet service disruptions ('Force Majeure Event'). The party claiming a Force Majeure Event shall provide written notice to the other party within five (5) business days of the occurrence, describing the event in reasonable detail and the expected duration. Performance obligations shall be suspended for the duration of the Force Majeure Event. If a Force Majeure Event continues for more than ninety (90) days, either party may terminate this Agreement upon thirty (30) days written notice without liability.",
}

DOC_INTEL_FIELDS = {
    "parties": ("Parties", "Named legal entities in the agreement"),
    "effective_date": ("Effective Date", "When the agreement takes effect"),
    "governing_law": ("Governing Law", "Jurisdiction / choice of law"),
    "liability_cap": ("Liability Cap", "Maximum financial exposure"),
    "notice_period": ("Notice Period", "Required advance notice for actions"),
    "confidentiality_period": ("Confidentiality Period", "Duration of confidentiality obligation"),
    "termination_rights": ("Termination Rights", "Conditions allowing termination"),
    "dispute_resolution": ("Dispute Resolution", "Arbitration / litigation mechanism"),
    "payment_terms": ("Payment Terms", "Invoice and payment timing"),
    "key_obligations": ("Key Obligations", "Material duties of each party"),
}

import random as _rand
_rand.seed(42)
ANOMALY_DATA = {}
_matter_ids = ["M-2026-0041", "M-2026-0042", "M-2025-1847", "M-2026-0078", "M-2026-0089"]
_weeks = [f"W{i}" for i in range(1, 13)]
for _mid in _matter_ids:
    _base = _rand.randint(20, 60)
    _series = []
    for _i, _w in enumerate(_weeks):
        _v = _base + _rand.randint(-8, 8)
        _series.append((_w, max(0, _v)))
    _ai = _rand.randint(3, 9)
    _bi = _rand.randint(0, 2)
    _ci = _rand.randint(9, 11)
    _series[_ai] = (_weeks[_ai], _series[_ai][1] + _rand.randint(35, 65))
    _series[_bi] = (_weeks[_bi], max(0, _series[_bi][1] - _rand.randint(25, 40)))
    ANOMALY_DATA[_mid] = {
        "series": _series,
        "anomalies": [
            {"week": _weeks[_ai], "type": "Spike", "hours": _series[_ai][1], "explanation": f"Unusually high billing week detected on {_mid}. Hours billed ({_series[_ai][1]}) are {round(_series[_ai][1]/_base*100-100)}% above the 12-week average ({_base} hrs/week). Cortex AI flags this for partner review — common causes include: undisclosed parallel work streams, time entry error, or legitimate crisis response. Recommend: partner approval + narrative audit."},
            {"week": _weeks[_bi], "type": "Drop", "hours": _series[_bi][1], "explanation": f"Near-zero billing on {_mid} in {_weeks[_bi]} despite active matter status. Hours billed ({_series[_bi][1]}) are {round((1-_series[_bi][1]/_base)*100)}% below average. Cortex AI flags for review — may indicate: attorney reassignment, billing entry lag, or client-requested work pause. Recommend: confirm with matter team that work was captured."},
            {"week": _weeks[_ci], "type": "Trend", "hours": _series[_ci][1], "explanation": f"Sustained billing acceleration detected on {_mid} through {_weeks[_ci]}. Five-week trailing average ({round(sum(h for _,h in _series[-5:])/5)} hrs/week) significantly exceeds prior-period baseline ({_base} hrs/week). Budget exhaustion projected {_rand.randint(3,8)} weeks ahead of scheduled matter close. Recommend: immediate budget-to-actual review with client notification."},
        ],
    }
_rand.seed()


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

    # Topic filter
    topics = ["All", "Litigation", "Employment", "Regulatory", "M&A", "IP"]
    selected_topic = st.segmented_control(
        "Filter by practice area:",
        topics,
        default=st.session_state.research_topic,
        label_visibility="collapsed",
    )
    if selected_topic and selected_topic != st.session_state.research_topic:
        st.session_state.research_topic = selected_topic
        st.rerun()
    active_topic = st.session_state.research_topic or "All"

    # Live activity ticker
    active_count = random.randint(2, 7)
    st.markdown(f'<div style="text-align:right;color:{GR};font-size:.78rem;margin-bottom:.3rem;font-weight:600;">● {active_count} attorneys currently running research queries</div>', unsafe_allow_html=True)

    chat_container = st.container()

    # Suggestion pills filtered by topic
    if not st.session_state.chat_messages:
        filtered_qs = [q for q, v in RESEARCH_QA.items() if active_topic == "All" or v.get("topic") == active_topic]
        if filtered_qs:
            st.markdown(f'<div style="color:#888;font-size:.84rem;margin-bottom:.4rem;">Try a sample question{" (" + active_topic + ")" if active_topic != "All" else ""}:</div>', unsafe_allow_html=True)
            suggestion = st.pills("Suggestions", filtered_qs, label_visibility="collapsed")
            if suggestion:
                st.session_state.chat_messages.append({"role": "user", "content": suggestion})
                st.rerun()
        else:
            st.markdown(f'<div style="color:#888;font-size:.84rem;">No sample questions for this topic — type your own below.</div>', unsafe_allow_html=True)

    # Render chat history
    with chat_container:
        for i, msg in enumerate(st.session_state.chat_messages):
            with st.chat_message(msg["role"], avatar="⚖️" if msg["role"] == "user" else "❄️"):
                if msg["role"] == "assistant":
                    st.markdown(msg["content"])
                    if "sources" in msg:
                        with st.expander("📚 Sources & citations", expanded=False):
                            for src in msg["sources"]:
                                st.markdown(f"- {src}")
                        col_c, col_t, col_d = st.columns(3)
                        col_c.metric("Confidence", f"{msg.get('confidence', 95)}%")
                        col_t.metric("Response time", "1.3s")
                        col_d.metric("Sources retrieved", f"{random.randint(8,24)}")
                    # Follow-up chips on the last assistant message
                    if i == len(st.session_state.chat_messages) - 1 and "followups" in msg:
                        st.markdown('<div style="color:#888;font-size:.8rem;margin-top:.5rem;">💡 Follow-up questions:</div>', unsafe_allow_html=True)
                        followup = st.pills(f"followup_{i}", msg["followups"], label_visibility="collapsed")
                        if followup:
                            st.session_state.chat_messages.append({"role": "user", "content": followup})
                            st.rerun()
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
                    col_c, col_t, col_d = st.columns(3)
                    col_c.metric("Confidence", f"{qa['confidence']}%")
                    col_t.metric("Response time", "1.3s")
                    col_d.metric("Sources retrieved", f"{random.randint(8,24)}")
                    st.session_state.chat_messages.append({
                        "role": "assistant", "content": full,
                        "sources": qa["sources"], "confidence": qa["confidence"],
                        "followups": qa.get("followups", []),
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
        if st.button("🗑 Clear conversation", type="secondary"):
            st.session_state.chat_messages = []
            st.session_state.research_topic = "All"
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

    # ── Cortex Analyst (hero section — top) ──────────────────────────────────
    st.markdown(f"""<div style="background:linear-gradient(135deg,{SN}F5,#1a3a5cF5);
      border-radius:16px;padding:1.5rem 2rem;margin-bottom:1.5rem;border:1px solid {SB}44;">
      <div style="color:{SB};font-size:.75rem;font-weight:700;text-transform:uppercase;letter-spacing:.1em;margin-bottom:.4rem;">❄️ Cortex Analyst</div>
      <div style="color:white;font-size:1.15rem;font-weight:700;margin-bottom:.3rem;">Ask any question about your matters in plain English</div>
      <div style="color:#8BA3B8;font-size:.83rem;">Cortex Analyst translates your question to SQL, runs it against live matter data, and returns the result — no query writing required.</div>
    </div>""", unsafe_allow_html=True)

    analyst_left, analyst_right = st.columns([2, 3])

    with analyst_left:
        preset_qs = list(ANALYST_QUERIES.keys())
        analyst_q = st.selectbox("Choose a question:", preset_qs, label_visibility="collapsed")
        ask_btn = st.button("▶ Ask Cortex Analyst", type="primary", use_container_width=True)
        if ask_btn:
            st.session_state.analyst_query = analyst_q
            st.session_state.analyst_result = None
            st.session_state.analyst_running = True

    with analyst_right:
        sql_ph = st.empty()
        result_ph = st.empty()

        if st.session_state.analyst_running and st.session_state.analyst_result is None:
            # Typewriter SQL animation
            q_key = st.session_state.analyst_query
            sql_str = ANALYST_QUERIES.get(q_key, {}).get("sql", "SELECT * FROM matter_portfolio;")
            displayed = ""
            sql_ph.markdown(f"""<div style="background:#0D1B2A;border-radius:10px;padding:1rem 1.2rem;font-family:monospace;font-size:.78rem;color:#8FBCBB;min-height:80px;">
              <span style="color:{SB};font-weight:700;">-- Cortex Analyst generated SQL</span><br>{displayed}▌</div>""", unsafe_allow_html=True)
            for ch in sql_str:
                displayed += ch
                if ch in ("\n",):
                    displayed_html = displayed.replace("\n", "<br>").replace(" ", "&nbsp;")
                    sql_ph.markdown(f"""<div style="background:#0D1B2A;border-radius:10px;padding:1rem 1.2rem;font-family:monospace;font-size:.78rem;color:#8FBCBB;min-height:80px;">
                      <span style="color:{SB};font-weight:700;">-- Cortex Analyst generated SQL</span><br>{displayed_html}▌</div>""", unsafe_allow_html=True)
                    time.sleep(0.04)
                elif random.random() < 0.08:
                    displayed_html = displayed.replace("\n", "<br>").replace(" ", "&nbsp;")
                    sql_ph.markdown(f"""<div style="background:#0D1B2A;border-radius:10px;padding:1rem 1.2rem;font-family:monospace;font-size:.78rem;color:#8FBCBB;min-height:80px;">
                      <span style="color:{SB};font-weight:700;">-- Cortex Analyst generated SQL</span><br>{displayed_html}▌</div>""", unsafe_allow_html=True)
                    time.sleep(0.015)
            time.sleep(0.3)
            st.session_state.analyst_result = ANALYST_QUERIES[q_key]
            st.session_state.analyst_running = False

        if st.session_state.analyst_result and st.session_state.analyst_query:
            q_key = st.session_state.analyst_query
            sql_str = ANALYST_QUERIES.get(q_key, {}).get("sql", "")
            displayed_html = sql_str.replace("\n", "<br>").replace(" ", "&nbsp;")
            sql_ph.markdown(f"""<div style="background:#0D1B2A;border-radius:10px;padding:1rem 1.2rem;font-family:monospace;font-size:.78rem;color:#8FBCBB;min-height:80px;">
              <span style="color:{SB};font-weight:700;">-- Cortex Analyst generated SQL</span><br>{displayed_html}</div>""", unsafe_allow_html=True)
            result = st.session_state.analyst_result
            with result_ph.container():
                st.markdown(f'<div style="background:{GR}18;border-left:3px solid {GR};padding:.5rem .9rem;border-radius:7px;margin:.5rem 0;font-size:.82rem;color:{SN};font-weight:600;">✅ {q_key} — {len(result["rows"])} rows returned in 0.4s</div>', unsafe_allow_html=True)
                res_df = pd.DataFrame(result["rows"], columns=result["cols"])
                st.dataframe(res_df, hide_index=True, use_container_width=True)
        elif not st.session_state.analyst_result:
            sql_ph.markdown(f"""<div style="background:#0D1B2A;border-radius:10px;padding:1rem 1.2rem;font-family:monospace;font-size:.78rem;color:#4A5568;min-height:80px;text-align:center;display:flex;align-items:center;justify-content:center;">
              <span>Select a question and click ▶ Ask Cortex Analyst</span></div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Practice filter + KPIs ────────────────────────────────────────────────
    practices = ["All Practices"] + sorted(df["practice"].unique().tolist())
    practice_filter = st.pills("Filter by practice:", practices, default="All Practices")
    df_filtered = df[df["practice"] == practice_filter] if practice_filter and practice_filter != "All Practices" else df

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

    # Alert cards
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

    # Zero-copy proof bar
    st.markdown(f"""<div style="background:linear-gradient(90deg,{GR}18,{SB}12);border:1px solid {GR}44;
      border-radius:10px;padding:.7rem 1.4rem;display:flex;gap:3rem;margin-bottom:1rem;flex-wrap:wrap;">
      <div style="text-align:center;"><div style="font-size:1.5rem;font-weight:800;color:{GR};">0</div>
        <div style="font-size:.72rem;color:#666;font-weight:600;text-transform:uppercase;letter-spacing:.06em;">Data Copies Made</div></div>
      <div style="text-align:center;"><div style="font-size:1.5rem;font-weight:800;color:{GR};">0</div>
        <div style="font-size:.72rem;color:#666;font-weight:600;text-transform:uppercase;letter-spacing:.06em;">Export Files Created</div></div>
      <div style="text-align:center;"><div style="font-size:1.5rem;font-weight:800;color:{GR};">0ms</div>
        <div style="font-size:.72rem;color:#666;font-weight:600;text-transform:uppercase;letter-spacing:.06em;">Sync Latency</div></div>
      <div style="text-align:center;"><div style="font-size:1.5rem;font-weight:800;color:{SB};">Live</div>
        <div style="font-size:.72rem;color:#666;font-weight:600;text-transform:uppercase;letter-spacing:.06em;">Data Freshness</div></div>
      <div style="flex:1;display:flex;align-items:center;justify-content:flex-end;">
        <span style="background:{GR}22;color:{GR};font-size:.78rem;font-weight:700;padding:.3rem .8rem;border-radius:20px;border:1px solid {GR}44;">
          ● Snowflake Zero-Copy Architecture
        </span>
      </div>
    </div>""", unsafe_allow_html=True)

    tgl_col, picker_col, _ = st.columns([2, 2, 1])
    with tgl_col:
        view_toggle = st.toggle("👤 Simulate Client Login", value=st.session_state.client_view)
        if view_toggle != st.session_state.client_view:
            st.session_state.client_view = view_toggle
            st.session_state.share_revoked = False
            st.rerun()

    CLIENT_SHARES = {
        "Global Pharma Corp":   {"share": "FD_GPCorp_MatterShare",  "queries": 284},
        "HealthSystem Partners": {"share": "FD_HSP_MatterShare",    "queries": 142},
        "National Retail Group": {"share": "FD_NRG_MatterShare",    "queries": 67},
    }

    if st.session_state.client_view:
        with picker_col:
            sim_client = st.selectbox(
                "Simulating:", list(CLIENT_SHARES.keys()),
                index=list(CLIENT_SHARES.keys()).index(st.session_state.simulated_client),
                label_visibility="visible",
            )
            if sim_client != st.session_state.simulated_client:
                st.session_state.simulated_client = sim_client
                st.rerun()

        chosen = st.session_state.simulated_client
        share_info = CLIENT_SHARES[chosen]

        if st.session_state.share_revoked:
            st.error(f"🚫 Access revoked — {chosen} can no longer query this share.", icon="🔒")
            if st.button("Restore access", type="secondary"):
                st.session_state.share_revoked = False
                st.session_state.client_view = False
                st.rerun()
        else:
            # Client portal header
            hdr_col, revoke_col = st.columns([5, 1])
            with hdr_col:
                st.markdown(f"""
                <div style="background:linear-gradient(135deg,{SN},#1a3a5c);padding:1.2rem 1.8rem;border-radius:14px;margin-bottom:1rem;border:2px solid {SB}55;">
                  <div style="color:{SB};font-size:.75rem;font-weight:700;text-transform:uppercase;letter-spacing:.08em;">Snowflake Secure Share — Live Matter Portal</div>
                  <div style="color:white;font-size:1.3rem;font-weight:800;margin-top:.3rem;">{chosen} · Client View</div>
                  <div style="color:#8BA3B8;font-size:.8rem;margin-top:.2rem;">Viewing data shared by Faegre Drinker Biddle & Reath LLP · Real-time · Zero copies</div>
                </div>""", unsafe_allow_html=True)
            with revoke_col:
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("🚫 Revoke Access", type="secondary", use_container_width=True):
                    st.session_state.share_revoked = True
                    st.session_state.client_view = False
                    st.rerun()

            client_matters = [m for m in MATTERS if m["client"] == chosen]

            # Live activity feed
            feed_events = [
                (f"{chosen[:12]} queried matter billing detail", "just now"),
                ("Cortex Analyst ran fee summary query", "8s ago"),
                (f"{chosen[:12]} downloaded matter status report", "24s ago"),
                ("Row-level policy enforced — 342 matters hidden", "1m ago"),
                ("Audit log entry written to SNOWFLAKE.ACCOUNT_USAGE", "1m ago"),
                (f"Share query #{share_info['queries']} completed in 0.2s", "2m ago"),
            ]
            feed_ph = st.empty()
            shown_feed = []
            for event, ts in feed_events:
                shown_feed.append((event, ts))
                rows = "".join(f'<div style="display:flex;justify-content:space-between;padding:.35rem 0;border-bottom:1px solid #F0F4F8;font-size:.8rem;"><span style="color:{SN};">● {e}</span><span style="color:#AAB8C8;">{t}</span></div>' for e, t in shown_feed)
                feed_ph.markdown(f'<div style="background:white;border:1px solid #E2EBF5;border-radius:10px;padding:.6rem 1rem;margin-bottom:.8rem;"><div style="color:#888;font-size:.72rem;font-weight:700;text-transform:uppercase;letter-spacing:.08em;margin-bottom:.3rem;">Live Share Activity</div>{rows}</div>', unsafe_allow_html=True)
                time.sleep(0.12)

            # Matter cards
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
                    <div style="background:{color};width:{min(pct,100):.0f}%;height:8px;border-radius:6px;"></div>
                  </div>
                </div>""", unsafe_allow_html=True)

            if not client_matters:
                st.info(f"No matters found for {chosen} in this demo dataset.")

            st.markdown(f"""<div class="ib">
              <b style="color:{SN};">🔒 How this works</b><br>
              <span style="color:#5A6A7A;font-size:.86rem;">{chosen} is querying Faegre Drinker's Snowflake account directly via a secure share — zero data was copied or exported. Row-level security ensures they see <em>only their matters</em>. Click "🚫 Revoke Access" to instantly cut off access in under a second.</span>
            </div>""", unsafe_allow_html=True)

    else:
        # Step-by-step walkthrough
        steps = [
            ("1", "Create a Row-Level Security view", "A single SQL view filters matter data by `CURRENT_USER()` — each client automatically sees only their matters when they query the share. No application logic required."),
            ("2", "Create the secure share", "Snowflake creates a zero-copy pointer to your data. No data is duplicated, moved, or exported. The share references live production data in real time."),
            ("3", "Add the client's Snowflake account", "Specify the client's Snowflake account identifier. They instantly gain access. You control exactly which objects, tables, and columns they can see."),
            ("4", "Client queries live — always current", "The client connects their own BI tools (Tableau, Power BI, Sigma, or SQL) to the share. Every query hits live data. No refresh cycles, no stale PDFs, no billing disputes."),
        ]

        total_steps = len(steps)
        current = st.session_state.share_step

        step_cols = st.columns(total_steps)
        for i, (num, title, _) in enumerate(steps):
            is_active = i <= current
            bg = f"linear-gradient(135deg,{SB},{GR})" if is_active else "#E2EBF5"
            fc = "white" if is_active else "#888"
            fw = 700 if is_active else 400
            tc = SN if is_active else "#999"
            step_cols[i].markdown(f"""<div style="text-align:center;padding:.5rem;">
              <div style="width:36px;height:36px;border-radius:50%;background:{bg};
                color:{fc};font-weight:800;font-size:1rem;display:flex;align-items:center;justify-content:center;margin:0 auto .5rem auto;">{num}</div>
              <div style="font-size:.78rem;font-weight:{fw};color:{tc};">{title}</div>
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
            {"Client": "Global Pharma Corp",   "Share": "FD_GPCorp_MatterShare", "Matters": 1, "Last Query": "Today, 9:42 AM",      "Queries (30d)": 284, "Status": "Active"},
            {"Client": "HealthSystem Partners", "Share": "FD_HSP_MatterShare",   "Matters": 1, "Last Query": "Yesterday, 3:15 PM",  "Queries (30d)": 142, "Status": "Active"},
            {"Client": "National Retail Group", "Share": "FD_NRG_MatterShare",   "Matters": 1, "Last Query": "Apr 28, 2026",        "Queries (30d)": 67,  "Status": "Active"},
            {"Client": "Financial Services Co.","Share": "FD_FSC_MatterShare",   "Matters": 1, "Last Query": "—",                   "Queries (30d)": 0,   "Status": "Pending"},
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
# Page: Cortex AI Lab
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "🤖 Legal AI Lab":
    st.markdown(f"""
    <div class="hero">
      <div class="hero-title">🤖 Legal AI Lab</div>
      <div class="hero-sub">Five live demonstrations of Snowflake Cortex AI — from document intelligence to predictive analytics</div>
      <div class="hero-meta">AI_SUMMARIZE · AI_CLASSIFY · AI_SENTIMENT · AI_EXTRACT · AI_FILTER · AI_COMPLETE · Cortex ML</div>
    </div>""", unsafe_allow_html=True)

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "⚡ AI Functions",
        "💬 AI_COMPLETE Playground",
        "🎯 Predictive Outcomes",
        "🔍 Document Intelligence",
        "📈 Anomaly Detection",
    ])

    # ── Tab 1: AI Functions Showcase ─────────────────────────────────────────
    with tab1:
        st.markdown(f'<div class="sh">Cortex AI Functions — Pick a function, run it live</div>', unsafe_allow_html=True)
        st.markdown(f'<div style="color:#5A6A7A;font-size:.87rem;margin-bottom:1rem;">Snowflake Cortex AI ships five first-class AI functions that run directly in SQL — no Python, no external API calls, no data leaving your Snowflake account.</div>', unsafe_allow_html=True)

        fn_col, doc_col = st.columns([1, 1])
        with fn_col:
            fn_choice = st.selectbox(
                "Select a Cortex AI function:",
                list(AI_FUNCTIONS.keys()),
                format_func=lambda k: f"{k} — {AI_FUNCTIONS[k]['desc']}",
            )
        with doc_col:
            doc_choice = st.selectbox(
                "Select a document / dataset:",
                list(AI_FUNCTIONS[fn_choice]["docs"].keys()),
            )

        fn_data = AI_FUNCTIONS[fn_choice]
        doc_data = fn_data["docs"][doc_choice]
        sql_str = fn_data["sql_tmpl"].replace("{doc_id}", doc_choice[:12].replace(" ", "_").upper())

        run_fn_btn = st.button(f"▶ Run {fn_choice}", type="primary", use_container_width=False)
        if run_fn_btn:
            st.session_state.ai_func_result = None
            st.session_state.ai_func_running = True

        st.markdown("<br>", unsafe_allow_html=True)
        left_panel, right_panel = st.columns(2)

        with left_panel:
            st.markdown(f'<div style="color:{SN};font-weight:700;font-size:.88rem;margin-bottom:.4rem;">📄 Input Document</div>', unsafe_allow_html=True)
            st.markdown(f'<div style="background:#F8FAFC;border:1px solid #E2EBF5;border-radius:8px;padding:.8rem 1rem;font-size:.8rem;color:#444;line-height:1.7;min-height:140px;font-family:Georgia,serif;">{doc_data["input"]}</div>', unsafe_allow_html=True)
            st.markdown(f'<div style="background:{SN};border-radius:8px;padding:.7rem 1rem;font-family:monospace;font-size:.75rem;color:#8FBCBB;margin-top:.6rem;"><span style="color:{SB};font-weight:700;">-- Snowflake SQL</span><br>{sql_str.replace(chr(10), "<br>").replace(" ", "&nbsp;")}</div>', unsafe_allow_html=True)

        with right_panel:
            st.markdown(f'<div style="color:{SN};font-weight:700;font-size:.88rem;margin-bottom:.4rem;">✨ {fn_choice} Output</div>', unsafe_allow_html=True)
            result_area = st.empty()

            if st.session_state.ai_func_running and st.session_state.ai_func_result is None:
                words = doc_data["output"].split(" ")
                displayed = ""
                for i, w in enumerate(words):
                    displayed += w + " "
                    if i % 4 == 0:
                        result_area.markdown(f'<div class="air">{displayed}▌</div>', unsafe_allow_html=True)
                        time.sleep(0.03)
                result_area.markdown(f'<div class="air">{displayed}</div>', unsafe_allow_html=True)
                st.session_state.ai_func_result = displayed
                st.session_state.ai_func_running = False
                col_l, col_m, col_r = st.columns(3)
                col_l.metric("Latency", f"{random.randint(380, 620)}ms")
                col_m.metric("Model", "arctic-instruct")
                col_r.metric("Tokens used", f"{random.randint(320, 890):,}")
            elif st.session_state.ai_func_result:
                result_area.markdown(f'<div class="air">{st.session_state.ai_func_result}</div>', unsafe_allow_html=True)
                col_l, col_m, col_r = st.columns(3)
                col_l.metric("Latency", f"{random.randint(380, 620)}ms")
                col_m.metric("Model", "arctic-instruct")
                col_r.metric("Tokens used", f"{random.randint(320, 890):,}")
            else:
                result_area.markdown(f'<div style="background:#F8FAFC;border:1px dashed #C8D8E8;border-radius:8px;padding:2rem;text-align:center;color:#AAB8C8;min-height:140px;display:flex;align-items:center;justify-content:center;"><div><div style="font-size:1.8rem;margin-bottom:.5rem;">⚡</div>Select a function and click ▶ Run</div></div>', unsafe_allow_html=True)

        if run_fn_btn or st.session_state.ai_func_result:
            if st.button("↺ Clear result", key="clear_fn"):
                st.session_state.ai_func_result = None
                st.rerun()

    # ── Tab 2: AI_COMPLETE Playground ────────────────────────────────────────
    with tab2:
        st.markdown(f'<div class="sh">AI_COMPLETE Playground — Build legal AI prompts</div>', unsafe_allow_html=True)
        st.markdown(f'<div style="color:#5A6A7A;font-size:.87rem;margin-bottom:1rem;"><code>AI_COMPLETE(model, prompt)</code> lets attorneys and developers call any Snowflake-hosted LLM directly in SQL or Python — zero infrastructure, zero API keys, all within the Snowflake security perimeter.</div>', unsafe_allow_html=True)

        pg_left, pg_right = st.columns([1, 1])
        with pg_left:
            template_choice = st.selectbox("Load a prompt template:", list(PLAYGROUND_TEMPLATES.keys()))
            model_choice = st.pills(
                "Model:",
                ["snowflake-arctic-instruct", "mistral-large2", "llama3-70b"],
                default=st.session_state.playground_model,
            )
            if model_choice and model_choice != st.session_state.playground_model:
                st.session_state.playground_model = model_choice
            prompt_text = st.text_area(
                "Prompt (editable):",
                value=PLAYGROUND_TEMPLATES[template_choice]["prompt"],
                height=260,
                label_visibility="collapsed",
            )
            gen_btn = st.button("▶ Generate with AI_COMPLETE", type="primary", use_container_width=True)

        with pg_right:
            st.markdown(f'<div style="color:{SN};font-weight:700;font-size:.88rem;margin-bottom:.4rem;">🤖 AI Response</div>', unsafe_allow_html=True)
            sql_pg = f"SELECT AI_COMPLETE(\n  '{st.session_state.playground_model}',\n  $prompt_variable\n) AS ai_response;"
            st.markdown(f'<div style="background:{SN};border-radius:8px;padding:.5rem .9rem;font-family:monospace;font-size:.73rem;color:#8FBCBB;margin-bottom:.5rem;"><span style="color:{SB};font-weight:700;">-- SQL</span><br>{sql_pg.replace(chr(10), "<br>").replace(" ", "&nbsp;")}</div>', unsafe_allow_html=True)

            response_area = st.empty()
            token_area = st.empty()

            if gen_btn:
                st.session_state.playground_response = None
                resp = PLAYGROUND_TEMPLATES[template_choice]["response"]
                words = resp.split(" ")
                displayed = ""
                for i, w in enumerate(words):
                    displayed += w + " "
                    token_count = len(displayed.split())
                    pct = min(token_count / len(words), 1.0)
                    if i % 5 == 0:
                        response_area.markdown(f'<div class="air" style="min-height:220px;">{displayed}▌</div>', unsafe_allow_html=True)
                        token_area.markdown(f'<div style="background:#F0F4F8;border-radius:6px;height:6px;margin-top:.3rem;"><div style="background:{SB};width:{pct*100:.0f}%;height:6px;border-radius:6px;"></div></div><div style="color:#888;font-size:.73rem;margin-top:.2rem;">Generating · {token_count} tokens</div>', unsafe_allow_html=True)
                        time.sleep(0.025)
                response_area.markdown(f'<div class="air" style="min-height:220px;">{displayed}</div>', unsafe_allow_html=True)
                token_area.markdown(f'<div style="color:{GR};font-size:.78rem;font-weight:600;margin-top:.3rem;">✅ {len(words)} tokens · {st.session_state.playground_model} · {random.randint(620,1100)}ms</div>', unsafe_allow_html=True)
                st.session_state.playground_response = displayed

            elif st.session_state.playground_response:
                response_area.markdown(f'<div class="air" style="min-height:220px;">{st.session_state.playground_response}</div>', unsafe_allow_html=True)
                token_area.markdown(f'<div style="color:{GR};font-size:.78rem;font-weight:600;margin-top:.3rem;">✅ Complete · {st.session_state.playground_model}</div>', unsafe_allow_html=True)
            else:
                response_area.markdown(f'<div style="background:#F8FAFC;border:1px dashed #C8D8E8;border-radius:8px;padding:2rem;text-align:center;color:#AAB8C8;min-height:220px;"><div style="font-size:1.8rem;margin-bottom:.5rem;">💬</div>Click ▶ Generate to run AI_COMPLETE</div>', unsafe_allow_html=True)

    # ── Tab 3: Predictive Matter Outcomes ────────────────────────────────────
    with tab3:
        st.markdown(f'<div class="sh">Predictive Matter Outcomes — ML-powered forecasting</div>', unsafe_allow_html=True)
        st.markdown(f'<div style="color:#5A6A7A;font-size:.87rem;margin-bottom:1rem;">Trained on Faegre Drinker\'s historical matter portfolio, this model predicts outcome probability, budget overrun risk, and timeline using Snowflake ML Classification and Regression functions — no external ML platform required.</div>', unsafe_allow_html=True)

        pred_input_col, pred_result_col = st.columns([1, 2])
        with pred_input_col:
            st.markdown(f'<div style="color:{SN};font-weight:700;font-size:.88rem;margin-bottom:.6rem;">Matter Parameters</div>', unsafe_allow_html=True)
            matter_type = st.selectbox("Matter type:", ["Litigation", "M&A", "Regulatory", "Employment", "IP/Patent"])
            complexity = st.slider("Complexity score:", 1, 10, 5)
            opposing_tier = st.selectbox("Opposing counsel:", ["Tier 1 BigLaw", "Regional Firm", "In-House", "Pro Se"])
            budget_input = st.number_input("Initial budget ($):", value=500000, step=50000, format="%d")
            predict_btn = st.button("🧠 Predict Outcome", type="primary", use_container_width=True)

        with pred_result_col:
            complexity_band = "High" if complexity >= 6 else "Low"
            lookup_key = (matter_type, complexity_band)
            pred_data = PREDICTION_TABLE.get(lookup_key, PREDICTION_TABLE[("Litigation", "Low")])

            if predict_btn:
                st.session_state.prediction_result = pred_data

            if st.session_state.prediction_result or predict_btn:
                pd_show = st.session_state.prediction_result or pred_data
                st.markdown(f'<div style="color:{SN};font-weight:700;font-size:.88rem;margin-bottom:.6rem;">🎯 Model Prediction</div>', unsafe_allow_html=True)

                fav_ph = st.empty()
                bud_ph = st.empty()

                fav_target = pd_show["favorable_pct"]
                bud_target = pd_show["budget_overrun_risk"]
                fav_color = GR if fav_target >= 70 else (OR if fav_target >= 50 else RD)
                bud_color = GR if bud_target <= 25 else (OR if bud_target <= 50 else RD)

                steps_p = 30
                for s in range(steps_p + 1):
                    t = s / steps_p
                    ease = t * t * (3 - 2 * t)
                    fv = int(fav_target * ease)
                    bv = int(bud_target * ease)
                    fav_ph.markdown(f"""<div style="margin-bottom:.8rem;">
                      <div style="display:flex;justify-content:space-between;font-size:.83rem;font-weight:600;margin-bottom:.3rem;">
                        <span style="color:{SN};">Favorable Outcome Probability</span>
                        <span style="color:{fav_color};font-size:1.1rem;">{fv}%</span>
                      </div>
                      <div style="background:#F0F4F8;border-radius:8px;height:14px;">
                        <div style="background:{fav_color};width:{fv}%;height:14px;border-radius:8px;transition:width .1s;"></div>
                      </div>
                    </div>""", unsafe_allow_html=True)
                    bud_ph.markdown(f"""<div style="margin-bottom:.8rem;">
                      <div style="display:flex;justify-content:space-between;font-size:.83rem;font-weight:600;margin-bottom:.3rem;">
                        <span style="color:{SN};">Budget Overrun Risk</span>
                        <span style="color:{bud_color};font-size:1.1rem;">{bv}%</span>
                      </div>
                      <div style="background:#F0F4F8;border-radius:8px;height:14px;">
                        <div style="background:{bud_color};width:{bv}%;height:14px;border-radius:8px;transition:width .1s;"></div>
                      </div>
                    </div>""", unsafe_allow_html=True)
                    time.sleep(0.02)

                st.markdown(f'<div style="background:{SB}12;border:1px solid {SB}33;border-radius:8px;padding:.6rem 1rem;margin:.4rem 0;font-size:.84rem;"><b style="color:{SN};">⏱ Estimated Timeline:</b> <span style="color:{SB};font-weight:700;">{pd_show["timeline_months"]} months</span></div>', unsafe_allow_html=True)

                st.markdown(f'<div style="color:{SN};font-weight:700;font-size:.83rem;margin:.7rem 0 .3rem;">📊 Top Predictive Features (SHAP values)</div>', unsafe_allow_html=True)
                for feat, importance in pd_show["factors"]:
                    bar_w = importance
                    st.markdown(f"""<div style="margin-bottom:.3rem;">
                      <div style="display:flex;justify-content:space-between;font-size:.78rem;color:#5A6A7A;margin-bottom:.15rem;">
                        <span>{feat}</span><span style="font-weight:600;">{importance}%</span>
                      </div>
                      <div style="background:#F0F4F8;border-radius:4px;height:8px;">
                        <div style="background:linear-gradient(90deg,{SB},{GR});width:{bar_w}%;height:8px;border-radius:4px;"></div>
                      </div>
                    </div>""", unsafe_allow_html=True)

                st.markdown(f'<div style="color:{SN};font-weight:700;font-size:.83rem;margin:.8rem 0 .3rem;">💡 Recommended Actions</div>', unsafe_allow_html=True)
                for action in pd_show["actions"]:
                    st.markdown(f'<div style="background:{GR}10;border-left:3px solid {GR};padding:.5rem .8rem;border-radius:6px;margin-bottom:.4rem;font-size:.84rem;color:{SN};">✅ {action}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div style="background:#F8FAFC;border:1px dashed #C8D8E8;border-radius:8px;padding:3rem;text-align:center;color:#AAB8C8;"><div style="font-size:1.8rem;margin-bottom:.5rem;">🎯</div>Configure matter parameters and click Predict Outcome</div>', unsafe_allow_html=True)

    # ── Tab 4: Live Document Intelligence ────────────────────────────────────
    with tab4:
        st.markdown(f'<div class="sh">Live Document Intelligence — AI_EXTRACT in real time</div>', unsafe_allow_html=True)
        st.markdown(f'<div style="color:#5A6A7A;font-size:.87rem;margin-bottom:.8rem;">Paste any contract clause or select a sample. Watch Snowflake <code>AI_EXTRACT</code> identify and pull out every structured field — parties, dates, obligations, risk indicators — in under a second.</div>', unsafe_allow_html=True)

        sample_btns = st.columns(len(DOC_INTEL_SAMPLES))
        selected_sample = None
        for col, (sname, _) in zip(sample_btns, DOC_INTEL_SAMPLES.items()):
            with col:
                if st.button(sname, use_container_width=True, key=f"sample_{sname[:10]}"):
                    selected_sample = sname
                    st.session_state.doc_intel_result = None

        default_text = DOC_INTEL_SAMPLES.get(selected_sample, list(DOC_INTEL_SAMPLES.values())[0]) if selected_sample else list(DOC_INTEL_SAMPLES.values())[0]

        di_left, di_right = st.columns(2)
        with di_left:
            doc_text = st.text_area("Contract text (editable):", value=default_text, height=280, label_visibility="collapsed")
            extract_btn = st.button("🔍 Extract Fields with AI_EXTRACT", type="primary", use_container_width=True)

        with di_right:
            st.markdown(f'<div style="color:{SN};font-weight:700;font-size:.88rem;margin-bottom:.4rem;">⚡ Extracted Fields</div>', unsafe_allow_html=True)
            fields_area = st.empty()

            def _extract_fields_from_text(txt):
                txt_l = txt.lower()
                results = []
                party_m = re.findall(r'between ([A-Z][A-Za-z\s,\.]+(?:LLC|Inc\.|LLP|Corp\.|Ltd\.)[^,\n]*)', txt)
                results.append(("parties", ", ".join(party_m[:2]) if party_m else "Not identified", 91 if party_m else 40))
                date_m = re.search(r'(?:as of|effective|entered into)\s+([A-Z][a-z]+ \d{1,2},? \d{4}|\d{1,2}/\d{2}/\d{4})', txt, re.IGNORECASE)
                results.append(("effective_date", date_m.group(1) if date_m else "Not specified", 95 if date_m else 30))
                law_m = re.search(r'laws? of (?:the (?:State|Commonwealth) of )?([A-Z][a-zA-Z]+)', txt)
                results.append(("governing_law", law_m.group(1) if law_m else "Not identified", 97 if law_m else 35))
                cap_m = re.search(r'(?:not exceed|limited to|cap)\s+(\$[\d,]+(?:\.\d+)?(?:\s*(?:million|thousand))?)', txt, re.IGNORECASE)
                results.append(("liability_cap", cap_m.group(1) if cap_m else "Not specified", 93 if cap_m else 50))
                notice_m = re.search(r'(\d+)[- ](?:business )?days?\s+(?:written |prior )?notice', txt, re.IGNORECASE)
                results.append(("notice_period", f"{notice_m.group(1)} days" if notice_m else "Not specified", 96 if notice_m else 45))
                conf_m = re.search(r'(\d+)[- ]years?\s+(?:following|after|from|post)[- ](?:termination|expiration)', txt, re.IGNORECASE)
                results.append(("confidentiality_period", f"{conf_m.group(1)} years post-termination" if conf_m else "Not specified", 94 if conf_m else 40))
                has_arb = bool(re.search(r'arbitrat|AAA|JAMS|dispute resolution', txt, re.IGNORECASE))
                results.append(("dispute_resolution", "Binding arbitration" if has_arb else "Not specified / litigation", 92 if has_arb else 60))
                payment_m = re.search(r'(?:within|pay within)\s+(\d+)[- ]days?', txt, re.IGNORECASE)
                results.append(("payment_terms", f"Net {payment_m.group(1)} days" if payment_m else "Not specified", 90 if payment_m else 45))
                shall_sent = [s.strip() for s in re.split(r'[.;]', txt) if re.search(r'\b(shall|must|agrees? to|required to)\b', s, re.IGNORECASE) and 10 < len(s.strip()) < 150]
                results.append(("key_obligations", shall_sent[0][:120] + "..." if shall_sent else "See full document", 88 if shall_sent else 50))
                return results

            if extract_btn:
                st.session_state.doc_intel_result = None
                fields = _extract_fields_from_text(doc_text)
                shown = []
                for field_key, field_val, confidence in fields:
                    info = DOC_INTEL_FIELDS.get(field_key, (field_key, ""))
                    conf_color = GR if confidence >= 85 else (OR if confidence >= 60 else RD)
                    shown.append((info[0], field_val, confidence, conf_color))
                    rows_html = "".join(f"""<div style="display:flex;justify-content:space-between;align-items:flex-start;padding:.45rem 0;border-bottom:1px solid #F0F4F8;" class="fade-in">
                      <div style="flex:1;">
                        <div style="font-size:.72rem;color:#888;font-weight:600;text-transform:uppercase;letter-spacing:.05em;">{lbl}</div>
                        <div style="font-size:.83rem;color:{SN};font-weight:500;margin-top:.1rem;">{val[:100]}</div>
                      </div>
                      <span style="background:{cc}22;color:{cc};font-size:.7rem;font-weight:700;padding:2px 7px;border-radius:12px;margin-left:.5rem;flex-shrink:0;">{c}%</span>
                    </div>""" for lbl, val, c, cc in shown)
                    fields_area.markdown(f'<div style="background:white;border:1px solid #E2EBF5;border-radius:10px;padding:.6rem 1rem;">{rows_html}</div>', unsafe_allow_html=True)
                    time.sleep(0.14)
                st.session_state.doc_intel_result = shown
            elif st.session_state.doc_intel_result:
                rows_html = "".join(f"""<div style="display:flex;justify-content:space-between;align-items:flex-start;padding:.45rem 0;border-bottom:1px solid #F0F4F8;">
                  <div style="flex:1;">
                    <div style="font-size:.72rem;color:#888;font-weight:600;text-transform:uppercase;letter-spacing:.05em;">{lbl}</div>
                    <div style="font-size:.83rem;color:{SN};font-weight:500;margin-top:.1rem;">{val[:100]}</div>
                  </div>
                  <span style="background:{cc}22;color:{cc};font-size:.7rem;font-weight:700;padding:2px 7px;border-radius:12px;margin-left:.5rem;flex-shrink:0;">{c}%</span>
                </div>""" for lbl, val, c, cc in st.session_state.doc_intel_result)
                fields_area.markdown(f'<div style="background:white;border:1px solid #E2EBF5;border-radius:10px;padding:.6rem 1rem;">{rows_html}</div>', unsafe_allow_html=True)
            else:
                fields_area.markdown(f'<div style="background:#F8FAFC;border:1px dashed #C8D8E8;border-radius:8px;padding:2rem;text-align:center;color:#AAB8C8;"><div style="font-size:1.8rem;margin-bottom:.5rem;">🔍</div>Click Extract Fields to run AI_EXTRACT</div>', unsafe_allow_html=True)

    # ── Tab 5: Billing Anomaly Detection ─────────────────────────────────────
    with tab5:
        st.markdown(f'<div class="sh">AI Billing Anomaly Detection — Cortex ML</div>', unsafe_allow_html=True)
        st.markdown(f'<div style="color:#5A6A7A;font-size:.87rem;margin-bottom:.8rem;">Cortex ML Anomaly Detection runs over your matter billing time series to surface unusual spikes, sudden drops, and unsustainable burn rate trends — automatically, in SQL.</div>', unsafe_allow_html=True)

        matter_options = ["All Matters — Portfolio View"] + list(ANOMALY_DATA.keys())
        chosen_matter = st.selectbox("Select matter:", matter_options, key="anomaly_sel")
        st.session_state.anomaly_matter = chosen_matter

        if chosen_matter == "All Matters — Portfolio View":
            plot_matters = list(ANOMALY_DATA.keys())
        else:
            plot_matters = [chosen_matter]

        fig_anom = go.Figure()
        all_anomaly_points = []
        colors_cycle = [SB, GR, OR, GD, "#9B59B6"]
        for idx, mid in enumerate(plot_matters):
            mdata = ANOMALY_DATA[mid]
            weeks = [w for w, _ in mdata["series"]]
            hours = [h for _, h in mdata["series"]]
            anom_weeks = {a["week"] for a in mdata["anomalies"]}
            line_color = colors_cycle[idx % len(colors_cycle)]
            fig_anom.add_trace(go.Scatter(
                x=weeks, y=hours, mode="lines+markers",
                name=mid, line=dict(color=line_color, width=2),
                marker=dict(size=5, color=line_color),
            ))
            for a in mdata["anomalies"]:
                aw = a["week"]
                ah = a["hours"]
                atype = a["type"]
                marker_color = RD if atype == "Spike" else (OR if atype == "Trend" else "#9B59B6")
                fig_anom.add_trace(go.Scatter(
                    x=[aw], y=[ah], mode="markers+text",
                    marker=dict(size=14, color=marker_color, symbol="star", line=dict(color="white", width=1.5)),
                    text=[f"⚠ {atype}"], textposition="top center",
                    textfont=dict(size=9, color=marker_color),
                    showlegend=False, name=f"{mid} anomaly",
                ))
                all_anomaly_points.append((mid, a))

        fig_anom.update_layout(
            plot_bgcolor="white", paper_bgcolor="white", height=320,
            margin=dict(l=0, r=0, t=20, b=0),
            legend=dict(orientation="h", y=-0.15, font=dict(size=10)),
            yaxis_title="Hours Billed",
            xaxis_title="Week",
        )
        st.plotly_chart(fig_anom, use_container_width=True)

        total_anomalies = len(all_anomaly_points)
        est_discrepancy = total_anomalies * random.randint(12000, 18000)
        st.markdown(f'<div style="background:{RD}10;border:1px solid {RD}33;border-radius:10px;padding:.7rem 1.2rem;margin-bottom:.8rem;display:flex;gap:2rem;flex-wrap:wrap;"><span style="font-weight:700;color:{RD};">⚠ {total_anomalies} anomalies detected</span><span style="color:#666;">across {len(plot_matters)} matter(s)</span><span style="color:{OR};font-weight:600;">Estimated discrepancy: ~${est_discrepancy:,.0f}</span></div>', unsafe_allow_html=True)

        st.markdown(f'<div class="sh" style="font-size:.95rem;">Anomaly Details</div>', unsafe_allow_html=True)
        for mid, anom in all_anomaly_points:
            akey = f"{mid}_{anom['week']}_{anom['type']}"
            atype_color = RD if anom["type"] == "Spike" else (OR if anom["type"] == "Trend" else "#9B59B6")
            with st.expander(f"{'🔴' if anom['type']=='Spike' else '🟠' if anom['type']=='Trend' else '🟣'} {mid} · {anom['week']} · {anom['type']} ({anom['hours']} hrs)", expanded=False):
                explain_ph = st.empty()
                if akey in st.session_state.anomaly_explained:
                    explain_ph.markdown(f'<div class="air">{st.session_state.anomaly_explained[akey]}</div>', unsafe_allow_html=True)
                    st.markdown(f'<span style="background:{atype_color}22;color:{atype_color};padding:3px 10px;border-radius:14px;font-size:.76rem;font-weight:700;">{anom["type"]} · {anom["hours"]} hours billed</span>', unsafe_allow_html=True)
                else:
                    if st.button(f"🧠 Explain this anomaly", key=f"exp_{akey}", type="primary"):
                        words = anom["explanation"].split(" ")
                        displayed = ""
                        for i, w in enumerate(words):
                            displayed += w + " "
                            if i % 5 == 0:
                                explain_ph.markdown(f'<div class="air">{displayed}▌</div>', unsafe_allow_html=True)
                                time.sleep(0.04)
                        explain_ph.markdown(f'<div class="air">{displayed}</div>', unsafe_allow_html=True)
                        st.session_state.anomaly_explained[akey] = displayed
                        st.markdown(f'<span style="background:{atype_color}22;color:{atype_color};padding:3px 10px;border-radius:14px;font-size:.76rem;font-weight:700;">{anom["type"]} · {anom["hours"]} hours billed</span>', unsafe_allow_html=True)


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
