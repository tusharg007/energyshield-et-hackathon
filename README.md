# EnergyShield 🛡️
### AI-Driven Energy Supply Chain Resilience for Import-Dependent Economies

> Built for ET AI Hackathon 2.0 — Problem Statement #2
> by Tushar Ghosh, IIIT Nagpur (B.Tech CSE — Data Science & Analytics)

---

## 🔴 The Problem

India imports 88% of its crude oil. 40-45% of that volume
transits the Strait of Hormuz — a single chokepoint whose
closure would drain India's Strategic Petroleum Reserve
in under 10 days. The 2025 US-Iran standoff sent Brent
crude up 8% in a single trading session. India had no
automated intelligence layer to respond.

Traditional supply chain tools cannot:
- Model geopolitical disruption scenarios in real time
- Dynamically rank alternative procurement corridors
- Explain their recommendations to decision-makers

**EnergyShield is that missing intelligence layer.**

---

## 🧠 What It Does

A single button press runs three LangGraph agents in sequence:

### Agent 1 — Geopolitical Risk Agent
Ingests geopolitical signals (sanctions, naval activity,
weather, piracy) and updates live risk scores for 5
major oil import corridors. Powered by Groq LLaMA-3.3-70B,
each corridor gets a plain-English reasoning trace
explaining exactly why its risk score changed.

### Agent 2 — Hormuz Scenario Modeller  
Given a closure percentage (10-90%), computes cascading
impacts deterministically using real India energy figures:
- Import gap (MBD)
- Brent crude price spike
- Refinery stress score
- SPR days remaining
- GDP drag estimate
- Unmet gap after maximum rerouting

All assumptions are explicit and testable — no black box.

### Agent 3 — Procurement Orchestrator
Filters out disrupted (Hormuz) suppliers, then ranks
all available alternatives on a 4-dimension composite score:

| Dimension | Weight | Logic |
|-----------|--------|-------|
| Price | 25% | Lower $/bbl = higher score |
| Lead Time | 25% | Shorter days = higher score |
| Grade Compatibility | 30% | Refinery match % |
| Corridor Safety | 20% | 1 - current_risk_score |

Top 3 suppliers get a per-supplier LLM reasoning trace
explaining the ranking decision with specific numbers.

---

## 🏗️ Architecture

```text
Geopolitical Signals (mock → real API-ready)
                         │
                         ▼
┌────────────────────────────────────────────────────────────┐
│ Geopolitical Risk Agent                                    │
│ LangGraph 4-node graph · Groq LLaMA-3.3-70B               │
└────────────────────────────┬───────────────────────────────┘
                             │ corridor risk scores
                             ▼
┌────────────────────────────────────────────────────────────┐
│ SQLite Database · SQLAlchemy ORM                           │
│ corridors · suppliers · signals · scenarios · recs         │
└────────────────────────────┬───────────────────────────────┘
                             │
                             ▼
┌────────────────────────────────────────────────────────────┐
│ Hormuz Scenario Agent                                      │
│ LangGraph 4-node graph · deterministic model · Groq brief  │
└────────────────────────────┬───────────────────────────────┘
                             │ import_gap_mbd
                             ▼
┌────────────────────────────────────────────────────────────┐
│ Procurement Orchestrator                                   │
│ LangGraph 5-node graph · composite scorer · Groq rationale │
└────────────────────────────┬───────────────────────────────┘
                             │
                             ▼
┌────────────────────────────────────────────────────────────┐
│ FastAPI REST Layer                                         │
│ POST /api/agents/full-pipeline/run                         │
└────────────────────────────┬───────────────────────────────┘
                             │
                             ▼
┌────────────────────────────────────────────────────────────┐
│ React Dashboard · Vite · Tailwind · Recharts               │
│ Risk · Scenario · Procurement · Agent Reasoning Traces     │
└────────────────────────────────────────────────────────────┘
```

---

## 🌐 Live Demo

- **Frontend:** https://energyshield-frontend.onrender.com
- **Backend API:** https://energyshield-backend.onrender.com
- **API Docs:** https://energyshield-backend.onrender.com/docs
- **Health Check:** https://energyshield-backend.onrender.com/api/health
- **GitHub:** https://github.com/tusharg007/energyshield-et-hackathon

---

## 🚀 Quick Start (Local)

### Prerequisites
- Python 3.11+
- Node.js 18+
- Groq API key (free at console.groq.com)

### Backend
```bash
cd backend
pip install -r requirements.txt
cp .env.example .env
# Add your GROQ_API_KEY to .env
python seed.py
uvicorn main:app --reload
# Backend: http://localhost:8000
# API docs: http://localhost:8000/docs
```

### Frontend
```bash
cd frontend
npm install
npm run dev
# Dashboard: http://localhost:5173
```

### Run the Pipeline
1. Open http://localhost:5173
2. Set Hormuz closure level (try 40%)
3. Click "Run Full Intelligence Pipeline"
4. Watch 3 agents execute in sequence
5. Read the reasoning traces

---

