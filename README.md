# ⛓ Supply Chain Command Center

> **One platform. 5 root problems eliminated. AI-powered by Groq.**  
> Built for supply chain analysts who are tired of juggling 10 spreadsheets, 4 tools, and stale data.

---

## 🔥 Why This Exists

After scraping and analyzing 100+ Supply Chain Analyst job descriptions, five problems kept showing up across every company, every industry — problems that waste capital, kill margins, and burn analyst hours daily:

| # | Problem | Real-World Cost |
|---|---|---|
| 1 | **Demand Forecast Failure** — manual Excel forecasting with ±30% error rates | Overstock ties up working capital · Stockouts kill revenue |
| 2 | **Inventory Imbalance** — no dynamic EOQ or safety-stock model | Cash locked in dead stock OR orders missed due to stockouts |
| 3 | **Supplier Risk Blindness** — single-source dependency, no early-warning scoring | One delay cascades into full production shutdown |
| 4 | **S&OP Misalignment** — Sales, Demand Planning, Production, Procurement running different numbers | Wrong product, wrong time, wrong place — every cycle |
| 5 | **KPI Visibility Gap** — OTIF, fill rates, lead times scattered across a dozen spreadsheets | Leadership makes decisions on stale, conflicting data |

This tool solves all five — under one roof.

---

## ✨ Features

### 📈 Module 1 — Demand Forecast Engine
- Visualizes historical demand with **EMA (Exponential Moving Average) smoothing**
- Generates **forward projections** using linear trend + EMA
- Detects and flags **promotional months** in the dataset
- Calculates **forecast accuracy (MAPE-based)** and **demand volatility %**
- Month-on-month growth chart to surface seasonality
- 🤖 AI analysis: trend direction, seasonality patterns, safety buffer recommendation, stockout/overstock risk for next quarter

### 📦 Module 2 — Inventory Health Monitor
- Automatically classifies every SKU: **Critical / Stockout Risk / Overstock / Healthy**
- Calculates **days of supply** vs lead time for every SKU
- Computes **working capital** and **locked capital** (excess above EOQ + safety stock)
- Stock vs Reorder Point vs Safety Stock vs EOQ grouped bar chart
- Working capital pie chart + days-of-supply color-coded bars
- Full inventory status heatmap
- 🤖 AI analysis: immediate PO actions, overstock reduction plan, working capital freed if right-sized, systemic fix recommendation

### 🏭 Module 3 — Supplier Risk Radar
- Composite supplier score: **Delivery (40%) · Quality (35%) · Cost (25%)**
- Automatic **risk tiering**: Low / Medium / High / Critical
- Flags single-source suppliers and calculates concentration spend exposure
- Bubble chart: Score vs Spend (bubble size = lead time)
- Per-supplier **radar chart** with healthy threshold ring
- Spend share donut by risk tier
- 🤖 AI analysis: $ exposure per supplier failure, PIP targets, dual-sourcing priorities, negotiation leverage, 30-day risk reduction plan

### 🔄 Module 4 — S&OP Alignment Monitor
- Side-by-side comparison: **Sales / Demand Plan / Production Capacity / Procurement**
- Gap analysis: unit and % misalignment per quarter
- Revenue-at-risk estimation at configurable ASP ($45 default)
- Department gap waterfall chart with color-scaled severity
- Cross-department shortfall heatmap
- 🤖 AI analysis: most dangerous quarter, revenue at risk, which department to trust, top 3 S&OP action items, process change to get gap below 5%

### 📊 Module 5 — KPI Command Center
- Tracks 6 core supply chain KPIs: **OTIF · Inventory Turns · Fill Rate · Avg Lead Time · Forecast Accuracy · Supplier OTIF**
- Dark **gauge charts** with target thresholds and colored zones
- Horizontal performance bar chart with on/near/off-target colors
- KPI performance heatmap (% of target)
- 4-point trend sparklines for all KPIs
- 🤖 AI analysis: $ impact per unit of gap, causal chain (root causes vs symptoms), 30/60/90-day action plan, untracked metric recommendation, board-level budget justification

---

## 🚀 Getting Started

