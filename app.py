# ============================================================
#  SUPPLY CHAIN COMMAND CENTER  |  app.py
#  Premium Dark UI · Streamlit + Groq (llama-3.3-70b-versatile)
#
#  All bugs fixed:
#   1. legend duplicate kwarg -> dark() helper
#   2. empty label warnings on text_input / radio
#   3. use_container_width deprecated -> width='stretch'
#   4. ASCII codec on Groq response -> _sanitize() on output
#   5. latin-1 codec on outgoing prompts -> _sanitize() on inputs
#   6. fillcolor hex-alpha invalid Plotly 6 -> hex_to_rgba()
#   7. gauge axis gridcolor invalid Plotly 6 -> removed
#   8. colorbar titlefont invalid Plotly 6 -> title=dict(font=...)
# ============================================================

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import json as _json
import re
import urllib.request
import urllib.error

# ── PAGE CONFIG ──────────────────────────────────────────────
st.set_page_config(
    page_title="Supply Chain Command Center",
    page_icon="chain",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── PREMIUM DARK CSS ─────────────────────────────────────────
st.markdown("""
<style>
html, body, [data-testid="stAppViewContainer"] {
    background: #050d1a !important; color: #e2e8f0 !important;
}
[data-testid="stHeader"]  { background: transparent !important; }
[data-testid="stToolbar"] { display: none; }
[data-testid="stSidebar"] {
    background: linear-gradient(180deg,#0a1628 0%,#0d1f3c 100%) !important;
    border-right: 1px solid #1e3a5f !important;
}
[data-testid="stSidebar"] * { color: #cbd5e1 !important; }
[data-testid="stSidebar"] .stTextInput input {
    background:#0f2744 !important; border:1px solid #1e4976 !important;
    color:#e2e8f0 !important; border-radius:8px !important;
}
[data-testid="stSidebar"] hr { border-color:#1e3a5f !important; }
section[data-testid="stSidebar"] [data-testid="stDownloadButton"] button {
    background:linear-gradient(135deg,#1e3a5f,#0f2744) !important;
    border:1px solid #3b82f6 !important; color:#93c5fd !important;
    font-size:12px !important; border-radius:8px !important; width:100% !important;
}
h1,h2,h3,h4,h5,p,span,label,div { color:#e2e8f0; }
[data-testid="metric-container"] {
    background:linear-gradient(135deg,#0f1e36,#0d2040) !important;
    border:1px solid #1e3a5f !important; border-radius:12px !important;
    padding:12px 16px !important;
}
[data-testid="metric-container"] label {
    color:#64a0d4 !important; font-size:12px !important;
    font-weight:600 !important; text-transform:uppercase; letter-spacing:.5px;
}
[data-testid="metric-container"] [data-testid="stMetricValue"] {
    color:#f0f9ff !important; font-size:26px !important; font-weight:800 !important;
}
[data-testid="stExpander"] {
    background:#0a1628 !important; border:1px solid #1e3a5f !important;
    border-radius:10px !important;
}
[data-testid="stExpander"] summary { color:#93c5fd !important; font-weight:600; }
[data-testid="stDataFrame"] {
    background:#0a1628 !important; border:1px solid #1e3a5f !important;
    border-radius:10px !important;
}
.stButton > button {
    background:linear-gradient(135deg,#1d4ed8,#2563eb) !important;
    color:#fff !important; border:none !important; border-radius:10px !important;
    font-weight:700 !important; font-size:13px !important; padding:10px 22px !important;
    transition:all .2s !important; box-shadow:0 4px 15px rgba(37,99,235,.4) !important;
}
.stButton > button:hover {
    background:linear-gradient(135deg,#2563eb,#3b82f6) !important;
    box-shadow:0 6px 20px rgba(59,130,246,.5) !important;
    transform:translateY(-1px) !important;
}
.stRadio > div { gap:6px; }
.stRadio > div > label {
    background:#0f2744 !important; border:1px solid #1e4976 !important;
    border-radius:8px !important; padding:6px 14px !important; font-size:12px !important;
    cursor:pointer !important; color:#93c5fd !important; transition:all .2s;
}
.stRadio > div > label:has(input:checked) {
    background:linear-gradient(135deg,#1d4ed8,#2563eb) !important;
    border-color:#3b82f6 !important; color:#fff !important;
}
[data-testid="stFileUploader"] {
    background:#0a1e3c !important; border:1px dashed #2563eb !important;
    border-radius:10px !important; padding:12px !important;
}
.stSelectbox > div > div {
    background:#0f2744 !important; border:1px solid #1e4976 !important;
    color:#e2e8f0 !important; border-radius:8px !important;
}
.stCaption { color:#64748b !important; font-size:11px !important; }
.hero-banner {
    background:linear-gradient(135deg,#020e24 0%,#0a1f40 50%,#071830 100%);
    border:1px solid #1e3a5f; border-radius:16px; padding:28px 32px;
    margin-bottom:28px; position:relative; overflow:hidden;
}
.hero-banner::before {
    content:''; position:absolute; top:-60px; right:-60px;
    width:220px; height:220px;
    background:radial-gradient(circle,rgba(59,130,246,.15) 0%,transparent 70%);
    border-radius:50%;
}
.hero-banner h1 {
    margin:0 0 6px 0; font-size:28px; font-weight:900;
    background:linear-gradient(90deg,#60a5fa,#a78bfa,#34d399);
    -webkit-background-clip:text; -webkit-text-fill-color:transparent; background-clip:text;
}
.hero-banner p { margin:0; color:#64748b; font-size:13px; }
.hero-pills { display:flex; gap:10px; margin-top:14px; flex-wrap:wrap; }
.pill {
    background:rgba(59,130,246,.12); border:1px solid rgba(59,130,246,.3);
    border-radius:20px; padding:4px 14px; font-size:11px; color:#93c5fd; font-weight:600;
}
.module-banner {
    border-radius:14px; padding:18px 24px; margin-bottom:22px;
    position:relative; overflow:hidden;
}
.module-banner::after {
    content:''; position:absolute; top:0;left:0;right:0;bottom:0;
    background:rgba(0,0,0,.35); border-radius:14px; pointer-events:none;
}
.module-banner-inner { position:relative; z-index:1; }
.module-banner h3  { margin:0 0 4px 0; font-size:18px; font-weight:800; color:#fff; }
.module-banner p   { margin:0; font-size:12px; color:rgba(255,255,255,.7); line-height:1.6; }
.module-banner .problem-tag {
    display:inline-block; margin-top:8px;
    background:rgba(0,0,0,.35); border:1px solid rgba(255,255,255,.15);
    border-radius:20px; padding:3px 12px; font-size:11px; color:rgba(255,255,255,.8);
}
.ai-box-wrap {
    background:linear-gradient(135deg,#07101f 0%,#0c1a30 60%,#091525 100%);
    border:1px solid #1e4070; border-radius:14px; padding:20px 24px; margin-top:18px;
    box-shadow:0 8px 32px rgba(0,0,0,.5),inset 0 1px 0 rgba(99,102,241,.15);
    position:relative; overflow:hidden;
}
.ai-box-wrap::before {
    content:''; position:absolute; top:-40px; right:-40px; width:160px; height:160px;
    background:radial-gradient(circle,rgba(99,102,241,.12) 0%,transparent 70%);
    border-radius:50%;
}
.ai-header {
    display:flex; align-items:center; gap:10px; margin-bottom:14px;
    padding-bottom:12px; border-bottom:1px solid #1e3a5f;
}
.ai-header-badge {
    background:linear-gradient(135deg,#4f46e5,#7c3aed); border-radius:8px;
    padding:4px 12px; font-size:10px; font-weight:800; color:#fff;
    letter-spacing:1px; text-transform:uppercase;
}
.ai-header-model { font-size:11px; color:#475569; }
.ai-content {
    color:#cbd5e1 !important; font-size:13.5px; line-height:1.85;
    white-space:pre-wrap; position:relative; z-index:1;
}
.ai-content strong { color:#93c5fd !important; font-weight:700; }
.section-header {
    display:flex; align-items:center; gap:10px;
    margin:22px 0 14px 0; padding-bottom:10px; border-bottom:1px solid #1e3a5f;
}
.section-header span {
    font-size:14px; font-weight:700; color:#93c5fd;
    text-transform:uppercase; letter-spacing:.5px;
}
.alert-critical {
    background:linear-gradient(135deg,#1a0a0a,#2d0f0f); border:1px solid #7f1d1d;
    border-left:4px solid #ef4444; border-radius:10px; padding:12px 16px;
    color:#fca5a5; font-size:12px; margin-bottom:12px;
}
.alert-info {
    background:linear-gradient(135deg,#0a1a2e,#0d2040); border:1px solid #1e4070;
    border-left:4px solid #3b82f6; border-radius:10px; padding:12px 16px;
    color:#93c5fd; font-size:12px; margin-bottom:12px;
}
.alert-warning {
    background:linear-gradient(135deg,#1a140a,#2d1f06); border:1px solid #78350f;
    border-left:4px solid #f59e0b; border-radius:10px; padding:12px 16px;
    color:#fcd34d; font-size:12px; margin-bottom:12px;
}
.sidebar-logo { text-align:center; padding:16px 0 8px 0; }
.sidebar-logo .logo-icon { font-size:40px; display:block; }
.sidebar-logo h2 {
    margin:8px 0 2px 0; font-size:15px; font-weight:800;
    background:linear-gradient(90deg,#60a5fa,#a78bfa);
    -webkit-background-clip:text; -webkit-text-fill-color:transparent; background-clip:text;
}
.sidebar-logo p { font-size:10px; color:#475569; margin:0; }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
#  PLOTLY DARK THEME
# ══════════════════════════════════════════════════════════════
_DARK_BASE = dict(
    paper_bgcolor="#0a1628",
    plot_bgcolor="#0a1628",
    font=dict(color="#94a3b8", family="Inter, sans-serif"),
    title_font=dict(color="#e2e8f0", size=15, family="Inter, sans-serif"),
    margin=dict(t=52, b=32, l=16, r=16),
    xaxis=dict(gridcolor="#0f2240", linecolor="#1e3a5f",
               tickfont=dict(color="#64748b"), zerolinecolor="#1e3a5f"),
    yaxis=dict(gridcolor="#0f2240", linecolor="#1e3a5f",
               tickfont=dict(color="#64748b"), zerolinecolor="#1e3a5f"),
)
_LEGEND_DEFAULT = dict(
    bgcolor="rgba(10,22,40,0.8)", bordercolor="#1e3a5f", borderwidth=1,
    font=dict(color="#94a3b8", size=11), orientation="h", y=-0.22,
)

def dark(fig, height=380, legend=True, **extra):
    layout = {**_DARK_BASE, "height": height, **extra}
    if legend is True:
        layout["legend"] = _LEGEND_DEFAULT
    elif isinstance(legend, dict):
        layout["legend"] = {**_LEGEND_DEFAULT, **legend}
    fig.update_layout(**layout)
    return fig

def pc(fig):
    st.plotly_chart(fig, width="stretch")

def hex_to_rgba(hex_color, alpha=0.18):
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2],16), int(h[2:4],16), int(h[4:6],16)
    return f"rgba({r},{g},{b},{alpha})"

PALETTE = ["#6366f1","#10b981","#f59e0b","#ec4899","#38bdf8",
           "#8b5cf6","#fb923c","#84cc16","#06b6d4","#f43f5e"]

# ══════════════════════════════════════════════════════════════
#  ENCODING HELPERS  (fix: sanitize both IN and OUT to Groq)
# ══════════════════════════════════════════════════════════════
_NON_ASCII = {
    '\u00b7': '-',  '\u2022': '-',  '\u2013': '-',  '\u2014': '--',
    '\u2018': "'",  '\u2019': "'",  '\u201c': '"',  '\u201d': '"',
    '\u2026': '...', '\u00a0': ' ', '\u00b1': '+-', '\u2192': '->',
    '\u2190': '<-',  '\u2713': 'ok', '\u2717': 'x',  '\u00d7': 'x',
    '\u00f7': '/',   '\u03b1': 'a',  '\u03b2': 'b',  '\u03bb': 'l',
}

def _sanitize(text: str) -> str:
    """Strip all non-ASCII from any string — used on BOTH prompts and responses."""
    for ch, rep in _NON_ASCII.items():
        text = text.replace(ch, rep)
    # Final sweep: replace anything still outside ASCII range
    return text.encode('ascii', errors='replace').decode('ascii')

# ══════════════════════════════════════════════════════════════
#  DEMO DATASETS
# ══════════════════════════════════════════════════════════════
DEMO = {
    "forecast": pd.DataFrame({
        "month":         ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"],
        "actual_demand": [4200,3800,5100,4700,5400,6200,5900,6800,None,None,None,None],
        "promo_flag":    [0,0,1,0,0,1,0,0,0,0,1,1],
    }),
    "inventory": pd.DataFrame({
        "sku":           ["SKU-001","SKU-002","SKU-003","SKU-004","SKU-005"],
        "item_name":     ["Widget A","Component B","Assembly C","Part D","Module E"],
        "stock":         [1240,88,430,22,670],
        "reorder_point": [500,200,150,300,200],
        "eoq":           [620,340,280,410,380],
        "safety_stock":  [180,120,90,210,140],
        "daily_demand":  [90,45,60,110,35],
        "lead_time_days":[7,14,5,21,8],
        "unit_cost":     [12.5,34.0,8.75,22.0,45.50],
    }),
    "supplier": pd.DataFrame({
        "supplier_name":  ["AlphaParts Co.","BetaManufacturing","Gamma Logistics","Delta Supplies","Epsilon Tech"],
        "delivery_pct":   [94,71,85,62,97],
        "quality_pct":    [88,76,90,69,95],
        "cost_score":     [82,91,78,95,72],
        "lead_time_days": [7,14,10,21,5],
        "annual_spend":   [420000,310000,185000,275000,540000],
        "single_source":  [0,1,0,1,0],
    }),
    "sop": pd.DataFrame({
        "department": ["Sales","Demand Plan","Production Capacity","Procurement"],
        "q1":[12400,11800,13000,11500],
        "q2":[15200,14600,13500,14800],
        "q3":[13800,14200,14000,13600],
        "q4":[16900,15800,14500,15200],
    }),
    "kpi": pd.DataFrame({
        "kpi_name":     ["OTIF Rate","Inventory Turns","Fill Rate","Avg Lead Time","Forecast Accuracy","Supplier OTIF"],
        "current_value":[87.4,8.2,91.8,12.3,73.5,79.2],
        "target_value": [95.0,12.0,98.0,8.0,90.0,92.0],
        "unit":         ["%","x","%","days","%","%"],
        "trend":        [-1.2,0.4,0.9,1.1,-2.8,-0.5],
    }),
}

SCHEMAS = {
    "forecast":  "month | actual_demand | promo_flag",
    "inventory": "sku | item_name | stock | reorder_point | eoq | safety_stock | daily_demand | lead_time_days | unit_cost",
    "supplier":  "supplier_name | delivery_pct | quality_pct | cost_score | lead_time_days | annual_spend | single_source",
    "sop":       "department | q1 | q2 | q3 | q4",
    "kpi":       "kpi_name | current_value | target_value | unit | trend",
}

MODULE_META = {
    "forecast":  {"icon":"📈","title":"Demand Forecast Engine",  "color":"#6366f1",
                  "grad":"linear-gradient(135deg,#312e81,#1e1b4b,#0f0d2e)",
                  "problem":"Analysts manually tweak spreadsheets - 30% forecast errors - overstock or stockouts bleed cash every quarter."},
    "inventory": {"icon":"📦","title":"Inventory Health Monitor","color":"#10b981",
                  "grad":"linear-gradient(135deg,#064e3b,#065f46,#022c22)",
                  "problem":"No dynamic EOQ/safety-stock model - working capital locked in dead stock OR stockouts tank fill rate."},
    "supplier":  {"icon":"🏭","title":"Supplier Risk Radar",     "color":"#f59e0b",
                  "grad":"linear-gradient(135deg,#78350f,#92400e,#451a03)",
                  "problem":"Single-source concentration + zero early-warning scores - one supplier failure cascades into a production shutdown."},
    "sop":       {"icon":"🔄","title":"S&OP Alignment Monitor",  "color":"#ec4899",
                  "grad":"linear-gradient(135deg,#831843,#9d174d,#4a0520)",
                  "problem":"Sales, Demand Planning, Production & Procurement run different numbers - wrong product, wrong time, wrong place."},
    "kpi":       {"icon":"📊","title":"KPI Command Center",      "color":"#38bdf8",
                  "grad":"linear-gradient(135deg,#0c4a6e,#075985,#082f49)",
                  "problem":"OTIF, fill rates, lead times tracked in 10 spreadsheets by 10 people - leadership decides on stale conflicting data."},
}

GROQ_MODEL = "llama-3.3-70b-versatile"

# ══════════════════════════════════════════════════════════════
#  CORE HELPERS
# ══════════════════════════════════════════════════════════════
def get_df(key):
    return st.session_state.get(f"upload_{key}", DEMO[key]).copy()

def is_demo(key):
    return f"upload_{key}" not in st.session_state

def to_csv_bytes(df):
    return df.to_csv(index=False).encode()

def read_upload(file):
    if file is None:
        return None
    try:
        n = file.name.lower()
        return pd.read_csv(file) if n.endswith(".csv") else pd.read_excel(file)
    except Exception as e:
        st.error(f"Could not read file: {e}")
    return None

def groq_insight(api_key, system, user):
    if not api_key:
        return ("Add your Groq API key in the sidebar to unlock AI insights.\n\n"
                "Get a free key at console.groq.com -- takes 30 seconds.")
    try:
        # Sanitize inputs first — remove every non-ASCII character
        clean_sys  = _sanitize(system)
        clean_user = _sanitize(user)

        # Build payload — ensure_ascii=True escapes anything _sanitize missed
        payload_bytes = _json.dumps({
            "model": GROQ_MODEL,
            "messages": [
                {"role": "system", "content": clean_sys},
                {"role": "user",   "content": clean_user},
            ],
            "max_tokens": 900,
            "temperature": 0.3,
        }, ensure_ascii=True).encode("ascii")  # pure ASCII bytes, no codec issues

        # urllib.request gives full byte-level control — no latin-1 surprises
        # from requests/http.client internals (affects Python 3.14+)
        req = urllib.request.Request(
            "https://api.groq.com/openai/v1/chat/completions",
            data=payload_bytes,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = _json.loads(resp.read().decode("utf-8"))
        raw = result["choices"][0]["message"]["content"].strip()
        return _sanitize(raw)

    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")[:200]
        return f"Groq API error {e.code}: {body}"
    except Exception as e:
        return f"Error: {_sanitize(str(e))}"

def render_ai_box(text):
    lines = text.split("\n")
    html_lines = []
    for line in lines:
        line = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', line)
        stripped = line.strip()
        if stripped.startswith(("-", "*", "?")):
            line = "&nbsp;&nbsp;" + stripped[1:].strip()
        html_lines.append(line)
    formatted = "<br>".join(html_lines)
    st.markdown(f"""
    <div class="ai-box-wrap">
        <div class="ai-header">
            <div class="ai-header-badge">AI Insight</div>
            <div class="ai-header-model">llama-3.3-70b-versatile via Groq</div>
        </div>
        <div class="ai-content">{formatted}</div>
    </div>""", unsafe_allow_html=True)

def module_banner(key):
    m = MODULE_META[key]
    st.markdown(f"""
    <div class="module-banner" style="background:{m['grad']};border:1px solid {m['color']}40;">
        <div class="module-banner-inner">
            <h3>{m['icon']} {m['title']}</h3>
            <p>Problem being solved: {m['problem']}</p>
            <span class="problem-tag">One of 5 core supply chain resource problems solved here</span>
        </div>
    </div>""", unsafe_allow_html=True)

def sh(icon, label):
    st.markdown(
        f'<div class="section-header"><span style="font-size:16px">{icon}</span>'
        f'<span>{label}</span></div>', unsafe_allow_html=True)

def alert(kind, msg):
    cls = {"critical":"alert-critical","info":"alert-info","warning":"alert-warning"}[kind]
    st.markdown(f'<div class="{cls}">{msg}</div>', unsafe_allow_html=True)

def data_source_panel(module_key):
    st.sidebar.markdown("---")
    st.sidebar.markdown("**Data Source**")
    use_demo = st.sidebar.radio(
        "Data source choice",
        ["Use Demo Dataset", "Upload My Data"],
        key=f"radio_{module_key}",
        label_visibility="collapsed",
    )
    if use_demo == "Upload My Data":
        st.sidebar.caption(f"Columns: `{SCHEMAS[module_key]}`")
        f = st.sidebar.file_uploader(
            "Upload CSV or Excel", type=["csv","xlsx","xls"],
            key=f"file_{module_key}",
        )
        df_up = read_upload(f)
        if df_up is not None:
            st.session_state[f"upload_{module_key}"] = df_up
            st.sidebar.success(f"Loaded {len(df_up)} rows")
        elif f"upload_{module_key}" in st.session_state:
            del st.session_state[f"upload_{module_key}"]
    else:
        st.session_state.pop(f"upload_{module_key}", None)
    st.sidebar.download_button(
        "Download CSV Template",
        data=to_csv_bytes(DEMO[module_key]),
        file_name=f"template_{module_key}.csv",
        mime="text/csv", key=f"dl_{module_key}",
    )

# ══════════════════════════════════════════════════════════════
#  MODULE 1 — DEMAND FORECAST
# ══════════════════════════════════════════════════════════════
def module_forecast_ui(api_key):
    module_banner("forecast")
    df = get_df("forecast")

    with st.expander(f"Raw Dataset {'(Demo)' if is_demo('forecast') else '(Uploaded)'}", False):
        st.dataframe(df, width="stretch")

    actuals = df[df["actual_demand"].notna()]["actual_demand"].astype(float).tolist()
    months  = df["month"].tolist()
    n       = len(actuals)

    alpha = 0.35
    ema = [actuals[0]]
    for v in actuals[1:]:
        ema.append(alpha * v + (1 - alpha) * ema[-1])

    x = np.arange(n)
    slope, intercept = np.polyfit(x, actuals, 1) if n > 1 else (0, actuals[0])
    forecast_vals = [
        max(0, round(intercept + slope * i +
                     np.random.uniform(-0.04, 0.04) * (intercept + slope * i)))
        for i in range(n, len(months))
    ]

    mape       = np.mean([abs(a-e)/a*100 for a,e in zip(actuals[-3:],ema[-3:])]) if n >= 3 else 0
    accuracy   = round(max(0, 100 - mape), 1)
    volatility = round(np.std(actuals) / np.mean(actuals) * 100, 1)

    promo_months = []
    if "promo_flag" in df.columns:
        promo_months = [months[i] for i,v in enumerate(df["promo_flag"].tolist())
                        if v == 1 and i < n]

    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Avg Monthly Demand", f"{int(np.mean(actuals)):,} u")
    c2.metric("EMA Accuracy",       f"{accuracy}%", f"{accuracy-90:.1f}% vs 90% target")
    c3.metric("Demand Volatility",  f"+-{volatility}%", "High" if volatility > 15 else "Moderate")
    c4.metric("Projected Next Qtr",
              f"{int(np.mean(forecast_vals[:3])):,} u/mo" if forecast_vals else "N/A")

    sh("📊", "Demand Timeline - Actuals, EMA, Forecast")
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=months[:n], y=actuals, name="Actual Demand",
        marker=dict(color=actuals,
                    colorscale=[[0,"#312e81"],[.5,"#6366f1"],[1,"#a5b4fc"]],
                    showscale=False, line=dict(width=0)),
        hovertemplate="<b>%{x}</b><br>Actual: %{y:,} units<extra></extra>",
    ))
    fig.add_trace(go.Scatter(
        x=months[:n], y=[round(v) for v in ema],
        name="EMA Smoothing", mode="lines+markers",
        line=dict(color="#f59e0b", width=2.5, dash="dot"),
        marker=dict(size=6, color="#f59e0b"),
    ))
    if forecast_vals:
        fig.add_trace(go.Bar(
            x=months[n:], y=forecast_vals, name="Forecast",
            marker=dict(color="#1e3a8a", line=dict(color="#6366f1", width=1.5)),
            hovertemplate="<b>%{x}</b><br>Forecast: %{y:,} units<extra></extra>",
        ))
    for pm in promo_months:
        idx = months.index(pm)
        fig.add_vline(x=idx, line_dash="dash", line_color="#ec4899", line_width=1,
                      annotation_text="Promo", annotation_position="top")
    pc(dark(fig, height=380, barmode="overlay", legend=dict(y=-0.18)))

    sh("📉", "Demand Trend & Growth Rate")
    col_a, col_b = st.columns(2)
    with col_a:
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(
            x=months[:n], y=actuals, fill="tozeroy",
            fillcolor="rgba(99,102,241,0.15)",
            line=dict(color="#6366f1", width=2), mode="lines",
        ))
        pc(dark(fig2, height=220, legend=False, title="Demand Area",
                margin=dict(t=32,b=16,l=8,r=8)))
    with col_b:
        mom = [round((actuals[i]-actuals[i-1])/actuals[i-1]*100,1) if i>0 else 0
               for i in range(n)]
        fig3 = go.Figure(go.Bar(
            x=months[:n], y=mom,
            marker_color=["#10b981" if v >= 0 else "#ef4444" for v in mom],
            text=[f"{v:+.1f}%" for v in mom], textposition="outside",
            textfont=dict(color="#e2e8f0"),
        ))
        fig3.add_hline(y=0, line_color="#334155", line_width=1)
        pc(dark(fig3, height=220, legend=False, title="Month-on-Month Growth %",
                margin=dict(t=32,b=16,l=8,r=8)))

    if promo_months:
        alert("info", f"<b>Promo months detected:</b> {', '.join(promo_months)} - factored into projection")

    sh("🤖", "AI Demand Analysis")
    if st.button("Run AI Forecast Analysis", key="btn_forecast"):
        with st.spinner("Analyzing with Groq..."):
            data_str = ", ".join([f"{m}: {v}" for m,v in zip(months[:n], actuals)])
            proj_str  = ", ".join([f"{m}: {v}" for m,v in zip(months[n:], forecast_vals)])
            render_ai_box(groq_insight(api_key,
                "You are a senior supply chain demand planning analyst. Be specific with numbers. Bold key findings with **text**.",
                f"Historical demand: {data_str}\n"
                f"EMA projection: {proj_str}\n"
                f"Forecast accuracy: {accuracy}% (target 90%)\n"
                f"Demand volatility: +-{volatility}%\n"
                f"Promo months: {promo_months or 'None'}\n\n"
                f"Provide:\n"
                f"1. Trend direction and monthly growth rate\n"
                f"2. Seasonality patterns and peak risk months\n"
                f"3. Root cause of forecast accuracy gap\n"
                f"4. Top 3 immediate actions to improve accuracy\n"
                f"5. Recommended safety stock buffer % for this volatility\n"
                f"6. Stockout or overstock risk next quarter with estimated $ exposure"
            ))

# ══════════════════════════════════════════════════════════════
#  MODULE 2 — INVENTORY HEALTH
# ══════════════════════════════════════════════════════════════
def module_inventory_ui(api_key):
    module_banner("inventory")
    df = get_df("inventory")

    df["days_of_supply"] = (df["stock"] / df["daily_demand"]).round(1)
    df["working_capital"] = (df["stock"] * df["unit_cost"]).round(2)
    df["excess_units"]    = (df["stock"] - df["eoq"] - df["safety_stock"]).clip(lower=0)
    df["locked_capital"]  = (df["excess_units"] * df["unit_cost"]).round(2)

    def classify(r):
        if r["stock"] < r["safety_stock"]:              return "Critical"
        if r["days_of_supply"] < r["lead_time_days"]:   return "Stockout Risk"
        if r["stock"] > 2 * r["eoq"] + r["safety_stock"]: return "Overstock"
        return "Healthy"
    df["status"] = df.apply(classify, axis=1)

    with st.expander(f"Raw Dataset {'(Demo)' if is_demo('inventory') else '(Uploaded)'}", False):
        st.dataframe(df, width="stretch")

    critical  = df[df["status"].isin(["Critical","Stockout Risk"])]
    overstock = df[df["status"] == "Overstock"]
    total_locked = overstock["locked_capital"].sum()
    total_wc     = df["working_capital"].sum()

    c1,c2,c3,c4 = st.columns(4)
    c1.metric("SKUs at Risk",     len(critical),  f"{len(critical)} need action now")
    c2.metric("Overstock SKUs",   len(overstock))
    c3.metric("Capital Locked",   f"${total_locked:,.0f}", "excess above EOQ+SS")
    c4.metric("Total Inv. Value", f"${total_wc:,.0f}")

    if not critical.empty:
        alert("critical",
              "<b>Immediate Action Required:</b> " +
              " | ".join([f"<b>{r.sku}</b> ({r.item_name}): {r.days_of_supply}d supply, LT {r.lead_time_days}d"
                          for _,r in critical.iterrows()]))

    sh("📦", "Stock Levels vs Thresholds")
    names = df["item_name"].tolist()
    fig = go.Figure()
    fig.add_trace(go.Bar(x=names, y=df["stock"],         name="Current Stock",  marker_color="#6366f1"))
    fig.add_trace(go.Bar(x=names, y=df["reorder_point"], name="Reorder Point",  marker_color="#f59e0b"))
    fig.add_trace(go.Bar(x=names, y=df["safety_stock"],  name="Safety Stock",   marker_color="#ef4444"))
    fig.add_trace(go.Scatter(x=names, y=df["eoq"], name="EOQ", mode="markers+lines",
                             marker=dict(size=10, color="#10b981", symbol="diamond"),
                             line=dict(dash="dot", color="#10b981", width=2)))
    pc(dark(fig, height=360, barmode="group"))

    sh("💰", "Capital & Days-of-Supply Breakdown")
    col_a, col_b = st.columns(2)
    with col_a:
        fig2 = go.Figure(go.Pie(
            labels=df["item_name"], values=df["working_capital"], hole=0.52,
            marker=dict(colors=PALETTE[:len(df)], line=dict(color="#0a1628", width=2)),
            textinfo="label+percent", textfont=dict(color="#e2e8f0", size=11),
        ))
        pc(dark(fig2, height=300, legend=False, title="Working Capital by SKU",
                margin=dict(t=40,b=0,l=0,r=0)))
    with col_b:
        dos = df["days_of_supply"].tolist()
        fig3 = go.Figure(go.Bar(
            x=df["item_name"], y=dos,
            marker_color=["#ef4444" if d<5 else "#f59e0b" if d<14 else "#10b981" for d in dos],
            text=[f"{d}d" for d in dos], textposition="outside",
            textfont=dict(color="#e2e8f0"),
        ))
        fig3.add_hline(y=14, line_dash="dot", line_color="#f59e0b",
                       annotation_text="14d threshold", annotation_font_color="#f59e0b")
        pc(dark(fig3, height=300, legend=False, title="Days of Supply per SKU",
                margin=dict(t=40,b=16,l=8,r=8)))

    sh("🌡", "Inventory Status Heatmap")
    heat_vals = df[["stock","reorder_point","safety_stock","eoq","days_of_supply"]].values.T
    fig4 = go.Figure(go.Heatmap(
        z=heat_vals, x=df["item_name"].tolist(),
        y=["Stock","Reorder Pt","Safety Stock","EOQ","Days Supply"],
        colorscale=[[0,"#0f172a"],[.3,"#1e3a5f"],[.6,"#6366f1"],[1,"#a5b4fc"]],
        texttemplate="%{z:,.0f}", textfont=dict(size=11, color="#e2e8f0"),
    ))
    pc(dark(fig4, height=240, legend=False, margin=dict(t=20,b=20,l=100,r=16)))

    sh("🤖", "AI Inventory Analysis")
    if st.button("Run AI Inventory Analysis", key="btn_inventory"):
        with st.spinner("Analyzing with Groq..."):
            rows = df[["sku","item_name","stock","reorder_point","eoq","safety_stock",
                        "daily_demand","lead_time_days","days_of_supply","status",
                        "working_capital","locked_capital"]].to_dict("records")
            render_ai_box(groq_insight(api_key,
                "You are a senior inventory optimization analyst. Be specific with numbers. Bold key findings with **text**.",
                f"Inventory portfolio: {rows}\n"
                f"Total working capital: ${total_wc:,.0f}\n"
                f"Locked in overstock: ${total_locked:,.0f}\n\n"
                f"Provide:\n"
                f"1. Top 2 SKUs needing immediate PO or production stop\n"
                f"2. Exact order quantity per critical/stockout-risk SKU\n"
                f"3. Overstock reduction plan with timeline\n"
                f"4. Working capital freed if right-sized to EOQ + Safety Stock\n"
                f"5. Safety stock formula recommendation for these lead times\n"
                f"6. One systemic fix to prevent recurrence"
            ))

# ══════════════════════════════════════════════════════════════
#  MODULE 3 — SUPPLIER RISK
# ══════════════════════════════════════════════════════════════
def module_supplier_ui(api_key):
    module_banner("supplier")
    df = get_df("supplier")

    df["composite_score"] = (
        df["delivery_pct"] * 0.40 +
        df["quality_pct"]  * 0.35 +
        df["cost_score"]   * 0.25
    ).round(1)
    df["risk_tier"]   = df["composite_score"].apply(
        lambda s: "Low" if s>=85 else ("Medium" if s>=70 else ("High" if s>=55 else "Critical")))
    df["spend_share"] = (df["annual_spend"] / df["annual_spend"].sum() * 100).round(1)

    total_spend   = df["annual_spend"].sum()
    at_risk_spend = df[df["risk_tier"].isin(["High","Critical"])]["annual_spend"].sum()
    ss_spend      = df[df["single_source"]==1]["annual_spend"].sum() \
                    if "single_source" in df.columns else 0
    risk_colors   = {"Low":"#10b981","Medium":"#f59e0b","High":"#ef4444","Critical":"#dc2626"}

    with st.expander(f"Raw Dataset {'(Demo)' if is_demo('supplier') else '(Uploaded)'}", False):
        st.dataframe(df, width="stretch")

    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Total Supplier Spend", f"${total_spend:,.0f}")
    c2.metric("At-Risk Spend",        f"${at_risk_spend:,.0f}",
              f"{at_risk_spend/total_spend*100:.0f}% of portfolio")
    c3.metric("Single-Source Spend",  f"${ss_spend:,.0f}", "Concentration risk")
    c4.metric("Avg Composite Score",  f"{df['composite_score'].mean():.1f}")

    high_risk = df[df["risk_tier"].isin(["High","Critical"])]
    if not high_risk.empty:
        alert("critical",
              "<b>High/Critical Risk Suppliers:</b> " +
              " | ".join([f"<b>{r.supplier_name}</b> score {r.composite_score} | ${r.annual_spend:,.0f}"
                          for _,r in high_risk.iterrows()]))

    sh("📊", "Supplier Scorecard")
    fig = go.Figure()
    fig.add_trace(go.Bar(x=df["supplier_name"], y=df["delivery_pct"], name="Delivery %",  marker_color="#6366f1"))
    fig.add_trace(go.Bar(x=df["supplier_name"], y=df["quality_pct"],  name="Quality %",   marker_color="#10b981"))
    fig.add_trace(go.Bar(x=df["supplier_name"], y=df["cost_score"],   name="Cost Score",  marker_color="#f59e0b"))
    fig.add_trace(go.Scatter(
        x=df["supplier_name"], y=df["composite_score"],
        name="Composite Score", mode="lines+markers",
        line=dict(color="#ec4899", width=3),
        marker=dict(size=12, color=[risk_colors.get(r,"#64748b") for r in df["risk_tier"]],
                    symbol="diamond", line=dict(color="#fff", width=1.5)),
    ))
    fig.add_hline(y=70, line_dash="dot", line_color="#ef4444",
                  annotation_text="Risk threshold (70)", annotation_font_color="#ef4444")
    fig.add_hline(y=85, line_dash="dot", line_color="#10b981",
                  annotation_text="Healthy (85)", annotation_font_color="#10b981")
    pc(dark(fig, height=360, barmode="group"))

    sh("🔵", "Risk vs Spend Exposure")
    col_a, col_b = st.columns([3, 2])
    with col_a:
        fig2 = go.Figure()
        for _,row in df.iterrows():
            clr = risk_colors.get(row["risk_tier"], "#64748b")
            fig2.add_trace(go.Scatter(
                x=[row["composite_score"]], y=[row["annual_spend"]],
                mode="markers+text",
                marker=dict(size=row["lead_time_days"]*3.5, color=clr, opacity=.75,
                            line=dict(color=clr, width=2)),
                text=[row["supplier_name"]], textposition="top center",
                textfont=dict(color="#e2e8f0", size=11),
                name=row["supplier_name"],
                hovertemplate=(f"<b>{row['supplier_name']}</b><br>"
                               f"Score: {row['composite_score']}<br>"
                               f"Spend: ${row['annual_spend']:,.0f}<extra></extra>"),
            ))
        fig2.add_vline(x=70, line_dash="dot", line_color="#ef4444")
        pc(dark(fig2, height=340, legend=False, title="Score vs Spend (bubble = lead time)",
                xaxis=dict(**_DARK_BASE["xaxis"], title="Composite Score"),
                yaxis=dict(**_DARK_BASE["yaxis"], title="Annual Spend ($)")))
    with col_b:
        fig3 = go.Figure(go.Pie(
            labels=df["supplier_name"], values=df["annual_spend"], hole=0.55,
            marker=dict(colors=[risk_colors.get(r,"#64748b") for r in df["risk_tier"]],
                        line=dict(color="#0a1628", width=2)),
            textinfo="percent", textfont=dict(color="#e2e8f0", size=10),
        ))
        pc(dark(fig3, height=340, title="Spend by Supplier",
                margin=dict(t=40,b=0,l=0,r=0)))

    sh("📡", "Supplier Deep Dive - Radar")
    sel = st.selectbox("Select supplier to inspect", df["supplier_name"].tolist(), key="sup_radar")
    row = df[df["supplier_name"] == sel].iloc[0]
    cats = ["Delivery %","Quality %","Cost Score","Lead Time Inv.","Composite"]
    vals = [
        row["delivery_pct"], row["quality_pct"], row["cost_score"],
        max(0, 100 - (row["lead_time_days"] / 30) * 100),
        row["composite_score"],
    ]
    clr = risk_colors.get(row["risk_tier"], "#6366f1")
    fig4 = go.Figure()
    fig4.add_trace(go.Scatterpolar(
        r=vals + [vals[0]], theta=cats + [cats[0]],
        fill="toself",
        fillcolor=hex_to_rgba(clr),   # fix: rgba() not 8-digit hex
        line=dict(color=clr, width=2.5),
        marker=dict(size=7, color=clr),
        name=sel,
    ))
    fig4.add_trace(go.Scatterpolar(
        r=[85]*len(cats)+[85], theta=cats+[cats[0]],
        line=dict(color="#334155", dash="dot", width=1),
        fill=None, name="Healthy Threshold",
    ))
    fig4.update_layout(
        polar=dict(
            bgcolor="#0a1628",
            radialaxis=dict(visible=True, range=[0,100], gridcolor="#1e3a5f",
                            tickfont=dict(color="#64748b", size=9)),
            angularaxis=dict(gridcolor="#1e3a5f", tickfont=dict(color="#94a3b8", size=11)),
        ),
        paper_bgcolor="#0a1628", height=320,
        legend=dict(bgcolor="#0a1628", bordercolor="#1e3a5f", font=dict(color="#94a3b8")),
        margin=dict(t=20,b=20,l=40,r=40),
    )
    pc(fig4)

    sh("🤖", "AI Supplier Risk Assessment")
    if st.button("Run AI Supplier Analysis", key="btn_supplier"):
        with st.spinner("Analyzing with Groq..."):
            rows = df[["supplier_name","delivery_pct","quality_pct","cost_score",
                        "lead_time_days","annual_spend","composite_score",
                        "risk_tier","spend_share"]].to_dict("records")
            ss_names = df[df.get("single_source", pd.Series(0,index=df.index))==1][
                "supplier_name"].tolist() if "single_source" in df.columns else []
            render_ai_box(groq_insight(api_key,
                "You are a procurement and supplier risk expert. Be specific with numbers. Bold key findings with **text**.",
                f"Supplier portfolio: {rows}\n"
                f"Single-source suppliers: {ss_names or 'Not flagged'}\n"
                f"Total spend: ${total_spend:,.0f}\n"
                f"At-risk spend: ${at_risk_spend:,.0f}\n\n"
                f"Provide:\n"
                f"1. Top 2 risks with exact $ exposure if supplier fails\n"
                f"2. Which supplier needs a 30-day PIP with specific KPI targets\n"
                f"3. Dual-sourcing priorities\n"
                f"4. Negotiation leverage - who we overpay given their risk score\n"
                f"5. 30-day quick win to reduce portfolio risk\n"
                f"6. One weekly early-warning metric to track"
            ))

# ══════════════════════════════════════════════════════════════
#  MODULE 4 — S&OP ALIGNMENT
# ══════════════════════════════════════════════════════════════
def module_sop_ui(api_key):
    module_banner("sop")
    df = get_df("sop")
    quarters = ["q1","q2","q3","q4"]
    ql = {"q1":"Q1","q2":"Q2","q3":"Q3","q4":"Q4"}

    with st.expander(f"Raw Dataset {'(Demo)' if is_demo('sop') else '(Uploaded)'}", False):
        st.dataframe(df, width="stretch")

    gap_data = []
    for q in quarters:
        vals = df[q].astype(float).tolist()
        gap_data.append({
            "quarter": ql[q], "max": max(vals), "min": min(vals),
            "gap": max(vals)-min(vals),
            "gap_pct": (max(vals)-min(vals))/max(vals)*100,
        })
    gap_df  = pd.DataFrame(gap_data)
    worst_q = gap_df.loc[gap_df["gap_pct"].idxmax()]
    avg_gap = gap_df["gap_pct"].mean()

    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Worst Quarter",      worst_q["quarter"])
    c2.metric("Max Dept Gap",       f"{int(worst_q['gap']):,} units",
              f"{worst_q['gap_pct']:.1f}% misalignment")
    c3.metric("Avg Cross-Dept Gap", f"{avg_gap:.1f}%", "Target: <5%")
    c4.metric("Revenue at Risk*",   f"${int(worst_q['gap']*45):,}", "*@$45 ASP")

    if avg_gap > 10:
        alert("critical",
              f"<b>Critical misalignment:</b> {avg_gap:.1f}% avg gap - "
              f"revenue leakage and overproduction risk are HIGH")
    elif avg_gap > 5:
        alert("warning",
              f"<b>Moderate misalignment:</b> {avg_gap:.1f}% avg gap - "
              f"S&OP sync needed before next planning cycle")

    sh("📊", "Department Signals by Quarter")
    dept_colors = {"Sales":"#6366f1","Demand Plan":"#10b981",
                   "Production Capacity":"#f59e0b","Procurement":"#ec4899"}
    fig = go.Figure()
    for _,row in df.iterrows():
        dept = row["department"]
        fig.add_trace(go.Bar(
            name=dept, x=[ql[q] for q in quarters],
            y=[row[q] for q in quarters],
            marker_color=dept_colors.get(dept,"#64748b"),
        ))
    pc(dark(fig, height=360, barmode="group"))

    sh("🌡", "Misalignment Analysis")
    col_a, col_b = st.columns(2)
    with col_a:
        fig2 = go.Figure(go.Bar(
            x=gap_df["quarter"], y=gap_df["gap"],
            marker=dict(
                color=gap_df["gap_pct"],
                colorscale=[[0,"#064e3b"],[.4,"#f59e0b"],[.7,"#ef4444"],[1,"#dc2626"]],
                showscale=True,
                # fix: titlefont -> title=dict(font=...) for Plotly 6
                colorbar=dict(
                    title=dict(text="Gap %", font=dict(color="#94a3b8")),
                    tickfont=dict(color="#94a3b8"),
                ),
                line=dict(width=0),
            ),
            text=gap_df["gap_pct"].apply(lambda v: f"{v:.1f}%"),
            textposition="outside", textfont=dict(color="#e2e8f0"),
        ))
        pc(dark(fig2, height=300, legend=False, title="Unit Gap by Quarter",
                margin=dict(t=40,b=16,l=8,r=8)))
    with col_b:
        heat_rows = []
        for _,row in df.iterrows():
            hr = {"Department": row["department"]}
            for q in quarters:
                hr[ql[q]] = round((df[q].max()-row[q])/df[q].max()*100, 1)
            heat_rows.append(hr)
        heat_df = pd.DataFrame(heat_rows).set_index("Department")
        fig3 = go.Figure(go.Heatmap(
            z=heat_df.values, x=heat_df.columns.tolist(), y=heat_df.index.tolist(),
            colorscale=[[0,"#064e3b"],[.4,"#f59e0b"],[.7,"#ef4444"],[1,"#7f1d1d"]],
            texttemplate="%{z:.1f}%", textfont=dict(size=12, color="#fff"),
            zmin=0, zmax=20,
        ))
        pc(dark(fig3, height=300, legend=False, title="Shortfall % vs Max Signal",
                margin=dict(t=40,b=16,l=100,r=16)))

    sh("🤖", "AI S&OP Misalignment Analysis")
    if st.button("Run AI S&OP Analysis", key="btn_sop"):
        with st.spinner("Analyzing with Groq..."):
            render_ai_box(groq_insight(api_key,
                "You are a senior S&OP and supply chain planning expert. Be precise with numbers. Bold key findings with **text**.",
                f"S&OP department signals (units): {df.to_dict('records')}\n"
                f"Gap analysis: {gap_df.to_dict('records')}\n"
                f"ASP = $45/unit | Average gap: {avg_gap:.1f}%\n\n"
                f"Provide:\n"
                f"1. Most dangerous quarter with specific dept shortfall/surplus\n"
                f"2. Revenue at risk from demand > production capacity (use ASP $45)\n"
                f"3. Cost from procurement over-ordering vs demand signal\n"
                f"4. Most reliable department signal and why\n"
                f"5. Top 3 S&OP meeting action items for next cycle\n"
                f"6. One process change to get misalignment below 5%"
            ))

# ══════════════════════════════════════════════════════════════
#  MODULE 5 — KPI DASHBOARD
# ══════════════════════════════════════════════════════════════
def module_kpi_ui(api_key):
    module_banner("kpi")
    df = get_df("kpi")

    df["performance_pct"] = (df["current_value"] / df["target_value"] * 100).round(1)
    df["gap"]    = (df["target_value"] - df["current_value"]).round(2)
    df["status"] = df["performance_pct"].apply(
        lambda p: "On Target" if p>=100 else ("Near Target" if p>=85 else "Off Target"))

    with st.expander(f"Raw Dataset {'(Demo)' if is_demo('kpi') else '(Uploaded)'}", False):
        st.dataframe(df, width="stretch")

    cols = st.columns(len(df))
    for i,(_,row) in enumerate(df.iterrows()):
        need_low   = row["kpi_name"] == "Avg Lead Time"
        good_trend = (row["trend"] < 0) if need_low else (row["trend"] > 0)
        sym = "+" if row["trend"] > 0 else "-"
        cols[i].metric(
            row["kpi_name"],
            f"{row['current_value']}{row['unit']}",
            f"{sym}{abs(row['trend'])}{row['unit']}",
            delta_color="normal" if good_trend else "inverse",
        )

    sh("🎯", "Performance Gauges")
    gcols = st.columns(3)
    for i,(_,row) in enumerate(df.iterrows()):
        pct = row["performance_pct"]
        clr = "#10b981" if pct>=100 else ("#f59e0b" if pct>=85 else "#ef4444")
        fig = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=row["current_value"],
            title={"text": row["kpi_name"], "font": {"size":12,"color":"#94a3b8"}},
            delta={"reference": row["target_value"], "suffix": row["unit"],
                   "increasing":{"color":"#10b981"}, "decreasing":{"color":"#ef4444"}},
            number={"suffix": row["unit"], "font":{"color":"#e2e8f0","size":24}},
            gauge={
                # fix: gridcolor removed from axis - invalid in Plotly 6
                "axis": {"range":[0, row["target_value"]*1.25],
                         "tickfont":{"color":"#64748b","size":9}},
                "bar":  {"color": clr, "thickness": .28},
                "bgcolor": "#0a1628",
                "bordercolor": "#1e3a5f",
                "threshold": {"line":{"color":"#fff","width":3},
                              "thickness":.75, "value":row["target_value"]},
                "steps": [
                    {"range":[0, row["target_value"]*.7],  "color":"#1a0a0a"},
                    {"range":[row["target_value"]*.7,  row["target_value"]*.9],  "color":"#1a140a"},
                    {"range":[row["target_value"]*.9,  row["target_value"]*1.25],"color":"#061a10"},
                ],
            },
        ))
        fig.update_layout(paper_bgcolor="#0a1628", height=210,
                          margin=dict(t=48,b=8,l=16,r=16))
        gcols[i%3].plotly_chart(fig, width="stretch")

    sh("📊", "KPI vs Target - Gap Analysis")
    col_a, col_b = st.columns(2)
    with col_a:
        bar_clrs = ["#10b981" if p>=100 else "#f59e0b" if p>=85 else "#ef4444"
                    for p in df["performance_pct"]]
        fig2 = go.Figure(go.Bar(
            x=df["performance_pct"], y=df["kpi_name"], orientation="h",
            marker_color=bar_clrs,
            text=df["performance_pct"].apply(lambda v: f"{v:.1f}%"),
            textposition="outside", textfont=dict(color="#e2e8f0"),
        ))
        fig2.add_vline(x=100, line_dash="dot",  line_color="#334155")
        fig2.add_vline(x=85,  line_dash="dash", line_color="#f59e0b", line_width=1)
        pc(dark(fig2, height=300, legend=False, title="% of Target Achieved",
                margin=dict(t=40,b=16,l=8,r=60)))
    with col_b:
        fig3 = go.Figure(go.Heatmap(
            z=[df["performance_pct"].tolist()],
            x=df["kpi_name"].tolist(), y=["KPI Performance"],
            colorscale=[[0,"#7f1d1d"],[.5,"#78350f"],[.75,"#064e3b"],[1,"#10b981"]],
            zmin=50, zmax=110,
            texttemplate="%{z:.1f}%", textfont=dict(size=12, color="#fff"),
        ))
        pc(dark(fig3, height=300, legend=False, title="Heatmap - % of Target",
                margin=dict(t=40,b=16,l=16,r=16)))

    sh("📈", "Trend Direction per KPI")
    fig4 = go.Figure()
    for i,(_,row) in enumerate(df.iterrows()):
        need_low = row["kpi_name"] == "Avg Lead Time"
        good = (row["trend"] <= 0) if need_low else (row["trend"] >= 0)
        clr  = "#10b981" if good else "#ef4444"
        fig4.add_trace(go.Scatter(
            x=["3mo ago","2mo ago","1mo ago","Now"],
            y=[row["current_value"]-row["trend"]*3,
               row["current_value"]-row["trend"]*2,
               row["current_value"]-row["trend"],
               row["current_value"]],
            name=row["kpi_name"], mode="lines+markers",
            line=dict(color=clr, width=2), marker=dict(size=6, color=clr),
        ))
    pc(dark(fig4, height=280, legend=dict(y=-0.3, font=dict(size=10))))

    sh("🤖", "AI Executive KPI Brief")
    if st.button("Generate AI KPI Brief", key="btn_kpi"):
        with st.spinner("Analyzing with Groq..."):
            rows = df[["kpi_name","current_value","target_value","unit","trend",
                        "performance_pct","gap","status"]].to_dict("records")
            off  = df[df["performance_pct"]<100]["kpi_name"].tolist()
            render_ai_box(groq_insight(api_key,
                "You are a supply chain VP preparing an executive briefing. Be direct, specific, data-driven. Bold key findings with **text**.",
                f"KPI performance: {rows}\n"
                f"Off-target ({len(off)} of {len(df)}): {off}\n"
                f"Monthly revenue base: $10M\n\n"
                f"Provide:\n"
                f"1. Top 3 KPIs bleeding most value with $ impact per unit of gap\n"
                f"2. Causal chain - which are root causes vs symptoms\n"
                f"3. Root cause hypothesis for the worst-performing KPI\n"
                f"4. 30 / 60 / 90-day action plan (one action per period)\n"
                f"5. One untracked metric that would explain these gaps\n"
                f"6. What leadership needs to see to approve resources for fixes"
            ))

# ══════════════════════════════════════════════════════════════
#  SIDEBAR + MAIN
# ══════════════════════════════════════════════════════════════
def main():
    st.sidebar.markdown("""
    <div class="sidebar-logo">
        <span class="logo-icon">⛓</span>
        <h2>Supply Chain<br>Command Center</h2>
        <p>5 Problems · 1 Platform · Groq AI</p>
    </div>""", unsafe_allow_html=True)
    st.sidebar.markdown("---")

    st.sidebar.markdown("**Groq API Key**")
    api_key = st.sidebar.text_input(
        "Groq API Key",
        type="password",
        placeholder="gsk_...",
        label_visibility="collapsed",
        help="Free key at console.groq.com",
    )
    if api_key:
        st.sidebar.markdown(
            '<div style="color:#86efac;font-size:12px">API key active</div>',
            unsafe_allow_html=True)
    else:
        st.sidebar.markdown(
            '<div style="color:#fcd34d;font-size:12px">Add key to enable AI insights</div>',
            unsafe_allow_html=True)
    st.sidebar.markdown("---")

    st.sidebar.markdown("**Module**")
    labels = {f"{MODULE_META[k]['icon']}  {MODULE_META[k]['title']}": k for k in MODULE_META}
    sel = st.sidebar.radio(
        "Select Module",
        list(labels.keys()),
        label_visibility="collapsed",
    )
    active = labels[sel]
    data_source_panel(active)

    st.sidebar.markdown("---")
    st.sidebar.markdown("""
    <div style="font-size:10px;color:#334155;line-height:1.8">
        Model: llama-3.3-70b-versatile<br>
        Provider: Groq - Ultra-low latency<br>
        Built for Supply Chain Analysts<br>
        Solving 5 core resource-drain problems
    </div>""", unsafe_allow_html=True)

    st.markdown("""
    <div class="hero-banner">
        <h1>Supply Chain Command Center</h1>
        <p>One platform · 5 root problems eliminated · AI-powered by Groq · No more spreadsheet juggling</p>
        <div class="hero-pills">
            <span class="pill">Demand Forecast</span>
            <span class="pill">Inventory Health</span>
            <span class="pill">Supplier Risk</span>
            <span class="pill">S&OP Alignment</span>
            <span class="pill">KPI Dashboard</span>
        </div>
    </div>""", unsafe_allow_html=True)

    {
        "forecast":  module_forecast_ui,
        "inventory": module_inventory_ui,
        "supplier":  module_supplier_ui,
        "sop":       module_sop_ui,
        "kpi":       module_kpi_ui,
    }[active](api_key)


if __name__ == "__main__":
    main()