## 📡 API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/health | DB status + table counts |
| GET | /api/corridors | All corridor risk scores |
| GET | /api/signals | All geopolitical signals |
| POST | /api/agents/risk/run | Run Risk Agent only |
| POST | /api/agents/scenario/run | Run Scenario Agent only |
| POST | /api/agents/procurement/run | Run Procurement Agent only |
| POST | /api/agents/full-pipeline/run | **Hero endpoint — all 3 agents** |
| GET | /api/scenarios/compare | Multi-closure comparison |
| GET | /api/procurement/recommendations | Saved recommendations |

### Hero Endpoint Example
```bash
curl -X POST http://localhost:8000/api/agents/full-pipeline/run \
  -H "Content-Type: application/json" \
  -d '{"closure_percentage": 0.40, "scenario_name": "Hormuz 40% Closure"}'
```

Returns:
```json
{
  "risk_assessments": [...],     // 5 corridors with reasoning
  "scenario": {...},             // 6 impact metrics + narrative  
  "procurement_recommendations": [...]  // ranked suppliers + rationale
}
```

---

## 🗄️ Database Schema

| Table | Purpose |
|-------|---------|
| corridor_risks | 5 corridors with live risk scores |
| suppliers | 8 suppliers with grade/price/lead time |
| geopolitical_signals | Mock signal feed (10 signals) |
| scenario_results | Saved Hormuz closure computations |
| procurement_recommendations | Ranked supplier outputs |

---

## 🧱 Tech Stack

| Layer | Technology | Version |
|-------|-----------|---------|
| Agent Orchestration | LangGraph | 1.2.9 |
| LLM | Groq — LLaMA-3.3-70B-Versatile | Latest |
| Backend Framework | FastAPI | 0.139.0 |
| ORM | SQLAlchemy | 2.0.51 |
| Database | SQLite | — |
| Frontend | React + Vite | 18 + 8.x |
| Styling | Tailwind CSS | 4.x |
| Charts | Recharts | Latest |
| Deployment | Render | — |

---

## 🌍 Data Strategy

| Data Type | Current | Production-Ready Swap |
|-----------|---------|----------------------|
| Geopolitical signals | Simulated (realistic) | NewsAPI, GDELT |
| AIS vessel tracking | Implicit in signals | MarineTraffic API |
| Sanctions data | Signal headlines | OFAC registry feed |
| Brent price | Hardcoded $74 baseline | EIA / Bloomberg API |
| Supplier prices | Realistic seed data | Argus, Platts feeds |

All simulated data is schema-compatible with real feeds.
Switching to live data = changing one data ingestion function.

---

## 📊 Domain Constants Used

```python
INDIA_CRUDE_IMPORT_MBD = 4.5      # Million barrels/day
HORMUZ_SHARE = 0.42                # 42% of imports via Hormuz  
SPR_TOTAL_DAYS = 9.5               # Strategic reserve cover
BRENT_BASE_PRICE_USD = 74.0        # Baseline (July 2026)
INDIA_GDP_USD_T = 3.9              # Trillion USD
OIL_GDP_SENSITIVITY = 0.6          # % GDP per 10% oil price rise
```

All figures sourced from public data:
MoPNG, IEA, McKinsey Energy Practice, PPAC India.

---

## 🔮 Future Scope

- Live AIS vessel tracking integration (MarineTraffic API)
- Real-time news ingestion (GDELT + NewsAPI)
- Multi-country extension (Bangladesh, Sri Lanka, Pakistan)
- SPR drawdown optimizer agent
- WebSocket live updates (replace polling)
- Mobile-responsive dashboard

---

## 📁 Project Structure

```text
energyshield/
├── backend/
│   ├── main.py                 # FastAPI app + all endpoints
│   ├── database.py             # SQLAlchemy engine + session
│   ├── models.py               # ORM models (5 tables)
│   ├── schemas.py              # Pydantic schemas
│   ├── seed.py                 # DB initialization + seed data
│   ├── agents/
│   │   ├── risk_agent.py       # Geopolitical Risk Agent
│   │   ├── scenario_agent.py   # Hormuz Scenario Modeller
│   │   └── procurement_agent.py # Procurement Orchestrator
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── App.jsx             # Main app + state management
│   │   ├── config.js           # API base URL config
│   │   └── components/
│   │       ├── Header.jsx
│   │       ├── ControlPanel.jsx
│   │       ├── RiskCorridorPanel.jsx
│   │       ├── ScenarioPanel.jsx
│   │       ├── ProcurementTable.jsx
│   │       └── ReasoningTrace.jsx
│   ├── package.json
│   └── vite.config.js
├── render.yaml                 # Render deployment config
├── SUBMISSION.md               # Hackathon submission document
└── README.md                   # This file
```

---

## 👤 Author

**Tushar Ghosh**
B.Tech CSE (Data Science & Analytics) — IIIT Nagpur
GitHub: github.com/tusharg007

*Built for ET AI Hackathon 2.0 — Economic Times*
*Problem Statement #2: AI-Driven Energy Supply Chain Resilience*
