# ============================================================
#  SUPPLY CHAIN COMMAND CENTER  |  app.py  |  FINAL v2
#  - Sidebar always visible (no collapse, fixed width)
#  - AI works: all data serialized via _safe_str() before prompts
#  - urllib only, zero external HTTP libs
#  - All Plotly 6 bugs fixed
# ============================================================

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import json, re, urllib.request, urllib.error

# ── PAGE CONFIG ──────────────────────────────────────────────
st.set_page_config(
    page_title="Supply Chain Command Center",
    page_icon="⛓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ══════════════════════════════════════════════════════════════
#  ENCODING — sanitize everything before it touches HTTP
# ══════════════════════════════════════════════════════════════
_CHAR_MAP = {
    '\u00b7':'-', '\u2022':'-', '\u2013':'-', '\u2014':'--',
    '\u2018':"'", '\u2019':"'", '\u201c':'"', '\u201d':'"',
    '\u2026':'...', '\u00a0':' ', '\u00b1':'+-', '\u2192':'->',
    '\u2190':'<-', '\u2713':'ok','\u2717':'x', '\u00d7':'x',
}

def _clean(text: str) -> str:
    for ch, rep in _CHAR_MAP.items():
        text = text.replace(ch, rep)
    return text.encode('ascii', errors='replace').decode('ascii')

def _safe_str(obj) -> str:
    """Convert ANY object (dict, list, DataFrame rows…) to a guaranteed
    pure-ASCII string.  This is the root fix for the latin-1 crash:
    never embed raw Python repr of data frames into prompt f-strings."""
    return _clean(json.dumps(obj, ensure_ascii=True, default=str))

# ══════════════════════════════════════════════════════════════
#  GROQ — urllib only, no third-party HTTP lib
# ══════════════════════════════════════════════════════════════
GROQ_MODEL = "llama-3.3-70b-versatile"

def groq_insight(api_key: str, system: str, user: str) -> str:
    if not api_key:
        return ("Enter your Groq API key in the sidebar to unlock AI insights.\n"
                "Get a free key at console.groq.com -- 30 seconds to set up.")
    try:
        payload = json.dumps({
            "model": GROQ_MODEL,
            "messages": [
                {"role": "system", "content": _clean(system)},
                {"role": "user",   "content": _clean(user)},
            ],
            "max_tokens": 900,
            "temperature": 0.3,
        }, ensure_ascii=True).encode("ascii")   # pure ASCII bytes — no codec issues

        req = urllib.request.Request(
            "https://api.groq.com/openai/v1/chat/completions",
            data=payload,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type":  "application/json",
            },
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=30) as r:
            result = json.loads(r.read().decode("utf-8"))
        return _clean(result["choices"][0]["message"]["content"].strip())

    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")[:200]
        return f"Groq API error {e.code}: {body}"
    except Exception as e:
        return f"Error: {_clean(str(e))}"