### Prerequisites
- Python 3.9+
- A free Groq API key → [console.groq.com](https://console.groq.com) (takes 30 seconds)

### 1. Clone the repo
```bash
git clone https://github.com/your-username/supply-chain-command-center.git
cd supply-chain-command-center
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Run locally
```bash
streamlit run app.py
```

The app opens at `http://localhost:8501`

### 4. Add your Groq API key
Paste your key in the **sidebar → Groq API Key** field. The key is never stored — it only lives in your browser session.

---

## ☁️ Deploy to Streamlit Cloud (Free)

1. Push this repo to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Click **New app** → select your repo → set `app.py` as the main file
4. Click **Deploy** — your shareable URL is live in ~2 minutes

> **Tip:** You can store your Groq key as a Streamlit secret so users don't need to enter it themselves. Add this to your Streamlit Cloud secrets:
> ```toml
> GROQ_API_KEY = "gsk_your_key_here"
> ```
> Then in `app.py`, replace the text input with:
> ```python
> api_key = st.secrets.get("GROQ_API_KEY", "")
> ```

---

## 📂 File Structure

```
supply-chain-command-center/
│
├── app.py                  # Main Streamlit application
├── requirements.txt        # Python dependencies
├── README.md               # This file
│
└── templates/              # (Optional) pre-filled CSV templates
    ├── template_forecast.csv
    ├── template_inventory.csv
    ├── template_supplier.csv
    ├── template_sop.csv
    └── template_kpi.csv
```

> **Note:** CSV templates can be downloaded directly from the app sidebar — no need to store them separately.

---

## 📊 Uploading Your Own Data

Every module supports **CSV** and **Excel (.xlsx)** upload. Use the sidebar toggle to switch between demo data and your own.

### Required column schemas

**📈 Forecast**
```
month | actual_demand | promo_flag
```
- `month`: string label (e.g. "Jan", "Feb")
- `actual_demand`: integer or float; leave blank for future months
- `promo_flag`: 1 if promotional activity that month, else 0

**📦 Inventory**
```
sku | item_name | stock | reorder_point | eoq | safety_stock | daily_demand | lead_time_days | unit_cost
```

**🏭 Supplier**
```
supplier_name | delivery_pct | quality_pct | cost_score | lead_time_days | annual_spend | single_source
```
- `single_source`: 1 if you have no backup supplier, else 0

**🔄 S&OP**
```
department | q1 | q2 | q3 | q4
```
- One row per department (Sales, Demand Plan, Production Capacity, Procurement)

**📊 KPI**
```
kpi_name | current_value | target_value | unit | trend
```
- `trend`: numeric change vs prior period (positive = improving, negative = declining)
- `unit`: `%`, `x`, `days`, etc.

> 💡 Click **"Download CSV Template"** in the sidebar for any module to get a pre-filled file with the correct format.

---

## 🤖 AI Model

All AI insights are powered by **Groq** running `llama-3.3-70b-versatile`.

| Property | Value |
|---|---|
| Provider | Groq |
| Model | `llama-3.3-70b-versatile` |
| Why this model | Best reasoning + longest context on Groq · handles large supply chain data summaries without truncation |
| Latency | ~1–3 seconds per insight (Groq runs at ~1,800 tokens/sec) |
| Cost | Free tier: 100 requests/day · Paid: fraction of a cent per insight |

Each module uses a **domain-specific system prompt** that instructs the model to act as the relevant expert (demand planning analyst, inventory optimization analyst, procurement expert, S&OP planning expert, supply chain VP) and return specific, numbered, data-grounded insights.

---

## 🛠 Tech Stack

| Layer | Technology |
|---|---|
| Frontend / App | [Streamlit](https://streamlit.io) |
| Charts | [Plotly](https://plotly.com/python/) — bar, scatter, pie, gauge, heatmap, radar |
| AI Inference | [Groq](https://groq.com) — `llama-3.3-70b-versatile` |
| Data Processing | Pandas · NumPy |
| File Support | CSV · Excel (openpyxl) |
| Styling | Custom CSS injected via `st.markdown` |

---

## 📸 Module Overview

```
┌─────────────────────────────────────────────────────────────┐
│  ⛓ SUPPLY CHAIN COMMAND CENTER                              │
│─────────────────────────────────────────────────────────────│
│  SIDEBAR                  │  MAIN PANEL                     │
│  ─────────                │  ──────────────────────────     │
│  🔑 Groq API Key          │  Module Banner (problem solved) │
│  🧭 Module Selector       │  Metrics Row (4 KPIs)           │
│  📂 Data Source Toggle    │  Alerts (critical / warning)    │
│     ├ Use Demo Dataset    │  Charts (2–4 Plotly charts)     │
│     └ Upload My Data      │  AI Insight Box (Groq output)   │
│  ⬇ Download CSV Template  │                                 │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔮 Roadmap / Possible Extensions

- [ ] Multi-period historical KPI tracking (not just current vs target)
- [ ] Automated email/Slack alerts for critical inventory or supplier events
- [ ] Monte Carlo demand simulation for advanced scenario planning
- [ ] Supplier contract expiry tracking
- [ ] Integration with ERP exports (SAP, Oracle, NetSuite CSV formats)
- [ ] PDF report export per module
- [ ] User authentication for team-shared deployments

---

## 🤝 Contributing

Pull requests are welcome. For major changes, open an issue first to discuss what you'd like to change.

---

## 📄 License

MIT License — free to use, modify, and deploy.

---

## 👤 Author

Built by a supply chain analyst, for supply chain analysts.  
Tired of switching between Excel, Power BI, a supplier tracker, an S&OP deck, and a KPI dashboard just to answer one question.

> The best supply chain tool is the one where everything lives in one place.