# ══════════════════════════════════════════════════════════════
#  CSS — dark premium theme + sidebar always open & readable
# ══════════════════════════════════════════════════════════════
st.markdown("""
<style>
/* ── Global ── */
html, body, [data-testid="stAppViewContainer"] {
    background:#050d1a !important; color:#e2e8f0 !important;
}
[data-testid="stHeader"]  { background:transparent !important; }
[data-testid="stToolbar"] { display:none; }

/* ── Sidebar shell ── */
[data-testid="stSidebar"] {
    background:linear-gradient(180deg,#0a1628 0%,#0d1f3c 100%) !important;
    border-right:1px solid #2563eb !important;
    min-width:260px !important;
}
/* Make every text node inside sidebar white */
[data-testid="stSidebar"],
[data-testid="stSidebar"] *,
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] div { color:#e2e8f0 !important; }

/* Sidebar collapse/expand toggle — bright blue so it's always visible */
[data-testid="collapsedControl"],
[data-testid="stSidebarCollapseButton"] > button,
[data-testid="stSidebarCollapsedControl"] > button {
    background:#1d4ed8 !important;
    border:2px solid #60a5fa !important;
    border-radius:50% !important;
    color:#fff !important;
    box-shadow:0 0 14px rgba(59,130,246,.7) !important;
}
[data-testid="collapsedControl"] svg,
[data-testid="stSidebarCollapseButton"] svg,
[data-testid="stSidebarCollapsedControl"] svg {
    fill:#ffffff !important; color:#ffffff !important;
}

/* Sidebar text input */
[data-testid="stSidebar"] input {
    background:#0f2744 !important; border:1px solid #3b82f6 !important;
    color:#ffffff !important; border-radius:8px !important;
}
[data-testid="stSidebar"] input::placeholder { color:#64748b !important; }

/* Sidebar radio */
[data-testid="stSidebar"] .stRadio label {
    background:#0f2744 !important; border:1px solid #3b82f6 !important;
    color:#93c5fd !important; border-radius:8px !important;
    padding:6px 12px !important; display:block !important;
    margin-bottom:4px !important; font-size:12px !important;
}
[data-testid="stSidebar"] .stRadio label:has(input:checked) {
    background:linear-gradient(135deg,#1d4ed8,#2563eb) !important;
    border-color:#60a5fa !important; color:#ffffff !important;
}

/* Sidebar download / file uploader buttons */
[data-testid="stSidebar"] [data-testid="stDownloadButton"] button,
[data-testid="stSidebar"] [data-testid="stDownloadButton"] button:hover,
[data-testid="stSidebar"] [data-testid="stBaseButton-secondary"] {
    background:linear-gradient(135deg,#1d4ed8,#2563eb) !important;
    border:1px solid #60a5fa !important; color:#ffffff !important;
    font-weight:700 !important; border-radius:8px !important;
    width:100% !important; box-shadow:0 2px 12px rgba(37,99,235,.5) !important;
}

/* Sidebar caption / small */
[data-testid="stSidebar"] .stCaption,
[data-testid="stSidebar"] small { color:#64a0d4 !important; }

/* HR */
[data-testid="stSidebar"] hr { border-color:#1e3a5f !important; }

/* ── Main metric cards ── */
[data-testid="metric-container"] {
    background:linear-gradient(135deg,#0f1e36,#0d2040) !important;
    border:1px solid #1e3a5f !important; border-radius:12px !important;
    padding:12px 16px !important;
}
[data-testid="metric-container"] label {
    color:#64a0d4 !important; font-size:11px !important;
    font-weight:700 !important; text-transform:uppercase; letter-spacing:.5px;
}
[data-testid="metric-container"] [data-testid="stMetricValue"] {
    color:#f0f9ff !important; font-size:24px !important; font-weight:900 !important;
}

/* ── Expander ── */
[data-testid="stExpander"] {
    background:#0a1628 !important; border:1px solid #1e3a5f !important;
    border-radius:10px !important;
}
[data-testid="stExpander"] summary { color:#93c5fd !important; font-weight:600; }

/* ── Main buttons ── */
.stButton > button {
    background:linear-gradient(135deg,#1d4ed8,#2563eb) !important;
    color:#fff !important; border:none !important; border-radius:10px !important;
    font-weight:700 !important; padding:10px 22px !important;
    box-shadow:0 4px 15px rgba(37,99,235,.4) !important; transition:all .2s !important;
}
.stButton > button:hover {
    box-shadow:0 6px 20px rgba(59,130,246,.6) !important;
    transform:translateY(-1px) !important;
}

/* ── Selectbox ── */
.stSelectbox > div > div {
    background:#0f2744 !important; border:1px solid #3b82f6 !important;
    color:#e2e8f0 !important; border-radius:8px !important;
}

/* ── File uploader ── */
[data-testid="stFileUploader"] {
    background:#0a1e3c !important; border:1px dashed #3b82f6 !important;
    border-radius:10px !important;
}

/* ── Hero banner ── */
.hero-banner {
    background:linear-gradient(135deg,#020e24,#0a1f40,#071830);
    border:1px solid #1e3a5f; border-radius:16px;
    padding:28px 32px; margin-bottom:24px; overflow:hidden; position:relative;
}
.hero-banner::before {
    content:''; position:absolute; top:-60px; right:-60px;
    width:220px; height:220px;
    background:radial-gradient(circle,rgba(59,130,246,.15),transparent 70%);
    border-radius:50%;
}
.hero-banner h1 {
    margin:0 0 6px; font-size:26px; font-weight:900;
    background:linear-gradient(90deg,#60a5fa,#a78bfa,#34d399);
    -webkit-background-clip:text; -webkit-text-fill-color:transparent;
}
.hero-banner p { margin:0; color:#64748b; font-size:13px; }
.hero-pills { display:flex; gap:8px; margin-top:12px; flex-wrap:wrap; }
.pill {
    background:rgba(59,130,246,.12); border:1px solid rgba(59,130,246,.3);
    border-radius:20px; padding:3px 12px; font-size:11px;
    color:#93c5fd; font-weight:600;
}

/* ── Module banner ── */
.module-banner {
    border-radius:14px; padding:18px 24px; margin-bottom:22px;
    position:relative; overflow:hidden;
}
.module-banner::after {
    content:''; position:absolute; inset:0;
    background:rgba(0,0,0,.35); border-radius:14px; pointer-events:none;
}
.module-banner-inner { position:relative; z-index:1; }
.module-banner h3  { margin:0 0 4px; font-size:18px; font-weight:800; color:#fff; }
.module-banner p   { margin:0; font-size:12px; color:rgba(255,255,255,.75); line-height:1.6; }
.problem-tag {
    display:inline-block; margin-top:8px;
    background:rgba(0,0,0,.35); border:1px solid rgba(255,255,255,.15);
    border-radius:20px; padding:3px 12px; font-size:11px; color:rgba(255,255,255,.8);
}

/* ── AI insight box ── */
.ai-box {
    background:linear-gradient(135deg,#07101f,#0c1a30,#091525);
    border:1px solid #1e4070; border-radius:14px;
    padding:20px 24px; margin-top:18px;
    box-shadow:0 8px 32px rgba(0,0,0,.5);
}
.ai-badge {
    display:inline-block; background:linear-gradient(135deg,#4f46e5,#7c3aed);
    border-radius:6px; padding:3px 10px; font-size:10px; font-weight:800;
    color:#fff; letter-spacing:1px; text-transform:uppercase; margin-bottom:10px;
}
.ai-model { font-size:11px; color:#475569; margin-left:8px; }
.ai-hr { border:none; border-top:1px solid #1e3a5f; margin:10px 0 14px; }
.ai-text {
    color:#cbd5e1; font-size:13.5px; line-height:1.85;
    white-space:pre-wrap;
}
.ai-text strong { color:#93c5fd; font-weight:700; }

/* ── Section headers ── */
.sh {
    display:flex; align-items:center; gap:10px;
    margin:20px 0 12px; padding-bottom:8px; border-bottom:1px solid #1e3a5f;
}
.sh span { font-size:13px; font-weight:700; color:#93c5fd;
           text-transform:uppercase; letter-spacing:.5px; }

/* ── Alert boxes ── */
.alert-r { background:#1a0a0a; border-left:4px solid #ef4444;
           border-radius:8px; padding:10px 14px; color:#fca5a5;
           font-size:12px; margin-bottom:10px; }
.alert-y { background:#1a140a; border-left:4px solid #f59e0b;
           border-radius:8px; padding:10px 14px; color:#fcd34d;
           font-size:12px; margin-bottom:10px; }
.alert-b { background:#0a1a2e; border-left:4px solid #3b82f6;
           border-radius:8px; padding:10px 14px; color:#93c5fd;
           font-size:12px; margin-bottom:10px; }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
#  PLOTLY DARK THEME
# ══════════════════════════════════════════════════════════════
_DB = dict(
    paper_bgcolor="#0a1628", plot_bgcolor="#0a1628",
    font=dict(color="#94a3b8", family="Inter,sans-serif"),
    title_font=dict(color="#e2e8f0", size=14),
    margin=dict(t=48,b=28,l=16,r=16),
    xaxis=dict(gridcolor="#0f2240",linecolor="#1e3a5f",
               tickfont=dict(color="#64748b"),zerolinecolor="#1e3a5f"),
    yaxis=dict(gridcolor="#0f2240",linecolor="#1e3a5f",
               tickfont=dict(color="#64748b"),zerolinecolor="#1e3a5f"),
)
_LEG = dict(bgcolor="rgba(10,22,40,.8)",bordercolor="#1e3a5f",
            borderwidth=1,font=dict(color="#94a3b8",size=11),
            orientation="h",y=-0.22)

def dark(fig, h=380, leg=True, **kw):
    lay = {**_DB, "height":h, **kw}
    if leg is True:   lay["legend"] = _LEG
    elif isinstance(leg,dict): lay["legend"] = {**_LEG,**leg}
    fig.update_layout(**lay)
    return fig

def pc(fig): st.plotly_chart(fig, width="stretch")

def hex_rgba(hx, a=0.18):
    h=hx.lstrip("#")
    return f"rgba({int(h[0:2],16)},{int(h[2:4],16)},{int(h[4:6],16)},{a})"

PAL = ["#6366f1","#10b981","#f59e0b","#ec4899","#38bdf8",
       "#8b5cf6","#fb923c","#84cc16","#06b6d4","#f43f5e"]

# ══════════════════════════════════════════════════════════════
#  DEMO DATA
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

META = {
    "forecast":  {"icon":"📈","title":"Demand Forecast Engine",  "color":"#6366f1",
                  "grad":"linear-gradient(135deg,#312e81,#1e1b4b)",
                  "problem":"Analysts manually tweak spreadsheets - 30% forecast errors - overstock or stockouts bleed cash every quarter."},
    "inventory": {"icon":"📦","title":"Inventory Health Monitor","color":"#10b981",
                  "grad":"linear-gradient(135deg,#064e3b,#065f46)",
                  "problem":"No dynamic EOQ/safety-stock model - working capital locked in dead stock OR stockouts tank fill rate."},
    "supplier":  {"icon":"🏭","title":"Supplier Risk Radar",     "color":"#f59e0b",
                  "grad":"linear-gradient(135deg,#78350f,#92400e)",
                  "problem":"Single-source concentration + zero early-warning scores - one supplier failure cascades into a production shutdown."},
    "sop":       {"icon":"🔄","title":"S&OP Alignment Monitor",  "color":"#ec4899",
                  "grad":"linear-gradient(135deg,#831843,#9d174d)",
                  "problem":"Sales, Demand Planning, Production and Procurement run different numbers - wrong product, wrong time, wrong place."},
    "kpi":       {"icon":"📊","title":"KPI Command Center",      "color":"#38bdf8",
                  "grad":"linear-gradient(135deg,#0c4a6e,#075985)",
                  "problem":"OTIF, fill rates, lead times tracked in 10 spreadsheets by 10 people - leadership decides on stale conflicting data."},
}

# ══════════════════════════════════════════════════════════════
#  SHARED HELPERS
# ══════════════════════════════════════════════════════════════
def get_df(k):   return st.session_state.get(f"up_{k}", DEMO[k]).copy()
def is_demo(k):  return f"up_{k}" not in st.session_state

def read_upload(f):
    if f is None: return None
    try:
        return pd.read_csv(f) if f.name.lower().endswith(".csv") else pd.read_excel(f)
    except Exception as e:
        st.error(f"Upload error: {e}")
    return None

def banner(k):
    m=META[k]
    st.markdown(
        f'<div class="module-banner" style="background:{m["grad"]};'
        f'border:1px solid {m["color"]}40">'
        f'<div class="module-banner-inner"><h3>{m["icon"]} {m["title"]}</h3>'
        f'<p>Problem: {m["problem"]}</p>'
        f'<span class="problem-tag">One of 5 core problems solved here</span>'
        f'</div></div>', unsafe_allow_html=True)

def sh(icon,label):
    st.markdown(f'<div class="sh"><span style="font-size:16px">{icon}</span>'
                f'<span>{label}</span></div>', unsafe_allow_html=True)

def ai_box(text):
    text = re.sub(r'\*\*(.+?)\*\*','<strong>\\1</strong>', text)
    st.markdown(
        f'<div class="ai-box">'
        f'<span class="ai-badge">AI Insight</span>'
        f'<span class="ai-model">llama-3.3-70b-versatile via Groq</span>'
        f'<hr class="ai-hr">'
        f'<div class="ai-text">{text}</div>'
        f'</div>', unsafe_allow_html=True)

def alrt(kind,msg):
    cls={"r":"alert-r","y":"alert-y","b":"alert-b"}[kind]
    st.markdown(f'<div class="{cls}">{msg}</div>', unsafe_allow_html=True)

def data_panel(k):
    st.sidebar.markdown("---")
    st.sidebar.markdown("**📂 Data Source**")
    mode = st.sidebar.radio("Data source",["Demo Dataset","Upload My Data"],
                             key=f"r_{k}", label_visibility="collapsed")
    if mode == "Upload My Data":
        st.sidebar.caption(f"Columns: `{SCHEMAS[k]}`")
        f = st.sidebar.file_uploader("CSV or Excel",type=["csv","xlsx","xls"],key=f"f_{k}")
        df = read_upload(f)
        if df is not None:
            st.session_state[f"up_{k}"] = df
            st.sidebar.success(f"Loaded {len(df)} rows")
        elif f"up_{k}" in st.session_state:
            del st.session_state[f"up_{k}"]
    else:
        st.session_state.pop(f"up_{k}", None)
    st.sidebar.download_button("⬇ Download CSV Template",
        data=DEMO[k].to_csv(index=False).encode(),
        file_name=f"template_{k}.csv", mime="text/csv", key=f"dl_{k}")

# ══════════════════════════════════════════════════════════════
#  MODULE 1 — DEMAND FORECAST
# ══════════════════════════════════════════════════════════════
def mod_forecast(api_key):
    banner("forecast")
    df = get_df("forecast")
    with st.expander(f"Raw Dataset ({'Demo' if is_demo('forecast') else 'Uploaded'})", False):
        st.dataframe(df, width="stretch")

    act   = df[df["actual_demand"].notna()]["actual_demand"].astype(float).tolist()
    months= df["month"].tolist()
    n     = len(act)
    alpha = 0.35
    ema   = [act[0]]
    for v in act[1:]: ema.append(alpha*v+(1-alpha)*ema[-1])
    x = np.arange(n)
    sl,ic = np.polyfit(x,act,1) if n>1 else (0,act[0])
    fcast = [max(0,round(ic+sl*i+np.random.uniform(-.04,.04)*(ic+sl*i)))
             for i in range(n,len(months))]
    mape  = np.mean([abs(a-e)/a*100 for a,e in zip(act[-3:],ema[-3:])]) if n>=3 else 0
    acc   = round(max(0,100-mape),1)
    vol   = round(np.std(act)/np.mean(act)*100,1)
    promo = [months[i] for i,v in enumerate(df.get("promo_flag",[0]*n).tolist())
             if v==1 and i<n]

    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Avg Monthly Demand", f"{int(np.mean(act)):,} u")
    c2.metric("EMA Accuracy",       f"{acc}%", f"{acc-90:.1f}% vs 90% target")
    c3.metric("Demand Volatility",  f"+-{vol}%","High" if vol>15 else "Moderate")
    c4.metric("Projected Next Qtr", f"{int(np.mean(fcast[:3])):,} u/mo" if fcast else "N/A")

    sh("📊","Demand Timeline")
    fig=go.Figure()
    fig.add_trace(go.Bar(x=months[:n],y=act,name="Actual",
        marker=dict(color=act,colorscale=[[0,"#312e81"],[.5,"#6366f1"],[1,"#a5b4fc"]],
                    showscale=False,line=dict(width=0))))
    fig.add_trace(go.Scatter(x=months[:n],y=[round(v) for v in ema],
        name="EMA",mode="lines+markers",
        line=dict(color="#f59e0b",width=2.5,dash="dot"),marker=dict(size=6,color="#f59e0b")))
    if fcast:
        fig.add_trace(go.Bar(x=months[n:],y=fcast,name="Forecast",
            marker=dict(color="#1e3a8a",line=dict(color="#6366f1",width=1.5))))
    for pm in promo:
        fig.add_vline(x=months.index(pm),line_dash="dash",line_color="#ec4899",
                      line_width=1,annotation_text="Promo",annotation_position="top")
    pc(dark(fig,h=370,barmode="overlay",leg=dict(y=-0.18)))

    sh("📉","MoM Growth Rate")
    mom=[round((act[i]-act[i-1])/act[i-1]*100,1) if i>0 else 0 for i in range(n)]
    fig2=go.Figure(go.Bar(x=months[:n],y=mom,
        marker_color=["#10b981" if v>=0 else "#ef4444" for v in mom],
        text=[f"{v:+.1f}%" for v in mom],textposition="outside",textfont=dict(color="#e2e8f0")))
    fig2.add_hline(y=0,line_color="#334155",line_width=1)
    pc(dark(fig2,h=220,leg=False,title="Month-on-Month Growth %",margin=dict(t=36,b=16,l=8,r=8)))

    if promo: alrt("b",f"<b>Promo months:</b> {', '.join(promo)} -- factored into projection")

    sh("🤖","AI Demand Analysis")
    if st.button("Run AI Forecast Analysis", key="btn_f"):
        with st.spinner("Analyzing with Groq..."):
            ai_box(groq_insight(api_key,
                "You are a senior supply chain demand planning analyst. Be specific with numbers. Use **bold** for key findings.",
                f"Historical demand by month: {_safe_str(dict(zip(months[:n],act)))}\n"
                f"EMA projection: {_safe_str(dict(zip(months[n:],fcast)))}\n"
                f"Forecast accuracy: {acc}% (target 90%)\n"
                f"Demand volatility: +-{vol}%\n"
                f"Promo months: {_safe_str(promo)}\n\n"
                "Provide:\n"
                "1. Trend direction and monthly growth rate\n"
                "2. Seasonality patterns and peak risk months\n"
                "3. Root cause of the accuracy gap\n"
                "4. Top 3 actions to improve accuracy\n"
                "5. Recommended safety stock buffer % for this volatility\n"
                "6. Stockout or overstock risk next quarter with $ estimate"
            ))

# ══════════════════════════════════════════════════════════════
#  MODULE 2 — INVENTORY HEALTH
# ══════════════════════════════════════════════════════════════
def mod_inventory(api_key):
    banner("inventory")
    df=get_df("inventory")
    df["days_of_supply"]=(df["stock"]/df["daily_demand"]).round(1)
    df["working_capital"]=(df["stock"]*df["unit_cost"]).round(2)
    df["excess_units"]=(df["stock"]-df["eoq"]-df["safety_stock"]).clip(lower=0)
    df["locked_capital"]=(df["excess_units"]*df["unit_cost"]).round(2)
    def clf(r):
        if r.stock < r.safety_stock:               return "Critical"
        if r.days_of_supply < r.lead_time_days:    return "Stockout Risk"
        if r.stock > 2*r.eoq+r.safety_stock:       return "Overstock"
        return "Healthy"
    df["status"]=df.apply(clf,axis=1)

    with st.expander(f"Raw Dataset ({'Demo' if is_demo('inventory') else 'Uploaded'})",False):
        st.dataframe(df,width="stretch")

    crit=df[df.status.isin(["Critical","Stockout Risk"])]
    over=df[df.status=="Overstock"]
    locked=over.locked_capital.sum(); twc=df.working_capital.sum()

    c1,c2,c3,c4=st.columns(4)
    c1.metric("SKUs at Risk",len(crit),f"{len(crit)} need action now")
    c2.metric("Overstock SKUs",len(over))
    c3.metric("Capital Locked",f"${locked:,.0f}","above EOQ+SS")
    c4.metric("Total Inv. Value",f"${twc:,.0f}")
    if not crit.empty:
        alrt("r","<b>Immediate Action:</b> "+
             " | ".join([f"<b>{r.sku}</b> {r.days_of_supply}d supply, LT {r.lead_time_days}d"
                         for _,r in crit.iterrows()]))

    sh("📦","Stock Levels vs Thresholds")
    nm=df.item_name.tolist()
    fig=go.Figure()
    fig.add_trace(go.Bar(x=nm,y=df.stock,        name="Stock",        marker_color="#6366f1"))
    fig.add_trace(go.Bar(x=nm,y=df.reorder_point,name="Reorder Point",marker_color="#f59e0b"))
    fig.add_trace(go.Bar(x=nm,y=df.safety_stock, name="Safety Stock", marker_color="#ef4444"))
    fig.add_trace(go.Scatter(x=nm,y=df.eoq,name="EOQ",mode="markers+lines",
        marker=dict(size=10,color="#10b981",symbol="diamond"),
        line=dict(dash="dot",color="#10b981",width=2)))
    pc(dark(fig,h=340,barmode="group"))

    sh("💰","Capital & Days of Supply")
    ca,cb=st.columns(2)
    with ca:
        f2=go.Figure(go.Pie(labels=df.item_name,values=df.working_capital,hole=0.52,
            marker=dict(colors=PAL[:len(df)],line=dict(color="#0a1628",width=2)),
            textinfo="label+percent",textfont=dict(color="#e2e8f0",size=11)))
        pc(dark(f2,h=280,leg=False,title="Working Capital by SKU",margin=dict(t=36,b=0,l=0,r=0)))
    with cb:
        dos=df.days_of_supply.tolist()
        f3=go.Figure(go.Bar(x=df.item_name,y=dos,
            marker_color=["#ef4444" if d<5 else "#f59e0b" if d<14 else "#10b981" for d in dos],
            text=[f"{d}d" for d in dos],textposition="outside",textfont=dict(color="#e2e8f0")))
        f3.add_hline(y=14,line_dash="dot",line_color="#f59e0b",
                     annotation_text="14d min",annotation_font_color="#f59e0b")
        pc(dark(f3,h=280,leg=False,title="Days of Supply",margin=dict(t=36,b=16,l=8,r=8)))

    sh("🤖","AI Inventory Analysis")
    if st.button("Run AI Inventory Analysis",key="btn_inv"):
        with st.spinner("Analyzing with Groq..."):
            rows=df[["sku","item_name","stock","reorder_point","eoq","safety_stock",
                      "daily_demand","lead_time_days","days_of_supply",
                      "status","working_capital","locked_capital"]].to_dict("records")
            ai_box(groq_insight(api_key,
                "You are a senior inventory optimization analyst. Be specific with numbers. Use **bold** for key findings.",
                f"Inventory data: {_safe_str(rows)}\n"
                f"Total working capital: ${twc:,.0f}\n"
                f"Locked in overstock: ${locked:,.0f}\n\n"
                "Provide:\n"
                "1. Top 2 SKUs needing immediate PO or production stop\n"
                "2. Exact order quantity per critical SKU\n"
                "3. Overstock reduction plan with timeline\n"
                "4. Working capital freed if right-sized to EOQ+SS\n"
                "5. Safety stock formula recommendation for these lead times\n"
                "6. One systemic fix to prevent recurrence"
            ))

# ══════════════════════════════════════════════════════════════
#  MODULE 3 — SUPPLIER RISK
# ══════════════════════════════════════════════════════════════
def mod_supplier(api_key):
    banner("supplier")
    df=get_df("supplier")
    df["composite_score"]=(df.delivery_pct*.40+df.quality_pct*.35+df.cost_score*.25).round(1)
    df["risk_tier"]=df.composite_score.apply(
        lambda s:"Low" if s>=85 else("Medium" if s>=70 else("High" if s>=55 else "Critical")))
    df["spend_share"]=(df.annual_spend/df.annual_spend.sum()*100).round(1)
    RC={"Low":"#10b981","Medium":"#f59e0b","High":"#ef4444","Critical":"#dc2626"}
    tot=df.annual_spend.sum()
    ar =df[df.risk_tier.isin(["High","Critical"])].annual_spend.sum()
    ss =df[df.single_source==1].annual_spend.sum() if "single_source" in df.columns else 0

    with st.expander(f"Raw Dataset ({'Demo' if is_demo('supplier') else 'Uploaded'})",False):
        st.dataframe(df,width="stretch")

    c1,c2,c3,c4=st.columns(4)
    c1.metric("Total Spend",     f"${tot:,.0f}")
    c2.metric("At-Risk Spend",   f"${ar:,.0f}", f"{ar/tot*100:.0f}% of portfolio")
    c3.metric("Single-Src Spend",f"${ss:,.0f}", "Concentration risk")
    c4.metric("Avg Score",       f"{df.composite_score.mean():.1f}")
    hr=df[df.risk_tier.isin(["High","Critical"])]
    if not hr.empty:
        alrt("r","<b>High/Critical:</b> "+
             " | ".join([f"<b>{r.supplier_name}</b> score {r.composite_score}" for _,r in hr.iterrows()]))

    sh("📊","Supplier Scorecard")
    fig=go.Figure()
    fig.add_trace(go.Bar(x=df.supplier_name,y=df.delivery_pct,name="Delivery %", marker_color="#6366f1"))
    fig.add_trace(go.Bar(x=df.supplier_name,y=df.quality_pct, name="Quality %",  marker_color="#10b981"))
    fig.add_trace(go.Bar(x=df.supplier_name,y=df.cost_score,  name="Cost Score", marker_color="#f59e0b"))
    fig.add_trace(go.Scatter(x=df.supplier_name,y=df.composite_score,
        name="Composite",mode="lines+markers",line=dict(color="#ec4899",width=3),
        marker=dict(size=12,color=[RC.get(r,"#64748b") for r in df.risk_tier],
                    symbol="diamond",line=dict(color="#fff",width=1.5))))
    fig.add_hline(y=70,line_dash="dot",line_color="#ef4444",
                  annotation_text="Risk (70)",annotation_font_color="#ef4444")
    fig.add_hline(y=85,line_dash="dot",line_color="#10b981",
                  annotation_text="Healthy (85)",annotation_font_color="#10b981")
    pc(dark(fig,h=340,barmode="group"))

    sh("🔵","Risk vs Spend")
    ca,cb=st.columns([3,2])
    with ca:
        f2=go.Figure()
        for _,row in df.iterrows():
            clr=RC.get(row.risk_tier,"#64748b")
            f2.add_trace(go.Scatter(x=[row.composite_score],y=[row.annual_spend],
                mode="markers+text",text=[row.supplier_name],textposition="top center",
                textfont=dict(color="#e2e8f0",size=10),
                marker=dict(size=row.lead_time_days*3.5,color=clr,opacity=.75,
                            line=dict(color=clr,width=2)),name=row.supplier_name))
        f2.add_vline(x=70,line_dash="dot",line_color="#ef4444")
        pc(dark(f2,h=320,leg=False,title="Score vs Spend (bubble=lead time)",
                xaxis=dict(**_DB["xaxis"],title="Score"),
                yaxis=dict(**_DB["yaxis"],title="Spend ($)")))
    with cb:
        f3=go.Figure(go.Pie(labels=df.supplier_name,values=df.annual_spend,hole=0.55,
            marker=dict(colors=[RC.get(r,"#64748b") for r in df.risk_tier],
                        line=dict(color="#0a1628",width=2)),
            textinfo="percent",textfont=dict(color="#e2e8f0",size=10)))
        pc(dark(f3,h=320,title="Spend Share",margin=dict(t=36,b=0,l=0,r=0)))

    sh("📡","Supplier Radar")
    sel=st.selectbox("Select supplier",df.supplier_name.tolist(),key="sup_sel")
    row=df[df.supplier_name==sel].iloc[0]
    cats=["Delivery %","Quality %","Cost Score","Lead Time Inv.","Composite"]
    vals=[row.delivery_pct,row.quality_pct,row.cost_score,
          max(0,100-(row.lead_time_days/30)*100),row.composite_score]
    clr=RC.get(row.risk_tier,"#6366f1")
    f4=go.Figure()
    f4.add_trace(go.Scatterpolar(r=vals+[vals[0]],theta=cats+[cats[0]],
        fill="toself",fillcolor=hex_rgba(clr),
        line=dict(color=clr,width=2.5),marker=dict(size=7,color=clr),name=sel))
    f4.add_trace(go.Scatterpolar(r=[85]*len(cats)+[85],theta=cats+[cats[0]],
        line=dict(color="#334155",dash="dot",width=1),fill=None,name="Healthy"))
    f4.update_layout(
        polar=dict(bgcolor="#0a1628",
                   radialaxis=dict(visible=True,range=[0,100],gridcolor="#1e3a5f",
                                   tickfont=dict(color="#64748b",size=9)),
                   angularaxis=dict(gridcolor="#1e3a5f",tickfont=dict(color="#94a3b8",size=11))),
        paper_bgcolor="#0a1628",height=300,
        legend=dict(bgcolor="#0a1628",bordercolor="#1e3a5f",font=dict(color="#94a3b8")),
        margin=dict(t=20,b=20,l=40,r=40))
    pc(f4)

    sh("🤖","AI Supplier Risk Assessment")
    if st.button("Run AI Supplier Analysis",key="btn_sup"):
        with st.spinner("Analyzing with Groq..."):
            rows=df[["supplier_name","delivery_pct","quality_pct","cost_score",
                      "lead_time_days","annual_spend","composite_score",
                      "risk_tier","spend_share"]].to_dict("records")
            ss_names=df[df.single_source==1].supplier_name.tolist() \
                     if "single_source" in df.columns else []
            ai_box(groq_insight(api_key,
                "You are a procurement and supplier risk expert. Be specific with numbers. Use **bold** for key findings.",
                f"Supplier portfolio: {_safe_str(rows)}\n"
                f"Single-source suppliers: {_safe_str(ss_names)}\n"
                f"Total spend: ${tot:,.0f} | At-risk: ${ar:,.0f}\n\n"
                "Provide:\n"
                "1. Top 2 risks with exact $ exposure if supplier fails\n"
                "2. Which supplier needs a 30-day PIP with KPI targets\n"
                "3. Dual-sourcing priorities\n"
                "4. Negotiation leverage -- who we overpay vs their risk score\n"
                "5. 30-day quick win to reduce portfolio risk\n"
                "6. One weekly early-warning metric to track"
            ))

# ══════════════════════════════════════════════════════════════
#  MODULE 4 — S&OP ALIGNMENT
# ══════════════════════════════════════════════════════════════
def mod_sop(api_key):
    banner("sop")
    df=get_df("sop")
    qs=["q1","q2","q3","q4"]; ql={"q1":"Q1","q2":"Q2","q3":"Q3","q4":"Q4"}

    with st.expander(f"Raw Dataset ({'Demo' if is_demo('sop') else 'Uploaded'})",False):
        st.dataframe(df,width="stretch")

    gd=[]
    for q in qs:
        v=df[q].astype(float).tolist()
        gd.append({"quarter":ql[q],"max":max(v),"min":min(v),
                   "gap":max(v)-min(v),"gap_pct":(max(v)-min(v))/max(v)*100})
    gdf=pd.DataFrame(gd); wq=gdf.loc[gdf.gap_pct.idxmax()]; avg=gdf.gap_pct.mean()

    c1,c2,c3,c4=st.columns(4)
    c1.metric("Worst Quarter",    wq.quarter)
    c2.metric("Max Gap",          f"{int(wq.gap):,} units",  f"{wq.gap_pct:.1f}% misalignment")
    c3.metric("Avg Cross-Dept Gap",f"{avg:.1f}%",            "Target <5%")
    c4.metric("Revenue at Risk*", f"${int(wq.gap*45):,}",   "*@$45 ASP")
    if avg>10: alrt("r",f"<b>Critical misalignment:</b> {avg:.1f}% avg gap -- revenue leakage HIGH")
    elif avg>5: alrt("y",f"<b>Moderate misalignment:</b> {avg:.1f}% avg gap -- sync needed")

    sh("📊","Department Signals by Quarter")
    DC={"Sales":"#6366f1","Demand Plan":"#10b981","Production Capacity":"#f59e0b","Procurement":"#ec4899"}
    fig=go.Figure()
    for _,row in df.iterrows():
        fig.add_trace(go.Bar(name=row.department,x=[ql[q] for q in qs],
            y=[row[q] for q in qs],marker_color=DC.get(row.department,"#64748b")))
    pc(dark(fig,h=340,barmode="group"))

    sh("🌡","Misalignment Heatmap")
    ca,cb=st.columns(2)
    with ca:
        f2=go.Figure(go.Bar(x=gdf.quarter,y=gdf.gap,
            marker=dict(color=gdf.gap_pct,
                        colorscale=[[0,"#064e3b"],[.4,"#f59e0b"],[.7,"#ef4444"],[1,"#dc2626"]],
                        showscale=True,
                        colorbar=dict(title=dict(text="Gap %",font=dict(color="#94a3b8")),
                                      tickfont=dict(color="#94a3b8")),
                        line=dict(width=0)),
            text=gdf.gap_pct.apply(lambda v:f"{v:.1f}%"),
            textposition="outside",textfont=dict(color="#e2e8f0")))
        pc(dark(f2,h=280,leg=False,title="Unit Gap by Quarter",margin=dict(t=36,b=16,l=8,r=8)))
    with cb:
        hr2=[]
        for _,row in df.iterrows():
            r2={"Dept":row.department}
            for q in qs: r2[ql[q]]=round((df[q].max()-row[q])/df[q].max()*100,1)
            hr2.append(r2)
        hdf=pd.DataFrame(hr2).set_index("Dept")
        f3=go.Figure(go.Heatmap(z=hdf.values,x=hdf.columns.tolist(),y=hdf.index.tolist(),
            colorscale=[[0,"#064e3b"],[.4,"#f59e0b"],[.7,"#ef4444"],[1,"#7f1d1d"]],
            texttemplate="%{z:.1f}%",textfont=dict(size=11,color="#fff"),zmin=0,zmax=20))
        pc(dark(f3,h=280,leg=False,title="Shortfall % vs Max Signal",margin=dict(t=36,b=16,l=90,r=16)))

    sh("🤖","AI S&OP Analysis")
    if st.button("Run AI S&OP Analysis",key="btn_sop"):
        with st.spinner("Analyzing with Groq..."):
            ai_box(groq_insight(api_key,
                "You are a senior S&OP expert. Be precise with numbers. Use **bold** for key findings.",
                f"Department signals (units): {_safe_str(df.to_dict('records'))}\n"
                f"Gap analysis: {_safe_str(gdf.to_dict('records'))}\n"
                f"ASP=$45/unit | Avg gap: {avg:.1f}%\n\n"
                "Provide:\n"
                "1. Most dangerous quarter with specific dept shortfall\n"
                "2. Revenue at risk from demand > production (use ASP $45)\n"
                "3. Cost from procurement over-ordering vs demand\n"
                "4. Most reliable department signal and why\n"
                "5. Top 3 S&OP meeting action items\n"
                "6. One change to get misalignment below 5%"
            ))

# ══════════════════════════════════════════════════════════════
#  MODULE 5 — KPI DASHBOARD
# ══════════════════════════════════════════════════════════════
def mod_kpi(api_key):
    banner("kpi")
    df=get_df("kpi")
    df["pct"]=(df.current_value/df.target_value*100).round(1)
    df["gap"]=(df.target_value-df.current_value).round(2)

    with st.expander(f"Raw Dataset ({'Demo' if is_demo('kpi') else 'Uploaded'})",False):
        st.dataframe(df,width="stretch")

    cols=st.columns(len(df))
    for i,(_,row) in enumerate(df.iterrows()):
        nl=row.kpi_name=="Avg Lead Time"
        good=(row.trend<0) if nl else (row.trend>0)
        sym="+" if row.trend>0 else "-"
        cols[i].metric(row.kpi_name,f"{row.current_value}{row.unit}",
                       f"{sym}{abs(row.trend)}{row.unit}",
                       delta_color="normal" if good else "inverse")

    sh("🎯","Performance Gauges")
    gc=st.columns(3)
    for i,(_,row) in enumerate(df.iterrows()):
        pct=row.pct
        clr="#10b981" if pct>=100 else("#f59e0b" if pct>=85 else "#ef4444")
        fig=go.Figure(go.Indicator(
            mode="gauge+number+delta",value=row.current_value,
            title={"text":row.kpi_name,"font":{"size":12,"color":"#94a3b8"}},
            delta={"reference":row.target_value,"suffix":row.unit,
                   "increasing":{"color":"#10b981"},"decreasing":{"color":"#ef4444"}},
            number={"suffix":row.unit,"font":{"color":"#e2e8f0","size":22}},
            gauge={"axis":{"range":[0,row.target_value*1.25],
                           "tickfont":{"color":"#64748b","size":9}},
                   "bar":{"color":clr,"thickness":.28},
                   "bgcolor":"#0a1628","bordercolor":"#1e3a5f",
                   "threshold":{"line":{"color":"#fff","width":3},
                                "thickness":.75,"value":row.target_value},
                   "steps":[{"range":[0,row.target_value*.7],"color":"#1a0a0a"},
                             {"range":[row.target_value*.7,row.target_value*.9],"color":"#1a140a"},
                             {"range":[row.target_value*.9,row.target_value*1.25],"color":"#061a10"}]}))
        fig.update_layout(paper_bgcolor="#0a1628",height=200,margin=dict(t=44,b=8,l=16,r=16))
        gc[i%3].plotly_chart(fig,width="stretch")

    sh("📊","KPI vs Target")
    ca,cb=st.columns(2)
    with ca:
        bc=["#10b981" if p>=100 else"#f59e0b" if p>=85 else"#ef4444" for p in df.pct]
        f2=go.Figure(go.Bar(x=df.pct,y=df.kpi_name,orientation="h",marker_color=bc,
            text=df.pct.apply(lambda v:f"{v:.1f}%"),textposition="outside",
            textfont=dict(color="#e2e8f0")))
        f2.add_vline(x=100,line_dash="dot",line_color="#334155")
        f2.add_vline(x=85, line_dash="dash",line_color="#f59e0b",line_width=1)
        pc(dark(f2,h=280,leg=False,title="% of Target",margin=dict(t=36,b=16,l=8,r=60)))
    with cb:
        f3=go.Figure(go.Heatmap(z=[df.pct.tolist()],x=df.kpi_name.tolist(),
            y=["Performance"],
            colorscale=[[0,"#7f1d1d"],[.5,"#78350f"],[.75,"#064e3b"],[1,"#10b981"]],
            zmin=50,zmax=110,texttemplate="%{z:.1f}%",textfont=dict(size=11,color="#fff")))
        pc(dark(f3,h=280,leg=False,title="Heatmap",margin=dict(t=36,b=16,l=16,r=16)))

    sh("📈","KPI Trends")
    f4=go.Figure()
    for _,row in df.iterrows():
        nl=row.kpi_name=="Avg Lead Time"
        clr="#10b981" if ((row.trend<=0) if nl else (row.trend>=0)) else "#ef4444"
        f4.add_trace(go.Scatter(
            x=["3mo ago","2mo ago","1mo ago","Now"],
            y=[row.current_value-row.trend*3,row.current_value-row.trend*2,
               row.current_value-row.trend,row.current_value],
            name=row.kpi_name,mode="lines+markers",
            line=dict(color=clr,width=2),marker=dict(size=6,color=clr)))
    pc(dark(f4,h=260,leg=dict(y=-0.32,font=dict(size=10))))

    sh("🤖","AI Executive KPI Brief")
    if st.button("Generate AI KPI Brief",key="btn_kpi"):
        with st.spinner("Analyzing with Groq..."):
            rows=df[["kpi_name","current_value","target_value","unit",
                      "trend","pct","gap"]].to_dict("records")
            off=df[df.pct<100].kpi_name.tolist()
            ai_box(groq_insight(api_key,
                "You are a supply chain VP. Be direct and data-driven. Use **bold** for key findings.",
                f"KPI data: {_safe_str(rows)}\n"
                f"Off-target KPIs ({len(off)} of {len(df)}): {_safe_str(off)}\n"
                f"Monthly revenue base: $10M\n\n"
                "Provide:\n"
                "1. Top 3 KPIs bleeding most value with $ impact per unit of gap\n"
                "2. Causal chain -- root causes vs symptoms\n"
                "3. Root cause for worst performer\n"
                "4. 30/60/90-day action plan (one action each)\n"
                "5. One untracked metric that would explain these gaps\n"
                "6. What leadership needs to approve resources"
            ))

# ══════════════════════════════════════════════════════════════
#  MAIN
# ══════════════════════════════════════════════════════════════
def main():
    # ── Sidebar ──
    st.sidebar.markdown("""
    <div style="text-align:center;padding:16px 0 8px">
        <div style="font-size:36px">⛓</div>
        <div style="font-size:15px;font-weight:900;
                    background:linear-gradient(90deg,#60a5fa,#a78bfa);
                    -webkit-background-clip:text;-webkit-text-fill-color:transparent">
            Supply Chain<br>Command Center
        </div>
        <div style="font-size:10px;color:#475569;margin-top:4px">
            5 Problems · 1 Platform · Groq AI
        </div>
    </div>""", unsafe_allow_html=True)
    st.sidebar.markdown("---")

    st.sidebar.markdown("**🔑 Groq API Key**")
    api_key = st.sidebar.text_input("Groq API Key", type="password",
                                     placeholder="gsk_...",
                                     label_visibility="collapsed",
                                     help="Free at console.groq.com")
    if api_key:
        st.sidebar.markdown('<p style="color:#86efac;font-size:12px">✅ Key active</p>',
                            unsafe_allow_html=True)
    else:
        st.sidebar.markdown('<p style="color:#fcd34d;font-size:12px">⚠️ Add key for AI insights</p>',
                            unsafe_allow_html=True)
    st.sidebar.markdown("---")

    st.sidebar.markdown("**🧭 Module**")
    labels={f"{META[k]['icon']} {META[k]['title']}":k for k in META}
    sel=st.sidebar.radio("Select Module",list(labels.keys()),
                          label_visibility="collapsed")
    active=labels[sel]
    data_panel(active)

    st.sidebar.markdown("---")
    st.sidebar.markdown(
        '<div style="font-size:10px;color:#334155;line-height:1.8">'
        'Model: llama-3.3-70b-versatile<br>Provider: Groq<br>'
        'Solving 5 supply chain resource problems'
        '</div>', unsafe_allow_html=True)

    # ── Hero ──
    st.markdown("""
    <div class="hero-banner">
        <h1>Supply Chain Command Center</h1>
        <p>One platform · 5 root problems eliminated · AI-powered by Groq · No more spreadsheet juggling</p>
        <div class="hero-pills">
            <span class="pill">📈 Demand Forecast</span>
            <span class="pill">📦 Inventory Health</span>
            <span class="pill">🏭 Supplier Risk</span>
            <span class="pill">🔄 S&OP Alignment</span>
            <span class="pill">📊 KPI Dashboard</span>
        </div>
    </div>""", unsafe_allow_html=True)

    # ── Route ──
    {"forecast":mod_forecast,"inventory":mod_inventory,
     "supplier":mod_supplier,"sop":mod_sop,"kpi":mod_kpi}[active](api_key)


if __name__ == "__main__":
    main()
